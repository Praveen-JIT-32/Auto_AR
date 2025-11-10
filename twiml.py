
import re
import logging
import json
import asyncio
import boto3
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
import time
from datetime import datetime
from typing import Dict, Optional, List
from decimal import Decimal

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

REGION = "us-east-1"
DYNAMODB_REGION = "ap-south-1"
DYNAMODB_TABLE = "call_logs"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
polly = boto3.client("polly", region_name=REGION)

app = FastAPI()

conversations = {}
call_metadata = {}


# ----------------------------------------------------------------
# 🤖 REAL-TIME AI EXTRACTION AGENT
# ----------------------------------------------------------------

class RealTimeExtractionAgent:
    """AI-powered extraction agent that runs async after each turn"""
    
    def __init__(self, bedrock_region: str, dynamodb_region: str, table_name: str):
        self.bedrock = boto3.client("bedrock-runtime", region_name=bedrock_region)
        self.dynamodb = boto3.resource("dynamodb", region_name=dynamodb_region)
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"🤖 Real-Time Extraction Agent initialized")
    
    def _convert_floats_to_decimal(self, obj):
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    def _call_nova_pro_for_extraction(self, conversation_text: str) -> Dict:
        """Use Nova Pro to extract structured insights"""
        try:
            system_prompt = """You are an AI extraction specialist analyzing debt collection conversations.
Analyze the conversation so far and extract key insights.
Respond ONLY with valid JSON. No markdown, no preamble, just pure JSON."""

            extraction_instructions = """
Extract this information from the conversation so far:

{
    "customer_name": "name or null",
    "phone_number": "phone or null", 
    "invoice_number": "invoice or null",
    "product_name": "product or null",
    "amount_due": number or null,
    "due_date": "YYYY-MM-DD or null",
    "days_overdue": number or null,
    "payment_commitment_date": "YYYY-MM-DD if customer committed, or null",
    "payment_commitment_amount": number or null,
    "customer_intent": "willing_to_pay/needs_time/financial_difficulty/disputing/uncooperative or null",
    "call_outcome": "payment_committed/follow_up_needed/dispute_raised/disconnected/no_resolution",
    "customer_reason_for_delay": "brief reason or null",
    "next_follow_up_date": "YYYY-MM-DD or null",
    "customer_sentiment": "cooperative/neutral/frustrated/angry or null",
    "conversation_summary": "brief summary of conversation so far",
    "key_points_discussed": ["list of key points discussed"],
    "extraction_timestamp": "current timestamp"
}
"""

            full_prompt = f"""{system_prompt}

CONVERSATION SO FAR:
{conversation_text}

{extraction_instructions}

Respond with ONLY the JSON object:"""

            messages = [{"role": "user", "content": [{"text": full_prompt}]}]
            
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "temperature": 0.1,
                    "max_new_tokens": 500,
                    "top_p": 0.9
                }
            }
            
            logger.info("🧠 Real-time extraction with Nova Pro...")
            response = self.bedrock.invoke_model(
                modelId="amazon.nova-pro-v1:0",
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response["body"].read())
            extracted_text = response_body["output"]["message"]["content"][0]["text"].strip()
            
            # Clean markdown formatting
            extracted_text = re.sub(r'^```json\s*', '', extracted_text)
            extracted_text = re.sub(r'\s*```$', '', extracted_text)
            extracted_text = extracted_text.strip()
            
            extracted_data = json.loads(extracted_text)
            logger.info("✅ Real-time extraction successful")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Real-time extraction failed: {e}")
            return {}
    
    async def extract_and_store_realtime(
        self,
        call_id: str,
        conversation_exchanges: List[Dict],
        customer_context: Optional[Dict] = None,
        turn_number: int = None
    ):
        """Real-time extraction after each conversation turn"""
        try:
            logger.info(f"🔄 REAL-TIME EXTRACTION for turn #{turn_number}")
            
            # Build conversation text up to current point
            conv_lines = []
            for idx, ex in enumerate(conversation_exchanges, 1):
                human = ex.get('human', ex.get('human_message', ''))
                agent = ex.get('agent', ex.get('agent_response', ''))
                conv_lines.append(f"Turn {idx}:")
                conv_lines.append(f"CUSTOMER: {human}")
                conv_lines.append(f"AGENT: {agent}")
                conv_lines.append("-" * 40)
            
            conversation_text = "\n".join(conv_lines)
            
            # Run extraction in background
            extracted = await asyncio.get_event_loop().run_in_executor(
                None, self._call_nova_pro_for_extraction, conversation_text
            )
            
            if not extracted:
                logger.warning("⚠️  Real-time extraction returned empty")
                return
            
            # Merge with customer context
            if customer_context:
                if not extracted.get('customer_name'):
                    extracted['customer_name'] = customer_context.get('name')
                if not extracted.get('phone_number'):
                    extracted['phone_number'] = customer_context.get('phone_number')
                if not extracted.get('invoice_number'):
                    extracted['invoice_number'] = customer_context.get('invoice_number')
                if not extracted.get('product_name'):
                    extracted['product_name'] = customer_context.get('product_name')
                if not extracted.get('amount_due'):
                    extracted['amount_due'] = customer_context.get('due_amount')
                if not extracted.get('due_date'):
                    extracted['due_date'] = customer_context.get('due_date')
                if not extracted.get('days_overdue'):
                    extracted['days_overdue'] = customer_context.get('days_overdue')
                
                extracted['customer_id'] = customer_context.get('customer_id')
            
            # Determine real-time status
            status = self._determine_realtime_status(extracted)
            
            # Store real-time insights
            item = {
                "call_id": call_id,
                "turn_number": turn_number,
                "record_type": "REALTIME_EXTRACTION",
                "timestamp": datetime.utcnow().isoformat(),
                "customer_name": extracted.get('customer_name'),
                "customer_id": extracted.get('customer_id'),
                "phone_number": extracted.get('phone_number'),
                "invoice_number": extracted.get('invoice_number', 'UNKNOWN'),
                "product_name": extracted.get('product_name'),
                "amount_due": self._convert_floats_to_decimal(extracted.get('amount_due')),
                "due_date": extracted.get('due_date'),
                "days_overdue": extracted.get('days_overdue'),
                "payment_commitment_date": extracted.get('payment_commitment_date'),
                "payment_commitment_amount": self._convert_floats_to_decimal(extracted.get('payment_commitment_amount')),
                "customer_intent": extracted.get('customer_intent'),
                "call_outcome": extracted.get('call_outcome'),
                "customer_reason_for_delay": extracted.get('customer_reason_for_delay'),
                "customer_sentiment": extracted.get('customer_sentiment'),
                "conversation_summary": extracted.get('conversation_summary'),
                "key_points_discussed": extracted.get('key_points_discussed', []),
                "status": status,
                "total_turns_so_far": len(conversation_exchanges),
                "extraction_type": "REALTIME_AFTER_TURN"
            }
            
            # Remove None values
            item = {k: v for k, v in item.items() if v is not None}
            
            self.table.put_item(Item=item)
            
            logger.info(f"💾 REAL-TIME extraction stored for turn #{turn_number}")
            logger.info(f"   Status: {status}, Intent: {extracted.get('customer_intent')}")
            logger.info(f"   Sentiment: {extracted.get('customer_sentiment')}")
            
        except Exception as e:
            logger.error(f"❌ Real-time extraction error: {e}")
    
    def _determine_realtime_status(self, data: Dict) -> str:
        """Determine real-time status from current conversation"""
        intent = data.get('customer_intent', '').lower()
        sentiment = data.get('customer_sentiment', '').lower()
        has_commitment = bool(data.get('payment_commitment_date'))
        
        if has_commitment:
            return "COMMITTED"
        elif 'disputing' in intent:
            return "DISPUTED"
        elif 'financial_difficulty' in intent or 'needs_time' in intent:
            return "FOLLOW_UP_REQUIRED"
        elif 'uncooperative' in intent or 'angry' in sentiment:
            return "UNCOOPERATIVE"
        elif 'willing_to_pay' in intent or 'cooperative' in sentiment:
            return "PENDING"
        else:
            return "IN_PROGRESS"


# Initialize real-time extraction agent
realtime_agent = RealTimeExtractionAgent(
    bedrock_region=REGION,
    dynamodb_region=DYNAMODB_REGION,
    table_name=DYNAMODB_TABLE
)


# ----------------------------------------------------------------
# 📊 CONVERSATION LOGGER
# ----------------------------------------------------------------

class ConversationLogger:
    """Logger for conversation turns"""
    
    def __init__(self, region: str, table_name: str):
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"📊 Conversation Logger initialized")
    
    def _convert_floats_to_decimal(self, obj):
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        return obj
    
    def log_call_start(self, call_sid: str, phone_number: str, customer_info: Dict) -> bool:
        try:
            item = {
                "call_id": call_sid,
                "record_type": "CALL_START",
                "timestamp": datetime.utcnow().isoformat(),
                "phone_number": phone_number,
                "customer_name": customer_info.get("name"),
                "invoice_number": customer_info.get("invoice_number"),
                "amount_due": self._convert_floats_to_decimal(customer_info.get("due_amount")),
                "call_status": "INITIATED"
            }
            item = {k: v for k, v in item.items() if v is not None}
            self.table.put_item(Item=item)
            logger.info(f"💾 Call start logged")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to log call start: {e}")
            return False
    
    def log_conversation_turn(
        self, call_sid: str, turn_number: int, human_message: str,
        agent_response: str, confidence: Optional[float] = None,
        customer_info: Optional[Dict] = None
    ) -> bool:
        try:
            item = {
                "call_id": call_sid,
                "turn_id": f"{call_sid}#{turn_number}",
                "record_type": "CONVERSATION_TURN",
                "timestamp": datetime.utcnow().isoformat(),
                "turn_number": turn_number,
                "human_message": human_message,
                "agent_response": agent_response
            }
            
            if confidence:
                item["confidence_score"] = self._convert_floats_to_decimal(confidence)
            if customer_info:
                item["customer_name"] = customer_info.get("name")
                item["invoice_number"] = customer_info.get("invoice_number")
            
            item = {k: v for k, v in item.items() if v is not None}
            self.table.put_item(Item=item)
            logger.info(f"💾 Turn #{turn_number} logged")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to log turn: {e}")
            return False


db_logger = ConversationLogger(region=DYNAMODB_REGION, table_name=DYNAMODB_TABLE)


# ----------------------------------------------------------------
# 📞 CUSTOMER DATA & AI RESPONSE
# ----------------------------------------------------------------

CUSTOMER_INFO = {
    "customer_id": "CUST001",
    "name": "Praveen Kumar",
    "phone_number": "+916385740104",
    "product_name": "Dell Inspiron 15 Laptop",
    "order_date": "2024-09-10",
    "purchase_date": "2024-09-12",
    "total_amount": 8000.00,
    "advance_amount": 3000.00,
    "total_paid": 3000.00,
    "due_amount": 5000.00,
    "due_date": "2024-10-15",
    "days_overdue": 22,
    "invoice_number": "INV-2024-1015",
    "last_payment_amount": 3000.00,
    "last_payment_date": "2024-09-20"
}


def get_customer_info(phone_number: str) -> Dict:
    logger.info(f"🔍 Call from: {phone_number}")
    logger.info(f"✅ Customer: {CUSTOMER_INFO['name']}")
    return CUSTOMER_INFO





def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
    """Build polite, natural debt collection prompt"""
    
    base_context = f"""You are kiwi, a polite and professional debt collection agent from JIT Global Financial Services.

CUSTOMER DETAILS:
- Name: {customer['name']}
- Product: {customer['product_name']}
- Total Amount: ₹{customer['total_amount']:,.2f}
- Amount Due: ₹{customer['due_amount']:,.2f}
- Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
- Invoice: {customer['invoice_number']}
- Last Payment: ₹{customer['last_payment_amount']:,.2f} on {customer['last_payment_date']}

CONVERSATION STYLE:
- Be polite, soft-spoken, and respectful
- Show empathy and understanding
- Keep responses 7-25 words
- Speak naturally like a caring professional
- Use warm, gentle language
- Never sound aggressive or demanding
- the exact date for payment

RESPONSE GUIDELINES:
✅ GOOD: "I understand this is difficult. When can we expect the payment?"
❌ BAD: "You must pay immediately."
❌ BAD: "Why are you delaying payment?"

QUESTION HANDLING:
- Payment history: Mention last payment amount and date
- Invoice: Provide invoice number clearly
- Due date: Mention original due date and days overdue
- Always return gently to payment discussion

YOUR GOAL: Remind about due amount while being respectful and understanding."""

    if is_first_message:
        return f"""{base_context}

FIRST MESSAGE CONTEXT:
- Customer just confirmed identity
- Mention product, invoice, amount due, due date
- Gently ask reason for delay
- Keep it 20-30 words, warm and clear"""
    
    return f"""{base_context}

CONVERSATION IN PROGRESS:
- Respond naturally to what customer just said
- If they give excuse, show understanding
- If they mention payment time, ask for specific date
- Keep responses 7-25 words, soft-spoken"""


async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
    start_time = time.time()
    log_prefix = f"[{conversation_id[:8]}]"
    
    try:
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        history = conversations[conversation_id]
        is_first_message = len(history) == 0

        system_prompt = build_system_prompt(customer_info, is_first_message)
        messages = []

        for msg in history[-8:]:
            messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

        if is_first_message:
            current_text = f"""Customer said: "{user_input}"

First message: Include product ({customer_info['product_name']}), invoice ({customer_info['invoice_number']}), amount (₹{customer_info['due_amount']:,.2f}), due date ({customer_info['due_date']}), and ask why delay. 20-30 words.

Your response:"""
        else:
            current_text = f"""Customer said: "{user_input}"

Respond politely in 7-25 words."""

        messages.append({"role": "user", "content": [{"text": f"{system_prompt}\n\n{current_text}"}]})

        request_body = {
            "messages": messages,
            "inferenceConfig": {"temperature": 0.7, "max_new_tokens": 120, "top_p": 0.9}
        }

        response = bedrock.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        ai_response = response_body["output"]["message"]["content"][0]["text"].strip()
        ai_response = re.sub(r'^(Agent|Assistant|kiwi):\s*', '', ai_response, flags=re.IGNORECASE)
        ai_response = ai_response.split("Customer:")[0].strip().strip('"\'')

        # Store both human and agent messages
        history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ])

        logger.info(f"{log_prefix} 💬 AI response: '{ai_response}'")
        return ai_response

    except Exception as e:
        logger.error(f"{log_prefix} ❌ AI error: {e}")
        return "I'm sorry, could you please repeat that?"


@app.post("/voice")
async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
    logger.info("=" * 80)
    logger.info(f"📞 CALL: {CallSid} from {From}")
    logger.info("=" * 80)
    
    response = VoiceResponse()
    
    try:
        customer_info = get_customer_info(From)
        
        db_logger.log_call_start(CallSid, From, customer_info)
        
        call_metadata[CallSid] = {
            "customer_info": customer_info,
            "call_start": datetime.now(),
            "interaction_count": 0
        }
        
        greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi from J I T Global Financial Services."
        response.say(greeting, voice="Polly.Joanna", language="en-US")
        
        gather = Gather(
            input='speech', action='/process_speech', method='POST',
            speechTimeout=2, timeout=5, language='en-US', enhanced=True
        )
        response.append(gather)
        response.redirect('/voice')
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/process_speech")
async def process_speech(
    request: Request, 
    SpeechResult: str = Form(None),
    CallSid: str = Form(...), 
    Confidence: str = Form("0.0"),
    background_tasks: BackgroundTasks = None
):
    log_prefix = f"[{CallSid[:8]}]"
    logger.info(f"{log_prefix} 🎤 Input: '{SpeechResult}' (Confidence: {Confidence})")
    
    response = VoiceResponse()
    confidence = float(Confidence) if Confidence else 0.0
    
    if confidence < 0.5:
        response.say("I'm sorry, could you repeat?", voice="Polly.Joanna")
        gather = Gather(input='speech', action='/process_speech', method='POST',
                       speechTimeout=2, timeout=10, language='en-US', enhanced=True)
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    # TRIGGER REAL-TIME EXTRACTION WHEN CALL ENDS
    if not SpeechResult or SpeechResult.strip() == "" or SpeechResult.lower() == "none":
        logger.info(f"{log_prefix} 🔚 Call ending")
        
        # Cleanup
        conversations.pop(CallSid, None)
        call_metadata.pop(CallSid, None)
        
        response.say("Thank you for your time. Goodbye.", voice="Polly.Joanna")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    try:
        if CallSid not in call_metadata:
            response.say("Session error. Please call again.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        customer_info = call_metadata[CallSid]["customer_info"]
        call_metadata[CallSid]["interaction_count"] += 1
        interaction_num = call_metadata[CallSid]["interaction_count"]
        
        ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
        
        # 💾 Log conversation turn
        db_logger.log_conversation_turn(
            CallSid, interaction_num, SpeechResult, ai_response, confidence, customer_info
        )
        
        # 🚀 TRIGGER REAL-TIME EXTRACTION AFTER EACH TURN
        if CallSid in conversations and conversations[CallSid]:
            # Prepare conversation exchanges for real-time extraction
            conv_exchanges = []
            history = conversations[CallSid]
            
            for i in range(0, len(history), 2):
                if i + 1 < len(history):
                    conv_exchanges.append({
                        "human": history[i]["content"],
                        "agent": history[i + 1]["content"]
                    })
            
            # 🔥 ASYNC REAL-TIME EXTRACTION - runs in background
            if conv_exchanges:
                logger.info(f"{log_prefix} 🚀 Starting REAL-TIME extraction for turn #{interaction_num}")
                background_tasks.add_task(
                    realtime_agent.extract_and_store_realtime,
                    CallSid,
                    conv_exchanges,
                    customer_info,
                    interaction_num
                )
        
        response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
        gather = Gather(input='speech', action='/process_speech', method='POST',
                       speechTimeout=2, timeout=10, language='en-US', enhanced=True)
        response.append(gather)
        response.say("Are you still there?", voice="Polly.Joanna")
        response.redirect('/process_speech')
        
    except Exception as e:
        logger.error(f"{log_prefix} ❌ Error: {e}")
        response.say("Technical difficulties.", voice="Polly.Joanna")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/call_status")
async def handle_call_status(request: Request):
    """Twilio webhook for call status updates"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    call_duration = form_data.get("CallDuration", "0")
    
    log_prefix = f"[{call_sid[:8]}]"
    logger.info(f"{log_prefix} 📊 CALL STATUS: {call_status}, Duration: {call_duration}s")
    
    if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
        # Cleanup
        conversations.pop(call_sid, None)
        call_metadata.pop(call_sid, None)
        logger.info(f"{log_prefix} 🧹 Cleaned up")
    
    return Response(content="OK")


@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "service": "JIT Debt Collection with REAL-TIME AI Extraction",
        "model": "Amazon Nova Pro v1.0",
        "active_calls": len(conversations),
        "extraction_type": "REALTIME_AFTER_EACH_TURN"
    }


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "JIT Debt Collection Agent with REAL-TIME AI Extraction",
        "version": "9.0-REALTIME-EXTRACTION",
        "features": [
            "Nova Pro AI for real-time analysis",
            "DynamoDB for comprehensive logging", 
            "Real-time extraction after EVERY agent response",
            "Async background processing",
            "Live conversation insights"
        ],
        "extraction_timing": "After each conversation turn (human + agent)",
        "endpoints": {
            "/voice": "Call handler",
            "/process_speech": "Speech processing (triggers real-time extraction)",
            "/call_status": "Status webhook",
            "/health": "Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀" * 50)
    logger.info("🚀 JIT DEBT COLLECTION WITH REAL-TIME AI EXTRACTION")
    logger.info(f"🚀 AI Model: Amazon Nova Pro v1.0")
    logger.info(f"🚀 Bedrock: {REGION}")
    logger.info(f"🚀 DynamoDB: {DYNAMODB_TABLE} in {DYNAMODB_REGION}")
    logger.info("🚀 Extraction: REAL-TIME after each conversation turn")
    logger.info("🚀 Processing: Async background tasks")
    logger.info("🚀" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")