# import re
# import logging
# import json
# import asyncio
# import boto3
# from fastapi import FastAPI, Request, Form
# from fastapi.responses import Response
# from twilio.twiml.voice_response import VoiceResponse, Gather
# import time
# from datetime import datetime
# from typing import Dict, Optional

# # Setup comprehensive logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s | %(levelname)s | %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)

# # AWS Clients with connection pooling
# bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
# polly = boto3.client("polly", region_name="ap-south-1")

# app = FastAPI()

# # Store conversation context with TTL
# conversations = {}
# call_metadata = {}

# # ============================================
# # SINGLE CUSTOMER FOR TESTING
# # ============================================
# CUSTOMER_INFO = {
#     "customer_id": "CUST001",
#     "name": "Praveen Kumar",
#     "phone_number": "+916385740104",
#     "due_amount": 5000.00,
#     "due_date": "2024-10-15",
#     "days_overdue": 22,
#     "invoice_number": "INV-2024-1015",
#     "last_contact": "2024-10-28"
# }


# def get_customer_info(phone_number: str) -> Dict:
#     """Return the single customer info for any call"""
#     logger.info(f"🔍 Call from: {phone_number}")
#     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']} (ID: {CUSTOMER_INFO['customer_id']})")
#     return CUSTOMER_INFO


# def build_system_prompt(customer: Dict) -> str:
#     """Build comprehensive debt collection prompt"""
#     prompt = f"""You are Arjun, a professional debt collection agent from JIT Global Financial Services.

# CUSTOMER DETAILS:
# - Name: {customer['name']}
# - Customer ID: {customer['customer_id']}
# - Outstanding Amount: ₹{customer['due_amount']:,.2f}
# - Original Due Date: {customer['due_date']}
# - Days Overdue: {customer['days_overdue']} days
# - Invoice Number: {customer['invoice_number']}

# YOUR ROLE:
# You are calling to collect the overdue payment. Be professional, empathetic but firm.

# CONVERSATION FLOW:
# 1. If customer says "Hello/Hi": Acknowledge and state purpose
# 2. Ask about non-payment reason
# 3. Listen and respond with empathy
# 4. Negotiate payment (full, installment, or hardship plan)
# 5. Get specific commitment with date and amount
# 6. Confirm and close

# RULES:
# - Keep responses under 40 words
# - Be conversational and natural
# - Don't repeat information
# - Always push for commitment
# - Stay professional

# Respond naturally to what the customer just said."""
    
#     return prompt


# async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
#     """Enhanced AI response for debt collection with FIXED Bedrock API call"""
#     start_time = time.time()
#     log_prefix = f"[{conversation_id[:8]}]"
    
#     logger.info(f"{log_prefix} ⚙️  Starting AI response generation")
#     logger.info(f"{log_prefix} 📝 User input: '{user_input}'")
    
#     try:
#         # Get or create conversation history
#         if conversation_id not in conversations:
#             logger.info(f"{log_prefix} 🆕 Creating new conversation history")
#             conversations[conversation_id] = []
        
#         history = conversations[conversation_id]
#         logger.info(f"{log_prefix} 📚 Conversation history length: {len(history)} messages")
        
#         # Limit history to last 6 messages (3 exchanges)
#         recent_history = history[-6:]
        
#         # Build optimized prompt
#         prompt_parts = []
        
#         # Add system context
#         system_prompt = build_system_prompt(customer_info)
#         prompt_parts.append(system_prompt)
#         logger.info(f"{log_prefix} 📋 System prompt built")
        
#         # Add recent history
#         for msg in recent_history:
#             if msg["role"] == "user":
#                 prompt_parts.append(f"\nCustomer: {msg['content']}")
#             else:
#                 prompt_parts.append(f"\nAgent: {msg['content']}")
        
#         # Add current input
#         prompt_parts.append(f"\nCustomer: {user_input}")
#         prompt_parts.append("\nAgent:")
        
#         full_prompt = "".join(prompt_parts)
#         logger.info(f"{log_prefix} 📦 Prompt size: {len(full_prompt)} chars")
        
#         # FIXED: Call Bedrock with CORRECT format for Titan
#         bedrock_start = time.time()
#         logger.info(f"{log_prefix} 🚀 Calling Bedrock API...")
        
#         # THIS IS THE FIX - Proper Titan Text Lite format
#         request_body = {
#             "inputText": full_prompt,
#             "textGenerationConfig": {
#                 "maxTokenCount": 120,
#                 "temperature": 0.7,
#                 "topP": 0.9
#             }
#         }
        
#         logger.info(f"{log_prefix} 📤 Request body prepared")
        
#         response = bedrock.invoke_model(
#             modelId="amazon.titan-text-lite-v1",
#             body=json.dumps(request_body),
#             contentType="application/json",
#             accept="application/json"
#         )
        
#         bedrock_latency = time.time() - bedrock_start
#         logger.info(f"{log_prefix} ✅ Bedrock API call completed in {bedrock_latency:.3f}s")
        
#         # Parse response
#         response_body = json.loads(response["body"].read())
#         ai_response = response_body["results"][0]["outputText"].strip()
#         logger.info(f"{log_prefix} 📤 Raw AI response: '{ai_response}'")
        
#         # Clean response - remove any role prefixes
#         ai_response = re.sub(r'^(Agent|Assistant|Arjun):\s*', '', ai_response, flags=re.IGNORECASE)
        
#         # Remove any customer/system text that leaked through
#         if "Customer:" in ai_response:
#             ai_response = ai_response.split("Customer:")[0].strip()
#         if "\n" in ai_response:
#             ai_response = ai_response.split("\n")[0].strip()
        
#         ai_response = ai_response.strip()
        
#         # Ensure valid response
#         if not ai_response or len(ai_response) < 5:
#             ai_response = f"Yes, I'm calling about your overdue payment of ₹{customer_info['due_amount']:,.2f}. When can you make this payment?"
#             logger.warning(f"{log_prefix} ⚠️  Empty response, using fallback")
        
#         logger.info(f"{log_prefix} 💬 Final response: '{ai_response}'")
        
#         # Update conversation history
#         history.extend([
#             {"role": "user", "content": user_input},
#             {"role": "assistant", "content": ai_response}
#         ])
        
#         # Keep only last 10 messages
#         if len(history) > 10:
#             conversations[conversation_id] = history[-10:]
        
#         total_latency = time.time() - start_time
#         logger.info(f"{log_prefix} ⏱️  Total AI processing: {total_latency:.3f}s")
        
#         return ai_response
        
#     except Exception as e:
#         total_latency = time.time() - start_time
#         logger.error(f"{log_prefix} ❌ AI Error after {total_latency:.3f}s: {str(e)}", exc_info=True)
#         return f"Let me verify your account. Your customer ID is {customer_info['customer_id']}. Can you confirm your name?"


# @app.post("/voice")
# async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
#     """Handle incoming call with customer lookup"""
#     call_start = time.time()
#     logger.info("=" * 80)
#     logger.info(f"📞 INCOMING CALL RECEIVED")
#     logger.info(f"📞 Call SID: {CallSid}")
#     logger.info(f"📞 From Number: {From}")
#     logger.info("=" * 80)
    
#     response = VoiceResponse()
    
#     try:
#         # Lookup customer information
#         customer_info = get_customer_info(From)
        
#         # Store call metadata
#         call_metadata[CallSid] = {
#             "customer_info": customer_info,
#             "call_start": datetime.now().isoformat(),
#             "phone_number": From
#         }
#         logger.info(f"💾 Call metadata stored for {CallSid}")
        
#         # Initial greeting with customer name
#         greeting = f"Hello, am I speaking with {customer_info['name']}? This is Arjun from JIT Global Financial Services."
#         logger.info(f"👋 Greeting: '{greeting}'")
        
#         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
#         # Gather response
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=3,
#             timeout=7,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
        
#         response.redirect('/voice')
        
#         total_latency = time.time() - call_start
#         logger.info(f"⏱️  Total /voice processing: {total_latency:.3f}s")
        
#     except Exception as e:
#         logger.error(f"❌ Error in /voice: {str(e)}", exc_info=True)
#         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/process_speech")
# async def process_speech(
#     request: Request,
#     SpeechResult: str = Form(None),
#     CallSid: str = Form(...),
#     Confidence: str = Form("0.0")
# ):
#     """Process speech with enhanced logging"""
#     processing_start = time.time()
#     log_prefix = f"[{CallSid[:8]}]"
    
#     logger.info("=" * 80)
#     logger.info(f"{log_prefix} 🎤 SPEECH INPUT")
#     logger.info(f"{log_prefix} Text: '{SpeechResult}'")
#     logger.info(f"{log_prefix} Confidence: {Confidence}")
#     logger.info("=" * 80)
    
#     response = VoiceResponse()
    
#     # Confidence check
#     confidence = float(Confidence) if Confidence else 0.0
    
#     if confidence < 0.5:
#         logger.warning(f"{log_prefix} ⚠️  Low confidence ({confidence:.2f})")
#         response.say("Sorry, I didn't catch that. Could you repeat?", voice="Polly.Joanna")
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=3,
#             timeout=7,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
#         return Response(content=str(response), media_type="application/xml")
    
#     if not SpeechResult or SpeechResult.strip() == "":
#         logger.warning(f"{log_prefix} ⚠️  Empty speech")
#         response.say("I didn't hear anything.", voice="Polly.Joanna")
#         response.redirect('/voice')
#         return Response(content=str(response), media_type="application/xml")
    
#     try:
#         # Get customer info
#         if CallSid not in call_metadata:
#             logger.error(f"{log_prefix} ❌ No metadata")
#             response.say("Session error. Please call again.", voice="Polly.Joanna")
#             response.hangup()
#             return Response(content=str(response), media_type="application/xml")
        
#         customer_info = call_metadata[CallSid]["customer_info"]
#         logger.info(f"{log_prefix} 👤 Customer: {customer_info['name']}")
        
#         # Get AI response
#         ai_start = time.time()
#         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
#         ai_latency = time.time() - ai_start
#         logger.info(f"{log_prefix} ✅ AI done in {ai_latency:.3f}s")
        
#         # Respond
#         response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
#         # Continue conversation
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=3,
#             timeout=7,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
        
#         # Timeout fallback
#         response.say("Are you still there?", voice="Polly.Joanna")
#         response.redirect('/process_speech')
        
#         total_latency = time.time() - processing_start
#         logger.info(f"{log_prefix} ⏱️  Total: {total_latency:.3f}s")
        
#     except Exception as e:
#         logger.error(f"{log_prefix} ❌ Error: {str(e)}", exc_info=True)
#         response.say("I'm having trouble. Let me transfer you.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/call_status")
# async def handle_call_status(request: Request):
#     """Handle call status updates"""
#     form_data = await request.form()
#     call_sid = form_data.get("CallSid")
#     call_status = form_data.get("CallStatus")
#     call_duration = form_data.get("CallDuration", "0")
    
#     log_prefix = f"[{call_sid[:8]}]"
#     logger.info("=" * 80)
#     logger.info(f"{log_prefix} 📊 CALL STATUS: {call_status}")
#     logger.info(f"{log_prefix} Duration: {call_duration}s")
    
#     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
#         if call_sid in conversations:
#             msg_count = len(conversations[call_sid])
#             logger.info(f"{log_prefix} 💬 Messages: {msg_count}")
            
#         conversations.pop(call_sid, None)
#         metadata = call_metadata.pop(call_sid, None)
        
#         if metadata:
#             customer_info = metadata.get("customer_info", {})
#             logger.info(f"{log_prefix} 👤 {customer_info.get('name', 'Unknown')}")
        
#         logger.info(f"{log_prefix} 🧹 Cleaned up")
    
#     logger.info("=" * 80)
#     return Response(content="OK")


# @app.get("/health")
# async def health_check():
#     """Health check"""
#     return {
#         "status": "running",
#         "service": "JIT Global Debt Collection Agent",
#         "active_calls": len(conversations),
#         "timestamp": datetime.now().isoformat()
#     }


# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "status": "running",
#         "service": "JIT Global Debt Collection Agent",
#         "version": "2.1-FIXED",
#         "endpoints": {
#             "/voice": "Incoming call handler",
#             "/process_speech": "Speech processing",
#             "/health": "Health check"
#         }
#     }


# @app.get("/customers")
# async def list_customers():
#     """Show customer info"""
#     return {
#         "customer": CUSTOMER_INFO,
#         "note": "This customer info is used for all calls"
#     }


# if __name__ == "__main__":
#     import uvicorn
#     logger.info("🚀" * 40)
#     logger.info("🚀 JIT GLOBAL DEBT COLLECTION AGENT")
#     logger.info(f"🚀 Customer: {CUSTOMER_INFO['name']}")
#     logger.info(f"🚀 Due Amount: ₹{CUSTOMER_INFO['due_amount']:,.2f}")
#     logger.info(f"🚀 Days Overdue: {CUSTOMER_INFO['days_overdue']}")
#     logger.info(f"🚀 Bedrock: Amazon Titan Text Lite v1")
#     logger.info(f"🚀 TTS: Twilio Polly (Joanna)")
#     logger.info(f"🚀 Port: 8000")
#     logger.info("🚀" * 40)
    
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")




# import re
# import logging
# import json
# import asyncio
# import boto3
# from fastapi import FastAPI, Request, Form
# from fastapi.responses import Response
# from twilio.twiml.voice_response import VoiceResponse, Gather
# import time
# from datetime import datetime
# from typing import Dict, Optional

# # Setup comprehensive logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s | %(levelname)s | %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)

# # AWS Configuration
# REGION = "us-east-1"

# # AWS Clients
# bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# polly = boto3.client("polly", region_name=REGION)

# app = FastAPI()

# # Store conversation context
# conversations = {}
# call_metadata = {}

# # ============================================
# # SINGLE CUSTOMER FOR TESTING
# # ============================================
# CUSTOMER_INFO = {
#     "customer_id": "CUST001",
#     "name": "Praveen Kumar",
#     "phone_number": "+916385740104",
#     "due_amount": 5000.00,
#     "due_date": "2024-10-15",
#     "days_overdue": 22,
#     "invoice_number": "INV-2024-1015",
#     "last_contact": "2024-10-28"
# }


# def get_customer_info(phone_number: str) -> Dict:
#     """Return the single customer info for any call"""
#     logger.info(f"🔍 Call from: {phone_number}")
#     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']} (ID: {CUSTOMER_INFO['customer_id']})")
#     return CUSTOMER_INFO


# def build_system_prompt(customer: Dict) -> str:
#     """Build debt collection prompt for Nova Pro with dynamic info usage"""
#     prompt = f"""
# You are Arjun, a professional debt collection agent from JIT Global Financial Services.

# CUSTOMER DETAILS:
# - Name: {customer['name']}
# - Customer ID: {customer['customer_id']}
# - Outstanding Amount: ₹{customer['due_amount']:,.2f}
# - Original Due Date: {customer['due_date']}
# - Days Overdue: {customer['days_overdue']} days
# - Invoice Number: {customer['invoice_number']}
# - Last Contact: {customer['last_contact']}

# YOUR ROLE:
# You are calling to collect the overdue payment. Be professional, empathetic, but firm.
# You are authorized to share payment details with the verified customer.

# IMPORTANT INSTRUCTIONS:
# - You may **freely mention or confirm** the payment amount (₹{customer['due_amount']:,.2f}), invoice number ({customer['invoice_number']}), due date ({customer['due_date']}), and customer ID ({customer['customer_id']}).
# - If the customer asks “how much should I pay?”, “what is the amount?”, or “what’s the balance?”, clearly state:
#   👉 “You have an overdue balance of ₹{customer['due_amount']:,.2f} from invoice {customer['invoice_number']} that was due on {customer['due_date']}.”
# - Be polite and conversational.
# - If the customer argues or hesitates, remind them gently about the due date and request a payment commitment.

# CONVERSATION STYLE:
# - Short, natural voice responses (under 40 words)
# - No repetition
# - Empathetic tone
# - Keep flow realistic for phone dialogue
# - Always close by confirming payment plan or follow-up date

# Now respond to what the customer just said.
# """
#     return prompt



# async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
#     """Get AI response using Amazon Nova Pro (corrected format)"""
#     start_time = time.time()
#     log_prefix = f"[{conversation_id[:8]}]"
    
#     logger.info(f"{log_prefix} ⚙️ Starting Nova Pro AI response")
#     logger.info(f"{log_prefix} 📝 User input: '{user_input}'")
    
#     try:
#         # Create or load chat history
#         if conversation_id not in conversations:
#             logger.info(f"{log_prefix} 🆕 Creating new conversation context")
#             conversations[conversation_id] = []

#         history = conversations[conversation_id]

#         # Build conversation context
#         system_prompt = build_system_prompt(customer_info)

#         messages = []

#         # Add last few exchanges
#         for msg in history[-6:]:
#             messages.append({
#                 "role": msg["role"],
#                 "content": [{"text": msg["content"]}]
#             })

#         # Add system context and new message
#         if not messages:
#             current_text = f"{system_prompt}\n\nCustomer says: {user_input}\n\nAgent responds:"
#         else:
#             current_text = user_input

#         messages.append({
#             "role": "user",
#             "content": [{"text": current_text}]
#         })

#         logger.info(f"{log_prefix} 📦 Prepared {len(messages)} messages for Nova Pro")

#         # ✅ Corrected body format (no 'type' key or inferenceConfig)
#         request_body = {
#             "messages": messages
#         }

#         logger.info(f"{log_prefix} 🚀 Sending request to Amazon Nova Pro...")

#         nova_start = time.time()
#         response = bedrock.invoke_model(
#             modelId="amazon.nova-pro-v1:0",  # ✅ Correct model ID
#             body=json.dumps(request_body),
#             contentType="application/json",
#             accept="application/json"
#         )
#         nova_latency = time.time() - nova_start
#         logger.info(f"{log_prefix} ✅ Nova Pro responded in {nova_latency:.3f}s")

#         # Parse model response
#         response_body = json.loads(response["body"].read())
#         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()

#         # Clean output
#         ai_response = re.sub(r'^(Agent|Assistant|Arjun):\s*', '', ai_response, flags=re.IGNORECASE)
#         ai_response = ai_response.split("Customer:")[0].split("System:")[0].strip()
#         ai_response = re.sub(r'\s+', ' ', ai_response).replace("\n", " ")

#         if not ai_response or len(ai_response) < 5:
#             ai_response = f"Yes, I'm calling about your overdue payment of ₹{customer_info['due_amount']:,.2f}. When can you make this payment?"
#             logger.warning(f"{log_prefix} ⚠️ Empty response, using fallback")

#         # Save chat history
#         history.extend([
#             {"role": "user", "content": user_input},
#             {"role": "assistant", "content": ai_response}
#         ])
#         if len(history) > 10:
#             conversations[conversation_id] = history[-10:]

#         total_latency = time.time() - start_time
#         logger.info(f"{log_prefix} ⏱️ Total AI latency: {total_latency:.3f}s (Nova: {nova_latency:.3f}s)")
#         logger.info(f"{log_prefix} 💬 Final AI response: '{ai_response}'")

#         return ai_response

#     except Exception as e:
#         total_latency = time.time() - start_time
#         logger.error(f"{log_prefix} ❌ Nova Pro error after {total_latency:.3f}s: {str(e)}", exc_info=True)
#         return f"I'm sorry, could you please repeat that?"



# @app.post("/voice")
# async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
#     """Handle incoming call"""
#     call_start = time.time()
#     logger.info("=" * 80)
#     logger.info(f"📞 INCOMING CALL RECEIVED")
#     logger.info(f"📞 Call SID: {CallSid}")
#     logger.info(f"📞 From Number: {From}")
#     logger.info("=" * 80)
    
#     response = VoiceResponse()
    
#     try:
#         # Lookup customer information
#         customer_info = get_customer_info(From)
        
#         # Store call metadata
#         call_metadata[CallSid] = {
#             "customer_info": customer_info,
#             "call_start": datetime.now().isoformat(),
#             "phone_number": From,
#             "interaction_count": 0
#         }
#         logger.info(f"💾 Call metadata stored for {CallSid}")
        
#         # Initial greeting with customer name
#         greeting = f"Hello, am I speaking with {customer_info['name']}? This is Arjun from JIT Global Financial Services."
#         logger.info(f"👋 Greeting: '{greeting}'")
        
#         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
#         # Gather response with optimized timeouts
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=2,
#             timeout=5,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
        
#         response.redirect('/voice')
        
#         total_latency = time.time() - call_start
#         logger.info(f"⏱️  Total /voice processing: {total_latency:.3f}s")
        
#     except Exception as e:
#         error_latency = time.time() - call_start
#         logger.error(f"❌ Error in /voice after {error_latency:.3f}s: {str(e)}", exc_info=True)
#         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/process_speech")
# async def process_speech(
#     request: Request,
#     SpeechResult: str = Form(None),
#     CallSid: str = Form(...),
#     Confidence: str = Form("0.0")
# ):
#     """Process speech with enhanced logging"""
#     processing_start = time.time()
#     log_prefix = f"[{CallSid[:8]}]"
    
#     logger.info("=" * 80)
#     logger.info(f"{log_prefix} 🎤 SPEECH INPUT")
#     logger.info(f"{log_prefix} Text: '{SpeechResult}'")
#     logger.info(f"{log_prefix} Confidence: {Confidence}")
#     logger.info("=" * 80)
    
#     response = VoiceResponse()
    
#     # Confidence check
#     confidence = float(Confidence) if Confidence else 0.0
#     logger.info(f"{log_prefix} 📊 Confidence score: {confidence:.2f}")
    
#     if confidence < 0.5:
#         logger.warning(f"{log_prefix} ⚠️  Low confidence ({confidence:.2f})")
#         response.say("Sorry, I didn't catch that. Could you repeat?", voice="Polly.Joanna")
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=2,
#             timeout=5,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
#         return Response(content=str(response), media_type="application/xml")
    
#     if not SpeechResult or SpeechResult.strip() == "":
#         logger.warning(f"{log_prefix} ⚠️  Empty speech result")
#         response.say("I didn't hear anything.", voice="Polly.Joanna")
#         response.redirect('/voice')
#         return Response(content=str(response), media_type="application/xml")
    
#     try:
#         # Get customer info
#         if CallSid not in call_metadata:
#             logger.error(f"{log_prefix} ❌ No metadata found")
#             response.say("Session error. Please call again.", voice="Polly.Joanna")
#             response.hangup()
#             return Response(content=str(response), media_type="application/xml")
        
#         customer_info = call_metadata[CallSid]["customer_info"]
#         call_metadata[CallSid]["interaction_count"] += 1
#         interaction_num = call_metadata[CallSid]["interaction_count"]
        
#         logger.info(f"{log_prefix} 👤 Customer: {customer_info['name']} (Interaction #{interaction_num})")
        
#         # Get AI response
#         ai_start = time.time()
#         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
#         ai_latency = time.time() - ai_start
#         logger.info(f"{log_prefix} ✅ AI response generated in {ai_latency:.3f}s")
        
#         # Respond with TTS
#         tts_start = time.time()
#         response.say(ai_response, voice="Polly.Joanna", language="en-US")
#         tts_latency = time.time() - tts_start
#         logger.info(f"{log_prefix} 🔊 TTS completed in {tts_latency:.3f}s")
        
#         # Continue conversation
#         gather = Gather(
#             input='speech',
#             action='/process_speech',
#             method='POST',
#             speechTimeout=2,
#             timeout=5,
#             language='en-US',
#             enhanced=True
#         )
#         response.append(gather)
        
#         # Timeout fallback
#         response.say("Are you still there?", voice="Polly.Joanna")
#         response.redirect('/process_speech')
        
#         total_latency = time.time() - processing_start
#         logger.info(f"{log_prefix} ⏱️  Total /process_speech: {total_latency:.3f}s")
#         logger.info(f"{log_prefix} 📊 Breakdown - AI: {ai_latency:.3f}s, TTS: {tts_latency:.3f}s, Other: {(total_latency - ai_latency - tts_latency):.3f}s")
        
#     except Exception as e:
#         error_latency = time.time() - processing_start
#         logger.error(f"{log_prefix} ❌ Processing error after {error_latency:.3f}s: {str(e)}", exc_info=True)
#         response.say("I'm having trouble. Let me transfer you to my supervisor.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/call_status")
# async def handle_call_status(request: Request):
#     """Handle call status updates"""
#     form_data = await request.form()
#     call_sid = form_data.get("CallSid")
#     call_status = form_data.get("CallStatus")
#     call_duration = form_data.get("CallDuration", "0")
    
#     log_prefix = f"[{call_sid[:8]}]"
#     logger.info("=" * 80)
#     logger.info(f"{log_prefix} 📊 CALL STATUS UPDATE")
#     logger.info(f"{log_prefix} Status: {call_status}")
#     logger.info(f"{log_prefix} Duration: {call_duration}s")
    
#     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
#         if call_sid in conversations:
#             msg_count = len(conversations[call_sid])
#             logger.info(f"{log_prefix} 💬 Total messages exchanged: {msg_count}")
            
#         metadata = call_metadata.get(call_sid, {})
#         if metadata:
#             customer_info = metadata.get("customer_info", {})
#             logger.info(f"{log_prefix} 👤 Customer: {customer_info.get('name', 'Unknown')}")
        
#         conversations.pop(call_sid, None)
#         call_metadata.pop(call_sid, None)
        
#         logger.info(f"{log_prefix} 🧹 Call data cleaned up")
    
#     logger.info("=" * 80)
#     return Response(content="OK")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "running",
#         "service": "JIT Global Debt Collection Agent",
#         "model": "Amazon Nova Pro v1.0",
#         "region": REGION,
#         "active_calls": len(conversations),
#         "active_metadata": len(call_metadata),
#         "timestamp": datetime.now().isoformat()
#     }


# @app.get("/")
# async def root():
#     """Root endpoint with service info"""
#     return {
#         "status": "running",
#         "service": "JIT Global Debt Collection Agent",
#         "version": "3.0-NOVA-PRO-PRODUCTION",
#         "model": "us.amazon.nova-pro-v1:0",
#         "region": REGION,
#         "endpoints": {
#             "/voice": "Incoming call handler",
#             "/process_speech": "Speech processing",
#             "/call_status": "Call status webhook",
#             "/health": "Health check",
#             "/customers": "View customer info"
#         }
#     }


# @app.get("/customers")
# async def list_customers():
#     """Show customer info"""
#     return {
#         "customer": CUSTOMER_INFO,
#         "note": "Single test customer for all calls"
#     }


# if __name__ == "__main__":
#     import uvicorn
#     logger.info("🚀" * 40)
#     logger.info("🚀 JIT GLOBAL DEBT COLLECTION AGENT")
#     logger.info(f"🚀 Model: Amazon Nova Pro v1.0")
#     logger.info(f"🚀 Model ID: us.amazon.nova-pro-v1:0")
#     logger.info(f"🚀 Region: {REGION}")
#     logger.info(f"🚀 Customer: {CUSTOMER_INFO['name']}")
#     logger.info(f"🚀 Due Amount: ₹{CUSTOMER_INFO['due_amount']:,.2f}")
#     logger.info(f"🚀 Days Overdue: {CUSTOMER_INFO['days_overdue']}")
#     logger.info(f"🚀 TTS: Twilio Polly (Joanna)")
#     logger.info(f"🚀 Port: 8000")
#     logger.info("🚀" * 40)
    
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")






import re
import logging
import json
import asyncio
import boto3
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import time
from datetime import datetime
from typing import Dict, Optional

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

REGION = "us-east-1"


bedrock = boto3.client("bedrock-runtime", region_name=REGION)
polly = boto3.client("polly", region_name=REGION)

app = FastAPI()

conversations = {}
call_metadata = {}


CUSTOMER_INFO = {
    "customer_id": "CUST001",
    "name": "Praveen Kumar",
    "phone_number": "+916385740104",
    "due_amount": 5000.00,
    "due_date": "2024-10-15",
    "days_overdue": 22,
    "invoice_number": "INV-2024-1015",
    "last_contact": "2024-10-28"
}



def get_customer_info(phone_number: str) -> Dict:
    """Return the single customer info for any call"""
    logger.info(f"🔍 Call from: {phone_number}")
    logger.info(f"✅ Customer: {CUSTOMER_INFO['name']} (ID: {CUSTOMER_INFO['customer_id']})")
    return CUSTOMER_INFO


def build_system_prompt(customer: Dict) -> str:
    """Build ASSERTIVE debt collection prompt that forces Nova Pro to act"""
    prompt = f"""You are Arjun, a debt collection agent from JIT Global Financial Services calling {customer['name']}.

CRITICAL MISSION: Collect overdue payment of ₹{customer['due_amount']:,.2f}

CUSTOMER DEBT DETAILS:
- Name: {customer['name']}
- Outstanding: ₹{customer['due_amount']:,.2f}
- Invoice: {customer['invoice_number']}
- Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
- Customer ID: {customer['customer_id']}

YOUR BEHAVIOR:
1. IMMEDIATELY mention the overdue payment in your first response after customer confirms identity
2. Ask WHY they haven't paid yet
3. If they ask "what amount?", state: "₹{customer['due_amount']:,.2f} from invoice {customer['invoice_number']}"
4. Be firm but professional - this is a debt collection call, NOT customer service
5. Every response should push towards getting a payment commitment

RESPONSE RULES:
- Keep responses under 30 words
- Always tie back to the payment
- Ask direct questions: "Why haven't you paid?", "When will you pay?", "Can you pay today?"
- DO NOT give generic customer service responses
- DO NOT ask "how can I help you?" - YOU are calling THEM about debt

EXAMPLES OF GOOD RESPONSES:
Customer: "This is Praveen, what do you want?"
You: "I'm calling about your overdue payment of ₹5,000 from invoice INV-2024-1015. It was due on October 15th. Why haven't you paid yet?"

Customer: "I forgot"
You: "It's been 22 days overdue. Can you make the payment today?"

Customer: "How much do I owe?"
You: "You owe ₹5,000 from invoice INV-2024-1015, due since October 15th. When can you pay this?"

NOW RESPOND TO THE CUSTOMER'S STATEMENT. Remember: This is a DEBT COLLECTION call."""
    return prompt


async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
    """Get AI response using Amazon Nova Pro with STRICT debt collection focus"""
    start_time = time.time()
    log_prefix = f"[{conversation_id[:8]}]"
    
    logger.info(f"{log_prefix} ⚙️ Starting Nova Pro AI response")
    logger.info(f"{log_prefix} 📝 User input: '{user_input}'")
    
    try:
        # Create or load chat history
        if conversation_id not in conversations:
            logger.info(f"{log_prefix} 🆕 Creating new conversation context")
            conversations[conversation_id] = []

        history = conversations[conversation_id]

        # Build ASSERTIVE system prompt
        system_prompt = build_system_prompt(customer_info)

        messages = []

        # Add conversation history
        for msg in history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })

        # Force debt collection context in EVERY message
        if not messages:
            # First interaction - set the tone
            current_text = f"""{system_prompt}

Customer just said: "{user_input}"

This is your FIRST response after they confirmed identity. You MUST immediately mention:
1. The overdue payment amount (₹{customer_info['due_amount']:,.2f})
2. The invoice number ({customer_info['invoice_number']})
3. How many days overdue ({customer_info['days_overdue']} days)
4. Ask why they haven't paid

Your response:"""
        else:
            # Ongoing conversation - keep pressure
            current_text = f"""Remember: You're collecting ₹{customer_info['due_amount']:,.2f} that's {customer_info['days_overdue']} days overdue.

Customer said: "{user_input}"

Push for payment commitment. Your response:"""

        messages.append({
            "role": "user",
            "content": [{"text": current_text}]
        })

        logger.info(f"{log_prefix} 📦 Prepared {len(messages)} messages for Nova Pro")

        # Call Nova Pro
        request_body = {
            "messages": messages,
            "inferenceConfig": {
                "temperature": 0.7,
                "max_new_tokens": 100
            }
        }

        logger.info(f"{log_prefix} 🚀 Sending request to Amazon Nova Pro...")

        nova_start = time.time()
        response = bedrock.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        nova_latency = time.time() - nova_start
        logger.info(f"{log_prefix} ✅ Nova Pro responded in {nova_latency:.3f}s")

        # Parse response
        response_body = json.loads(response["body"].read())
        ai_response = response_body["output"]["message"]["content"][0]["text"].strip()

        # Clean output
        ai_response = re.sub(r'^(Agent|Assistant|Arjun|You|Your response):\s*', '', ai_response, flags=re.IGNORECASE)
        ai_response = ai_response.split("Customer:")[0].split("System:")[0].strip()
        ai_response = re.sub(r'\s+', ' ', ai_response).replace("\n", " ")

        # FALLBACK: If response is still generic, force debt collection
        generic_phrases = ["how can i help", "assist you", "what can i do", "how may i help"]
        if any(phrase in ai_response.lower() for phrase in generic_phrases) or len(ai_response) < 10:
            ai_response = f"I'm calling about your overdue payment of ₹{customer_info['due_amount']:,.2f} from invoice {customer_info['invoice_number']}. It was due on {customer_info['due_date']}, {customer_info['days_overdue']} days ago. Why haven't you paid yet?"
            logger.warning(f"{log_prefix} ⚠️ Generic response detected, using debt collection fallback")

        # Save to history
        history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ])
        if len(history) > 10:
            conversations[conversation_id] = history[-10:]

        total_latency = time.time() - start_time
        logger.info(f"{log_prefix} ⏱️ Total AI latency: {total_latency:.3f}s (Nova: {nova_latency:.3f}s)")
        logger.info(f"{log_prefix} 💬 Final AI response: '{ai_response}'")

        return ai_response

    except Exception as e:
        total_latency = time.time() - start_time
        logger.error(f"{log_prefix} ❌ Nova Pro error after {total_latency:.3f}s: {str(e)}", exc_info=True)
        return f"I'm calling about your overdue payment of ₹{customer_info['due_amount']:,.2f}. Can you hear me?"


@app.post("/voice")
async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
    """Handle incoming call"""
    call_start = time.time()
    logger.info("=" * 80)
    logger.info(f"📞 INCOMING CALL RECEIVED")
    logger.info(f"📞 Call SID: {CallSid}")
    logger.info(f"📞 From Number: {From}")
    logger.info("=" * 80)
    
    response = VoiceResponse()
    
    try:
        # Lookup customer information
        customer_info = get_customer_info(From)
        
        # Store call metadata
        call_metadata[CallSid] = {
            "customer_info": customer_info,
            "call_start": datetime.now().isoformat(),
            "phone_number": From,
            "interaction_count": 0
        }
        logger.info(f"💾 Call metadata stored for {CallSid}")
        
        # Initial greeting with customer name
        greeting = f"Hello, am I speaking with {customer_info['name']}? This is Arjun from JIT Global Financial Services."
        logger.info(f"👋 Greeting: '{greeting}'")
        
        response.say(greeting, voice="Polly.Joanna", language="en-US")
        
        # Gather response with optimized timeouts
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,
            timeout=5,
            language='en-US',
            enhanced=True
        )
        response.append(gather)
        
        response.redirect('/voice')
        
        total_latency = time.time() - call_start
        logger.info(f"⏱️  Total /voice processing: {total_latency:.3f}s")
        
    except Exception as e:
        error_latency = time.time() - call_start
        logger.error(f"❌ Error in /voice after {error_latency:.3f}s: {str(e)}", exc_info=True)
        response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/process_speech")
async def process_speech(
    request: Request,
    SpeechResult: str = Form(None),
    CallSid: str = Form(...),
    Confidence: str = Form("0.0")
):
    """Process speech with enhanced logging"""
    processing_start = time.time()
    log_prefix = f"[{CallSid[:8]}]"
    
    logger.info("=" * 80)
    logger.info(f"{log_prefix} 🎤 SPEECH INPUT")
    logger.info(f"{log_prefix} Text: '{SpeechResult}'")
    logger.info(f"{log_prefix} Confidence: {Confidence}")
    logger.info("=" * 80)
    
    response = VoiceResponse()
    
    # Confidence check
    confidence = float(Confidence) if Confidence else 0.0
    logger.info(f"{log_prefix} 📊 Confidence score: {confidence:.2f}")
    
    if confidence < 0.5:
        logger.warning(f"{log_prefix} ⚠️  Low confidence ({confidence:.2f})")
        response.say("Sorry, I didn't catch that. Could you repeat?", voice="Polly.Joanna")
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,
            timeout=5,
            language='en-US',
            enhanced=True
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")
    
    if not SpeechResult or SpeechResult.strip() == "":
        logger.warning(f"{log_prefix} ⚠️  Empty speech result")
        response.say("I didn't hear anything.", voice="Polly.Joanna")
        response.redirect('/voice')
        return Response(content=str(response), media_type="application/xml")
    
    try:
        # Get customer info
        if CallSid not in call_metadata:
            logger.error(f"{log_prefix} ❌ No metadata found")
            response.say("Session error. Please call again.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        customer_info = call_metadata[CallSid]["customer_info"]
        call_metadata[CallSid]["interaction_count"] += 1
        interaction_num = call_metadata[CallSid]["interaction_count"]
        
        logger.info(f"{log_prefix} 👤 Customer: {customer_info['name']} (Interaction #{interaction_num})")
        
        # Get AI response
        ai_start = time.time()
        ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
        ai_latency = time.time() - ai_start
        logger.info(f"{log_prefix} ✅ AI response generated in {ai_latency:.3f}s")
        
        # Respond with TTS
        tts_start = time.time()
        response.say(ai_response, voice="Polly.Joanna", language="en-US")
        tts_latency = time.time() - tts_start
        logger.info(f"{log_prefix} 🔊 TTS completed in {tts_latency:.3f}s")
        
        # Continue conversation
        gather = Gather(
            input='speech',
            action='/process_speech',
            method='POST',
            speechTimeout=2,
            timeout=5,
            language='en-US',
            enhanced=True
        )
        response.append(gather)
        
        # Timeout fallback
        response.say("Are you still there?", voice="Polly.Joanna")
        response.redirect('/process_speech')
        
        total_latency = time.time() - processing_start
        logger.info(f"{log_prefix} ⏱️  Total /process_speech: {total_latency:.3f}s")
        logger.info(f"{log_prefix} 📊 Breakdown - AI: {ai_latency:.3f}s, TTS: {tts_latency:.3f}s, Other: {(total_latency - ai_latency - tts_latency):.3f}s")
        
    except Exception as e:
        error_latency = time.time() - processing_start
        logger.error(f"{log_prefix} ❌ Processing error after {error_latency:.3f}s: {str(e)}", exc_info=True)
        response.say("I'm having trouble. Let me transfer you to my supervisor.", voice="Polly.Joanna")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/call_status")
async def handle_call_status(request: Request):
    """Handle call status updates"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    call_duration = form_data.get("CallDuration", "0")
    
    log_prefix = f"[{call_sid[:8]}]"
    logger.info("=" * 80)
    logger.info(f"{log_prefix} 📊 CALL STATUS UPDATE")
    logger.info(f"{log_prefix} Status: {call_status}")
    logger.info(f"{log_prefix} Duration: {call_duration}s")
    
    if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
        if call_sid in conversations:
            msg_count = len(conversations[call_sid])
            logger.info(f"{log_prefix} 💬 Total messages exchanged: {msg_count}")
            
        metadata = call_metadata.get(call_sid, {})
        if metadata:
            customer_info = metadata.get("customer_info", {})
            logger.info(f"{log_prefix} 👤 Customer: {customer_info.get('name', 'Unknown')}")
        
        conversations.pop(call_sid, None)
        call_metadata.pop(call_sid, None)
        
        logger.info(f"{log_prefix} 🧹 Call data cleaned up")
    
    logger.info("=" * 80)
    return Response(content="OK")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "JIT Global Debt Collection Agent",
        "model": "Amazon Nova Pro v1.0",
        "region": REGION,
        "active_calls": len(conversations),
        "active_metadata": len(call_metadata),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "status": "running",
        "service": "JIT Global Debt Collection Agent",
        "version": "3.0-NOVA-PRO-PRODUCTION",
        "model": "us.amazon.nova-pro-v1:0",
        "region": REGION,
        "endpoints": {
            "/voice": "Incoming call handler",
            "/process_speech": "Speech processing",
            "/call_status": "Call status webhook",
            "/health": "Health check",
            "/customers": "View customer info"
        }
    }


@app.get("/customers")
async def list_customers():
    """Show customer info"""
    return {
        "customer": CUSTOMER_INFO,
        "note": "Single test customer for all calls"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀" * 40)
    logger.info("🚀 JIT GLOBAL DEBT COLLECTION AGENT")
    logger.info(f"🚀 Model: Amazon Nova Pro v1.0")
    logger.info(f"🚀 Model ID: us.amazon.nova-pro-v1:0")
    logger.info(f"🚀 Region: {REGION}")
    logger.info(f"🚀 Customer: {CUSTOMER_INFO['name']}")
    logger.info(f"🚀 Due Amount: ₹{CUSTOMER_INFO['due_amount']:,.2f}")
    logger.info(f"🚀 Days Overdue: {CUSTOMER_INFO['days_overdue']}")
    logger.info(f"🚀 TTS: Twilio Polly (Joanna)")
    logger.info(f"🚀 Port: 8000")
    logger.info("🚀" * 40)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
