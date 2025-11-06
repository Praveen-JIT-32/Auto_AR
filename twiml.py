
import re
import logging
import json
import asyncio
import boto3
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("twilio-voice-agent")

# AWS Clients with connection pooling
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
polly = boto3.client("polly", region_name="ap-south-1")

app = FastAPI()

# Store conversation context with TTL
conversations = {}



async def get_ai_response(user_input: str, conversation_id: str) -> str:
    """Optimized AI response with latency improvements"""
    start_time = time.time()
    
    try:
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        history = conversations[conversation_id]
        
        # LATENCY OPTIMIZATION: Limit history to last 2 exchanges
        recent_history = history[-4:]  # Only last 2 user+assistant pairs
        
        # LATENCY OPTIMIZATION: Build optimized prompt
        prompt_parts = []
        
        # Add system prompt
        prompt_parts.append("System: You are a helpful AI assistant for JIT Global. Keep responses under 15 words.")
        
        # Add recent history
        for msg in recent_history:
            if msg["role"] == "user":
                prompt_parts.append(f"Human: {msg['content']}")
            else:
                prompt_parts.append(f"Assistant: {msg['content']}")
        
        # Add current input
        prompt_parts.append(f"Human: {user_input}")
        prompt_parts.append("Assistant:")
        
        prompt = "\n".join(prompt_parts)
        
        # LATENCY OPTIMIZATION: Reduced token count and faster parameters
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 60,  # Reduced from 100
                    "temperature": 0.3,   # Lower for faster, more consistent responses
                    "topP": 0.8           # Slightly lower for speed
                }
            })
        )
        
        result = json.loads(response["body"].read())
        ai_response = result["results"][0]["outputText"].strip()
        
        # 🔥 COMPREHENSIVE RESPONSE CLEANING
        # 1. Remove any "Assistant:" prefix
        ai_response = re.sub(r'^Assistant:\s*', '', ai_response, flags=re.IGNORECASE)
        
        # 2. Split at the first "Human:" occurrence and take only the first part
        if "Human:" in ai_response:
            ai_response = ai_response.split("Human:")[0].strip()
        
        # 3. Also check for "System:" as a stopping point
        if "System:" in ai_response:
            ai_response = ai_response.split("System:")[0].strip()
        
        # 4. Remove any extra whitespace
        ai_response = ai_response.strip()
        
        # 5. Ensure we have a valid response
        if not ai_response or len(ai_response) < 2:
            ai_response = "How can I assist you?"
        
        # Update conversation history
        history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ])
        
        # LATENCY OPTIMIZATION: Keep only last 6 messages (reduced from 10)
        if len(history) > 6:
            conversations[conversation_id] = history[-6:]
        
        latency = time.time() - start_time
        logger.info(f"🤖 AI Response ({latency:.2f}s): {ai_response}")
        return ai_response
        
    except Exception as e:
        latency = time.time() - start_time
        logger.error(f"AI error ({latency:.2f}s): {e}")
        return "Please repeat that."

@app.post("/voice")
async def handle_incoming_call(request: Request):
    """Optimized voice endpoint"""
    logger.info("📞 Incoming call received")
    
    response = VoiceResponse()
    
    # LATENCY OPTIMIZATION: Shorter greeting
    response.say(
        "Hello! How can I help you today?",
        voice="salli",
        language="en-US"
    )
    
    # LATENCY OPTIMIZATION: Faster timeouts
    gather = Gather(
        input='speech',
        action='/process_speech',
        method='POST',
        speechTimeout=2,  # Reduced from 3 seconds
        timeout=4,        # Reduced from 5 seconds
        language='en-US',
        enhanced=True
    )
    response.append(gather)
    
    response.redirect('/voice')
    return Response(content=str(response), media_type="application/xml")

@app.post("/process_speech")
async def process_speech(
    request: Request,
    SpeechResult: str = Form(None),
    CallSid: str = Form(...),
    Confidence: str = Form("0.0")
):
    """Optimized speech processing"""
    start_time = time.time()
    
    logger.info(f"🎤 Speech received: {SpeechResult}")
    
    response = VoiceResponse()
    
    # LATENCY OPTIMIZATION: Faster confidence check
    confidence = float(Confidence) if Confidence else 0.0
    if confidence < 0.5:  # Slightly lower threshold
        response.say("Could you repeat that?", voice="salli")
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,
            timeout=4
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")
    
    if not SpeechResult or SpeechResult.strip() == "":
        response.say("I didn't hear that. Please speak clearly.", voice="salli")
        response.redirect('/voice')
        return Response(content=str(response), media_type="application/xml")
    
    try:
        # Get AI response
        ai_response = await get_ai_response(SpeechResult, CallSid)
        
        # Speak the response
        response.say(ai_response, voice="salli", language="en-US")
        
        # LATENCY OPTIMIZATION: Shorter continuation prompt
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,  # Reduced
            timeout=6,        # Reduced
            language='en-US',
            enhanced=True
        )
        gather.say('How can I help?', voice='salli')  # Shorter prompt
        response.append(gather)
        
        response.say("Thank you. Goodbye!", voice="salli")
        response.hangup()
        
        total_time = time.time() - start_time
        logger.info(f"⚡ Total processing time: {total_time:.2f}s")
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Processing error ({total_time:.2f}s): {e}")
        response.say("Please try again.", voice="salli")
        
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,
            timeout=4
        )
        response.append(gather)
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/call_status")
async def handle_call_status(request: Request):
    """Clean up ended calls to prevent memory leaks"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    
    if call_status in ["completed", "failed", "busy", "no-answer"]:
        conversations.pop(call_sid, None)
        logger.info(f"🧹 Cleaned up conversation for: {call_sid}")
    
    return Response(content="OK")

@app.get("/health")
async def health_check():
    return {
        "status": "running", 
        "service": "JIT Global Twilio Voice AI",
        "active_conversations": len(conversations)
    }

@app.get("/")
async def root():
    return {"status": "running", "service": "JIT Global Twilio Voice AI"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Optimized Twilio Voice AI Agent...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        access_log=False  # Disable access logs for better performance
    )