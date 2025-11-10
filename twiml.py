


# # # # # import re
# # # # # import logging
# # # # # import json
# # # # # import asyncio
# # # # # import boto3
# # # # # from fastapi import FastAPI, Request, Form
# # # # # from fastapi.responses import Response
# # # # # from twilio.twiml.voice_response import VoiceResponse, Gather
# # # # # import time
# # # # # from datetime import datetime
# # # # # from typing import Dict, Optional

# # # # # # Setup comprehensive logging
# # # # # logging.basicConfig(
# # # # #     level=logging.INFO,
# # # # #     format='%(asctime)s | %(levelname)s | %(message)s',
# # # # #     datefmt='%Y-%m-%d %H:%M:%S'
# # # # # )
# # # # # logger = logging.getLogger(__name__)

# # # # # REGION = "us-east-1"

# # # # # bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# # # # # polly = boto3.client("polly", region_name=REGION)

# # # # # app = FastAPI()

# # # # # conversations = {}
# # # # # call_metadata = {}




# # # # # CUSTOMER_INFO = {
# # # # #     # Basic customer identity
# # # # #     "customer_id": "CUST001",
# # # # #     "name": "Praveen Kumar",
# # # # #     "phone_number": "+916385740104",

# # # # #     # Product and purchase details
# # # # #     "product_name": "Dell Inspiron 15 Laptop",
# # # # #     "order_date": "2024-09-10",
# # # # #     "purchase_date": "2024-09-12",
# # # # #     "quantity": 1,
# # # # #     "total_amount": 8000.00,
# # # # #     "advance_amount": 3000.00,

# # # # #     # Payment and due info
# # # # #     "total_paid": 3000.00,
# # # # #     "due_amount": 5000.00,
# # # # #     "due_date": "2024-10-15",
# # # # #     "days_overdue": 22,
# # # # #     "invoice_number": "INV-2024-1015",

# # # # #     # Transaction history
# # # # #     "last_payment_amount": 3000.00,
# # # # #     "last_payment_date": "2024-09-20",
# # # # #     "last_transaction_date": "2024-09-20",
# # # # #     "last_contact": "2024-10-28"
# # # # # }


# # # # # def get_customer_info(phone_number: str) -> Dict:
# # # # #     """Return the single customer info for any call"""
# # # # #     logger.info(f"🔍 Call from: {phone_number}")
# # # # #     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']} (ID: {CUSTOMER_INFO['customer_id']})")
# # # # #     return CUSTOMER_INFO


# # # # # def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
# # # # #     """Build polite, natural debt collection prompt"""
    
# # # # #     base_context = f"""You are kiwi, a polite and professional debt collection agent from JIT Global Financial Services.

# # # # # CUSTOMER DETAILS:
# # # # # - Name: {customer['name']}
# # # # # - Product: {customer['product_name']}
# # # # # - Order Date: {customer['order_date']}
# # # # # - Purchase Date: {customer['purchase_date']}
# # # # # - Quantity: {customer['quantity']}
# # # # # - Total Amount: ₹{customer['total_amount']:,.2f}
# # # # # - Advance Paid: ₹{customer['advance_amount']:,.2f}
# # # # # - Total Paid: ₹{customer['total_paid']:,.2f}
# # # # # - Amount Due: ₹{customer['due_amount']:,.2f}
# # # # # - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # # # # - Invoice: {customer['invoice_number']}
# # # # # - Last Payment: ₹{customer['last_payment_amount']:,.2f} on {customer['last_payment_date']}
# # # # # - Last Transaction Date: {customer['last_transaction_date']}
# # # # # - Customer ID: {customer['customer_id']}


# # # # # CONVERSATION STYLE:
# # # # # - Be polite, soft-spoken, and respectful at all times
# # # # # - Show empathy and understanding
# # # # # - Keep responses between 7-25 words
# # # # # - Speak naturally like a caring professional
# # # # # - Use warm, gentle language
# # # # # - Never sound aggressive or demanding

# # # # # CONVERSATION FLOW:
# # # # # 1. First, mention the overdue payment politely
# # # # # 2. Ask gently why they haven't paid yet
# # # # # 3. Listen to their reason with empathy



# # # # # HANDLING CUSTOMER QUESTIONS:
# # # # # - If they ask about payment history: "Your last payment was ₹{customer['last_payment_amount']:,.2f} on {customer['last_payment_date']}. The current due is ₹{customer['due_amount']:,.2f}."
# # # # # - If they ask about invoice: "The invoice number is {customer['invoice_number']}."
# # # # # - If they ask about due date: "It was due on {customer['due_date']}, that's {customer['days_overdue']} days ago."
# # # # # - If they ask about customer ID: "Your customer ID is {customer['customer_id']}."
# # # # # - After answering any question, gently bring conversation back to payment

# # # # # RESPONSE EXAMPLES:

# # # # # ✅ GOOD: "Your last payment was three thousand rupees on September twentieth. The remaining five thousand is overdue."
# # # # # ❌ BAD: "You must pay immediately."
# # # # # ❌ BAD: "Why are you delaying payment?"
# # # # # ❌ BAD: Long, complex sentences

# # # # # YOUR GOAL: to remind the due amount and due date while being respectful and understanding."""

# # # # #     if is_first_message:
# # # # #         return f"""{base_context}

# # # # #     CONTEXT: Customer just confirmed their identity. This is your FIRST response about the debt.

# # # # #     WHAT TO SAY: Naturally mention:
# # # # #     1. The product: {customer['product_name']}
# # # # #     2. The invoice: {customer['invoice_number']}
# # # # #     3. The amount due: ₹{customer['due_amount']:,.2f}
# # # # #     4. The due date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # # # #     5. Then gently ask what the reason for the delay?

# # # # #     Example: "Thank you, {customer['name']}. I'm calling about you purchased product {customer['product_name']} purchase. 
# # # # #     The invoice {customer['invoice_number']} shows ₹{customer['due_amount']:,.2f} due since {customer['due_date']}, 
# # # # #     that's {customer['days_overdue']} days overdue now. May I know the reason for the delay?"

# # # # #     Speak naturally like explaining to a friend. Keep it 20-30 words. Be warm and clear."""
    
# # # # #     return f"""{base_context}

# # # # # CONVERSATION IN PROGRESS: Respond naturally and politely to what the customer just said.
# # # # # - If they ask about payment history or transactions, provide the information clearly
# # # # # - If they give an excuse, show understanding 
# # # # # - If they say "tomorrow" or "soon", politely ask for the specific date (like November 8th)
# # # # # - speak like a humble person 
# # # # # - Always be respectful and soft-spoken

# # # # # Keep responses between 7-25 words."""


# # # # # async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
# # # # #     """Get AI response using Amazon Nova Pro with polite conversation focus"""
# # # # #     start_time = time.time()
# # # # #     log_prefix = f"[{conversation_id[:8]}]"
    
# # # # #     logger.info(f"{log_prefix} ⚙️ Starting Nova Pro AI response")
# # # # #     logger.info(f"{log_prefix} 📝 User input: '{user_input}'")
    
# # # # #     try:
# # # # #         # Create or load chat history
# # # # #         if conversation_id not in conversations:
# # # # #             logger.info(f"{log_prefix} 🆕 Creating new conversation context")
# # # # #             conversations[conversation_id] = []

# # # # #         history = conversations[conversation_id]
# # # # #         is_first_message = len(history) == 0

# # # # #         # Build system prompt
# # # # #         system_prompt = build_system_prompt(customer_info, is_first_message)

# # # # #         messages = []

# # # # #         # Add conversation history (keep last 8 messages for better context)
# # # # #         for msg in history[-8:]:
# # # # #             messages.append({
# # # # #                 "role": msg["role"],
# # # # #                 "content": [{"text": msg["content"]}]
# # # # #             })

# # # # #         # Add current user input with context
# # # # #         if is_first_message:

# # # # #             current_text = f"""Customer confirmed identity and said: "{user_input}"

# # # # #         This is your first mention of the debt. Speak naturally and include:
# # # # #         - Product: {customer_info['product_name']}
# # # # #         - Invoice: {customer_info['invoice_number']}
# # # # #         - Amount: ₹{customer_info['due_amount']:,.2f}
# # # # #         - Due date: {customer_info['due_date']} ({customer_info['days_overdue']} days overdue)
# # # # #         - Then gently ask why delay?

# # # # #         Be conversational and warm. Like explaining to a friend. 20-30 words.

# # # # #         Your response:"""

# # # # #         else:
# # # # #             # Check if customer is asking about payment history
# # # # #             payment_keywords = ["last payment", "previous payment", "paid before", "payment history", "transaction", "last paid"]
# # # # #             is_payment_query = any(keyword in user_input.lower() for keyword in payment_keywords)
            
# # # # #             if is_payment_query:
# # # # #                 current_text = f"""Customer asked: "{user_input}"

# # # # # They want to know about payment history. Answer politely with: Last payment was ₹{customer_info['last_payment_amount']:,.2f} on {customer_info['last_payment_date']}. Current due is ₹{customer_info['due_amount']:,.2f}. Then gently ask why the reason for dely?.

# # # # # Your response (7-25 words):"""
# # # # #             else:
# # # # #                 current_text = f"""Customer said: "{user_input}"

# # # # # Respond politely and naturally in 7-25 words. Be gentle and understanding.

# # # # # Your response:"""

# # # # #         messages.append({
# # # # #             "role": "user",
# # # # #             "content": [{"text": f"{system_prompt}\n\n{current_text}"}]
# # # # #         })

# # # # #         logger.info(f"{log_prefix} 📦 Prepared {len(messages)} messages for Nova Pro")

# # # # #         # Call Nova Pro
# # # # #         request_body = {
# # # # #             "messages": messages,
# # # # #             "inferenceConfig": {
# # # # #                 "temperature": 0.7,
# # # # #                 "max_new_tokens": 120,  # Increased for 7-25 word responses
# # # # #                 "top_p": 0.9
# # # # #             }
# # # # #         }

# # # # #         logger.info(f"{log_prefix} 🚀 Sending request to Amazon Nova Pro...")

# # # # #         nova_start = time.time()
# # # # #         response = bedrock.invoke_model(
# # # # #             modelId="amazon.nova-pro-v1:0",
# # # # #             body=json.dumps(request_body),
# # # # #             contentType="application/json",
# # # # #             accept="application/json"
# # # # #         )
# # # # #         nova_latency = time.time() - nova_start
# # # # #         logger.info(f"{log_prefix} ✅ Nova Pro responded in {nova_latency:.3f}s")

# # # # #         # Parse response
# # # # #         response_body = json.loads(response["body"].read())
# # # # #         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()

# # # # #         # Clean output - remove any prefixes or artifacts
# # # # #         ai_response = re.sub(r'^(Agent|Assistant|kiwi|You|Your response):\s*', '', ai_response, flags=re.IGNORECASE)
# # # # #         ai_response = ai_response.split("Customer:")[0].split("System:")[0].split("\n")[0].strip()
# # # # #         ai_response = re.sub(r'\s+', ' ', ai_response)
        
# # # # #         # Remove quotes if AI wrapped response in them
# # # # #         ai_response = ai_response.strip('"\'')

# # # # #         # Save to history
# # # # #         history.extend([
# # # # #             {"role": "user", "content": user_input},
# # # # #             {"role": "assistant", "content": ai_response}
# # # # #         ])
# # # # #         if len(history) > 12:
# # # # #             conversations[conversation_id] = history[-12:]

# # # # #         total_latency = time.time() - start_time
# # # # #         word_count = len(ai_response.split())
# # # # #         logger.info(f"{log_prefix} ⏱️ Total AI latency: {total_latency:.3f}s (Nova: {nova_latency:.3f}s)")
# # # # #         logger.info(f"{log_prefix} 💬 Final AI response ({word_count} words): '{ai_response}'")

# # # # #         return ai_response

# # # # #     except Exception as e:
# # # # #         total_latency = time.time() - start_time
# # # # #         logger.error(f"{log_prefix} ❌ Nova Pro error after {total_latency:.3f}s: {str(e)}", exc_info=True)
# # # # #         # Simple error recovery without detailed fallback
# # # # #         return "I'm sorry, could you please repeat that?"


# # # # # @app.post("/voice")
# # # # # async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
# # # # #     """Handle incoming call"""
# # # # #     call_start = time.time()
# # # # #     logger.info("=" * 80)
# # # # #     logger.info(f"📞 INCOMING CALL RECEIVED")
# # # # #     logger.info(f"📞 Call SID: {CallSid}")
# # # # #     logger.info(f"📞 From Number: {From}")
# # # # #     logger.info("=" * 80)
    
# # # # #     response = VoiceResponse()
    
# # # # #     try:
# # # # #         # Lookup customer information
# # # # #         customer_info = get_customer_info(From)
        
# # # # #         # Store call metadata
# # # # #         call_metadata[CallSid] = {
# # # # #             "customer_info": customer_info,
# # # # #             "call_start": datetime.now().isoformat(),
# # # # #             "phone_number": From,
# # # # #             "interaction_count": 0
# # # # #         }
# # # # #         logger.info(f"💾 Call metadata stored for {CallSid}")
        
# # # # #         # Initial greeting with customer name
# # # # #         greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi debt collector from J I T Global Financial Services."
# # # # #         logger.info(f"👋 Greeting: '{greeting}'")
        
# # # # #         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
# # # # #         # Gather response with optimized timeouts
# # # # #         gather = Gather(
# # # # #             input='speech',
# # # # #             action='/process_speech',
# # # # #             method='POST',
# # # # #             speechTimeout=2,
# # # # #             timeout=5,
# # # # #             language='en-US',
# # # # #             enhanced=True
# # # # #         )
# # # # #         response.append(gather)
        
# # # # #         response.redirect('/voice')
        
# # # # #         total_latency = time.time() - call_start
# # # # #         logger.info(f"⏱️  Total /voice processing: {total_latency:.3f}s")
        
# # # # #     except Exception as e:
# # # # #         error_latency = time.time() - call_start
# # # # #         logger.error(f"❌ Error in /voice after {error_latency:.3f}s: {str(e)}", exc_info=True)
# # # # #         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
# # # # #         response.hangup()
    
# # # # #     return Response(content=str(response), media_type="application/xml")


# # # # # @app.post("/process_speech")
# # # # # async def process_speech(
# # # # #     request: Request,
# # # # #     SpeechResult: str = Form(None),
# # # # #     CallSid: str = Form(...),
# # # # #     Confidence: str = Form("0.0")
# # # # # ):
# # # # #     """Process speech with enhanced logging"""
# # # # #     processing_start = time.time()
# # # # #     log_prefix = f"[{CallSid[:8]}]"
    
# # # # #     logger.info("=" * 80)
# # # # #     logger.info(f"{log_prefix} 🎤 SPEECH INPUT")
# # # # #     logger.info(f"{log_prefix} Text: '{SpeechResult}'")
# # # # #     logger.info(f"{log_prefix} Confidence: {Confidence}")
# # # # #     logger.info("=" * 80)
    
# # # # #     response = VoiceResponse()
    
# # # # #     # Confidence check
# # # # #     confidence = float(Confidence) if Confidence else 0.0
# # # # #     logger.info(f"{log_prefix} 📊 Confidence score: {confidence:.2f}")
    
# # # # #     # ⚠️ Low-confidence speech — ask to repeat
# # # # #     if confidence < 0.5:
# # # # #         logger.warning(f"{log_prefix} ⚠️  Low confidence ({confidence:.2f})")
# # # # #         response.say(
# # # # #             "I'm sorry, I didn't catch that. Could you please repeat?",
# # # # #             voice="Polly.Joanna"
# # # # #         )
# # # # #         gather = Gather(
# # # # #             input='speech',
# # # # #             action='/process_speech',
# # # # #             method='POST',
# # # # #             speechTimeout=2,
# # # # #             timeout=10,  # ⏱️ wait up to 10 seconds
# # # # #             language='en-US',
# # # # #             enhanced=True
# # # # #         )
# # # # #         response.append(gather)
# # # # #         return Response(content=str(response), media_type="application/xml")

# # # # #     # 🔇 Silence or no speech detected (after 10 seconds)
# # # # #     if not SpeechResult or SpeechResult.strip().lower() in ["", "none"]:
# # # # #         logger.warning(f"{log_prefix} 💤 No speech for 10 seconds — ending call politely.")
# # # # #         response.say(
# # # # #             "It seems you went quiet. I'll end the call now. Thank you for your time.",
# # # # #             voice="Polly.Joanna"
# # # # #         )
# # # # #         response.hangup()
# # # # #         return Response(content=str(response), media_type="application/xml")
    
# # # # #     try:
# # # # #         # Retrieve session metadata
# # # # #         if CallSid not in call_metadata:
# # # # #             logger.error(f"{log_prefix} ❌ No metadata found")
# # # # #             response.say("I apologize, there's a session error. Please call again.", voice="Polly.Joanna")
# # # # #             response.hangup()
# # # # #             return Response(content=str(response), media_type="application/xml")
        
# # # # #         customer_info = call_metadata[CallSid]["customer_info"]
# # # # #         call_metadata[CallSid]["interaction_count"] += 1
# # # # #         interaction_num = call_metadata[CallSid]["interaction_count"]
        
# # # # #         logger.info(f"{log_prefix} 👤 Customer: {customer_info['name']} (Interaction #{interaction_num})")
        
# # # # #         # 🤖 Get AI response
# # # # #         ai_start = time.time()
# # # # #         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
# # # # #         ai_latency = time.time() - ai_start
# # # # #         logger.info(f"{log_prefix} ✅ AI response generated in {ai_latency:.3f}s")
        
# # # # #         # 🗣️ Convert AI reply to speech
# # # # #         tts_start = time.time()
# # # # #         response.say(ai_response, voice="Polly.Joanna", language="en-US")
# # # # #         tts_latency = time.time() - tts_start
# # # # #         logger.info(f"{log_prefix} 🔊 TTS completed in {tts_latency:.3f}s")
        
# # # # #         # Continue listening for user response
# # # # #         gather = Gather(
# # # # #             input='speech',
# # # # #             action='/process_speech',
# # # # #             method='POST',
# # # # #             speechTimeout=2,
# # # # #             timeout=10,  # ⏱️ increased to 10 seconds
# # # # #             language='en-US',
# # # # #             enhanced=True
# # # # #         )
# # # # #         response.append(gather)
        
# # # # #         # Optional prompt if no reply
# # # # #         response.say("Are you still there?", voice="Polly.Joanna")
# # # # #         response.redirect('/process_speech')
        
# # # # #         total_latency = time.time() - processing_start
# # # # #         logger.info(f"{log_prefix} ⏱️  Total /process_speech: {total_latency:.3f}s")
# # # # #         logger.info(f"{log_prefix} 📊 Breakdown - AI: {ai_latency:.3f}s, TTS: {tts_latency:.3f}s, Other: {(total_latency - ai_latency - tts_latency):.3f}s")
        
# # # # #     except Exception as e:
# # # # #         error_latency = time.time() - processing_start
# # # # #         logger.error(f"{log_prefix} ❌ Processing error after {error_latency:.3f}s: {str(e)}", exc_info=True)
# # # # #         response.say(
# # # # #             "I apologize, I'm having technical difficulties.",
# # # # #             voice="Polly.Joanna"
# # # # #         )
# # # # #         response.hangup()
    
# # # # #     return Response(content=str(response), media_type="application/xml")






# # # # # @app.post("/call_status")
# # # # # async def handle_call_status(request: Request):
# # # # #     """Handle call status updates"""
# # # # #     form_data = await request.form()
# # # # #     call_sid = form_data.get("CallSid")
# # # # #     call_status = form_data.get("CallStatus")
# # # # #     call_duration = form_data.get("CallDuration", "0")
    
# # # # #     log_prefix = f"[{call_sid[:8]}]"
# # # # #     logger.info("=" * 80)
# # # # #     logger.info(f"{log_prefix} 📊 CALL STATUS UPDATE")
# # # # #     logger.info(f"{log_prefix} Status: {call_status}")
# # # # #     logger.info(f"{log_prefix} Duration: {call_duration}s")
    
# # # # #     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
# # # # #         if call_sid in conversations:
# # # # #             msg_count = len(conversations[call_sid])
# # # # #             logger.info(f"{log_prefix} 💬 Total messages exchanged: {msg_count}")
            
# # # # #         metadata = call_metadata.get(call_sid, {})
# # # # #         if metadata:
# # # # #             customer_info = metadata.get("customer_info", {})
# # # # #             logger.info(f"{log_prefix} 👤 Customer: {customer_info.get('name', 'Unknown')}")
        
# # # # #         conversations.pop(call_sid, None)
# # # # #         call_metadata.pop(call_sid, None)
        
# # # # #         logger.info(f"{log_prefix} 🧹 Call data cleaned up")
    
# # # # #     logger.info("=" * 80)
# # # # #     return Response(content="OK")


# # # # # @app.get("/health")
# # # # # async def health_check():
# # # # #     """Health check endpoint"""
# # # # #     return {
# # # # #         "status": "running",
# # # # #         "service": "JIT Global Debt Collection Agent",
# # # # #         "model": "Amazon Nova Pro v1.0",
# # # # #         "region": REGION,
# # # # #         "active_calls": len(conversations),
# # # # #         "active_metadata": len(call_metadata),
# # # # #         "timestamp": datetime.now().isoformat()
# # # # #     }


# # # # # @app.get("/")
# # # # # async def root():
# # # # #     """Root endpoint with service info"""
# # # # #     return {
# # # # #         "status": "running",
# # # # #         "service": "JIT Global Debt Collection Agent - Polite & Professional",
# # # # #         "version": "5.0-NOVA-PRO-POLITE",
# # # # #         "model": "amazon.nova-pro-v1:0",
# # # # #         "region": REGION,
# # # # #         "response_style": "Polite, soft-spoken, 7-25 words",
# # # # #         "endpoints": {
# # # # #             "/voice": "Incoming call handler",
# # # # #             "/process_speech": "Speech processing",
# # # # #             "/call_status": "Call status webhook",
# # # # #             "/health": "Health check",
# # # # #             "/customers": "View customer info"
# # # # #         }
# # # # #     }


# # # # # @app.get("/customers")
# # # # # async def list_customers():
# # # # #     """Show customer info"""
# # # # #     return {
# # # # #         "customer": CUSTOMER_INFO,
# # # # #         "note": "Single test customer for all calls"
# # # # #     }


# # # # # if __name__ == "__main__":
# # # # #     import uvicorn
# # # # #     logger.info("🚀" * 40)
# # # # #     logger.info("🚀 JIT GLOBAL DEBT COLLECTION AGENT - POLITE & PROFESSIONAL")
# # # # #     logger.info(f"🚀 Model: Amazon Nova Pro v1.0")
# # # # #     logger.info(f"🚀 Model ID: amazon.nova-pro-v1:0")
# # # # #     logger.info(f"🚀 Region: {REGION}")
# # # # #     logger.info(f"🚀 Customer: {CUSTOMER_INFO['name']}")
# # # # #     logger.info(f"🚀 Due Amount: ₹{CUSTOMER_INFO['due_amount']:,.2f}")
# # # # #     logger.info(f"🚀 Days Overdue: {CUSTOMER_INFO['days_overdue']}")
# # # # #     logger.info(f"🚀 Last Payment: ₹{CUSTOMER_INFO['last_payment_amount']:,.2f} on {CUSTOMER_INFO['last_payment_date']}")
# # # # #     logger.info(f"🚀 Response Style: Polite, Soft-spoken, 7-25 words")
# # # # #     logger.info(f"🚀 TTS: Twilio Polly (Joanna)")
# # # # #     logger.info(f"🚀 Port: 8000")
# # # # #     logger.info("🚀" * 40)
    
# # # # #     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")




# # # # import re
# # # # import logging
# # # # import json
# # # # import asyncio
# # # # import boto3
# # # # from fastapi import FastAPI, Request, Form
# # # # from fastapi.responses import Response
# # # # from twilio.twiml.voice_response import VoiceResponse, Gather
# # # # import time
# # # # from datetime import datetime
# # # # from typing import Dict, Optional
# # # # from decimal import Decimal

# # # # # Setup comprehensive logging
# # # # logging.basicConfig(
# # # #     level=logging.INFO,
# # # #     format='%(asctime)s | %(levelname)s | %(message)s',
# # # #     datefmt='%Y-%m-%d %H:%M:%S'
# # # # )
# # # # logger = logging.getLogger(__name__)

# # # # REGION = "us-east-1"
# # # # DYNAMODB_REGION = "ap-south-1"  # DynamoDB can be in different region
# # # # DYNAMODB_TABLE = "call_logs"

# # # # bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# # # # polly = boto3.client("polly", region_name=REGION)

# # # # app = FastAPI()

# # # # conversations = {}
# # # # call_metadata = {}


# # # # # ----------------------------------------------------------------
# # # # # 📊 DynamoDB Conversation Logger
# # # # # ----------------------------------------------------------------

# # # # class ConversationLogger:
# # # #     """Handles logging of agent-human conversations to DynamoDB"""
    
# # # #     def __init__(self, region: str, table_name: str):
# # # #         self.region = region
# # # #         self.table_name = table_name
# # # #         self.dynamodb = boto3.resource("dynamodb", region_name=region)
# # # #         self.table = self.dynamodb.Table(table_name)
# # # #         logger.info(f"📊 DynamoDB Logger initialized: {table_name} in {region}")
    
# # # #     def _convert_floats_to_decimal(self, obj):
# # # #         """Convert float values to Decimal for DynamoDB compatibility"""
# # # #         if isinstance(obj, float):
# # # #             return Decimal(str(obj))
# # # #         elif isinstance(obj, dict):
# # # #             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
# # # #         elif isinstance(obj, list):
# # # #             return [self._convert_floats_to_decimal(item) for item in obj]
# # # #         return obj
    
# # # #     def log_call_start(self, call_sid: str, phone_number: str, customer_info: Dict) -> bool:
# # # #         """Log the start of a call"""
# # # #         try:
# # # #             item = {
# # # #                 "call_id": call_sid,
# # # #                 "record_type": "CALL_START",
# # # #                 "timestamp": datetime.utcnow().isoformat(),
# # # #                 "phone_number": phone_number,
# # # #                 "customer_id": customer_info.get("customer_id"),
# # # #                 "customer_name": customer_info.get("name"),
# # # #                 "invoice_number": customer_info.get("invoice_number"),
# # # #                 "amount_due": self._convert_floats_to_decimal(customer_info.get("due_amount")),
# # # #                 "days_overdue": customer_info.get("days_overdue"),
# # # #                 "call_status": "INITIATED"
# # # #             }
            
# # # #             item = {k: v for k, v in item.items() if v is not None}
# # # #             self.table.put_item(Item=item)
# # # #             logger.info(f"💾 DB: Call start logged for {customer_info.get('name')}")
# # # #             return True
            
# # # #         except Exception as e:
# # # #             logger.error(f"❌ DB: Failed to log call start: {e}")
# # # #             return False
    
# # # #     def log_conversation_turn(
# # # #         self,
# # # #         call_sid: str,
# # # #         turn_number: int,
# # # #         human_message: str,
# # # #         agent_response: str,
# # # #         confidence: Optional[float] = None,
# # # #         customer_info: Optional[Dict] = None
# # # #     ) -> bool:
# # # #         """Log a single conversation turn"""
# # # #         try:
# # # #             turn_id = f"{call_sid}#{turn_number}"
            
# # # #             item = {
# # # #                 "call_id": call_sid,
# # # #                 "turn_id": turn_id,
# # # #                 "record_type": "CONVERSATION_TURN",
# # # #                 "timestamp": datetime.utcnow().isoformat(),
# # # #                 "turn_number": turn_number,
# # # #                 "human_message": human_message,
# # # #                 "agent_response": agent_response,
# # # #                 "message_length_human": len(human_message.split()),
# # # #                 "message_length_agent": len(agent_response.split())
# # # #             }
            
# # # #             if confidence is not None:
# # # #                 item["confidence_score"] = self._convert_floats_to_decimal(confidence)
            
# # # #             if customer_info:
# # # #                 item["customer_name"] = customer_info.get("name")
# # # #                 item["invoice_number"] = customer_info.get("invoice_number")
            
# # # #             item = {k: v for k, v in item.items() if v is not None}
# # # #             self.table.put_item(Item=item)
# # # #             logger.info(f"💾 DB: Turn #{turn_number} logged")
# # # #             return True
            
# # # #         except Exception as e:
# # # #             logger.error(f"❌ DB: Failed to log conversation turn: {e}")
# # # #             return False
    
# # # #     def log_call_end(
# # # #         self,
# # # #         call_sid: str,
# # # #         call_status: str,
# # # #         call_duration: int,
# # # #         total_turns: int,
# # # #         customer_info: Optional[Dict] = None,
# # # #         outcome: Optional[str] = None
# # # #     ) -> bool:
# # # #         """Log the end of a call with summary"""
# # # #         try:
# # # #             item = {
# # # #                 "call_id": call_sid,
# # # #                 "record_type": "CALL_END",
# # # #                 "timestamp": datetime.utcnow().isoformat(),
# # # #                 "call_status": call_status,
# # # #                 "call_duration_seconds": call_duration,
# # # #                 "total_conversation_turns": total_turns
# # # #             }
            
# # # #             if customer_info:
# # # #                 item["customer_name"] = customer_info.get("name")
# # # #                 item["invoice_number"] = customer_info.get("invoice_number")
# # # #                 item["customer_id"] = customer_info.get("customer_id")
            
# # # #             if outcome:
# # # #                 item["call_outcome"] = outcome
            
# # # #             item = {k: v for k, v in item.items() if v is not None}
# # # #             self.table.put_item(Item=item)
# # # #             logger.info(f"💾 DB: Call end logged - Status: {call_status}, Duration: {call_duration}s")
# # # #             return True
            
# # # #         except Exception as e:
# # # #             logger.error(f"❌ DB: Failed to log call end: {e}")
# # # #             return False
    
# # # #     def log_error(
# # # #         self,
# # # #         call_sid: str,
# # # #         error_message: str,
# # # #         error_type: str,
# # # #         customer_info: Optional[Dict] = None
# # # #     ) -> bool:
# # # #         """Log an error that occurred during the call"""
# # # #         try:
# # # #             item = {
# # # #                 "call_id": call_sid,
# # # #                 "record_type": "ERROR",
# # # #                 "timestamp": datetime.utcnow().isoformat(),
# # # #                 "error_message": error_message,
# # # #                 "error_type": error_type
# # # #             }
            
# # # #             if customer_info:
# # # #                 item["customer_name"] = customer_info.get("name")
# # # #                 item["invoice_number"] = customer_info.get("invoice_number")
            
# # # #             item = {k: v for k, v in item.items() if v is not None}
# # # #             self.table.put_item(Item=item)
# # # #             logger.info(f"💾 DB: Error logged")
# # # #             return True
            
# # # #         except Exception as e:
# # # #             logger.error(f"❌ DB: Failed to log error: {e}")
# # # #             return False


# # # # # Initialize the DynamoDB logger
# # # # db_logger = ConversationLogger(region=DYNAMODB_REGION, table_name=DYNAMODB_TABLE)


# # # # # ----------------------------------------------------------------
# # # # # 📞 Customer Data (Example - replace with actual DB lookup)
# # # # # ----------------------------------------------------------------

# # # # CUSTOMER_INFO = {
# # # #     "customer_id": "CUST001",
# # # #     "name": "Praveen Kumar",
# # # #     "phone_number": "+916385740104",
# # # #     "product_name": "Dell Inspiron 15 Laptop",
# # # #     "order_date": "2024-09-10",
# # # #     "purchase_date": "2024-09-12",
# # # #     "quantity": 1,
# # # #     "total_amount": 8000.00,
# # # #     "advance_amount": 3000.00,
# # # #     "total_paid": 3000.00,
# # # #     "due_amount": 5000.00,
# # # #     "due_date": "2024-10-15",
# # # #     "days_overdue": 22,
# # # #     "invoice_number": "INV-2024-1015",
# # # #     "last_payment_amount": 3000.00,
# # # #     "last_payment_date": "2024-09-20",
# # # #     "last_transaction_date": "2024-09-20",
# # # #     "last_contact": "2024-10-28"
# # # # }


# # # # def get_customer_info(phone_number: str) -> Dict:
# # # #     """Return customer info for the call"""
# # # #     logger.info(f"🔍 Call from: {phone_number}")
# # # #     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']} (ID: {CUSTOMER_INFO['customer_id']})")
# # # #     return CUSTOMER_INFO


# # # # def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
# # # #     """Build polite, natural debt collection prompt"""
    
# # # #     base_context = f"""You are kiwi, a polite and professional debt collection agent from JIT Global Financial Services.

# # # # CUSTOMER DETAILS:
# # # # - Name: {customer['name']}
# # # # - Product: {customer['product_name']}
# # # # - Order Date: {customer['order_date']}
# # # # - Purchase Date: {customer['purchase_date']}
# # # # - Quantity: {customer['quantity']}
# # # # - Total Amount: ₹{customer['total_amount']:,.2f}
# # # # - Advance Paid: ₹{customer['advance_amount']:,.2f}
# # # # - Total Paid: ₹{customer['total_paid']:,.2f}
# # # # - Amount Due: ₹{customer['due_amount']:,.2f}
# # # # - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # # # - Invoice: {customer['invoice_number']}
# # # # - Last Payment: ₹{customer['last_payment_amount']:,.2f} on {customer['last_payment_date']}
# # # # - Last Transaction Date: {customer['last_transaction_date']}
# # # # - Customer ID: {customer['customer_id']}

# # # # CONVERSATION STYLE:
# # # # - Be polite, soft-spoken, and respectful at all times
# # # # - Show empathy and understanding
# # # # - Keep responses between 7-25 words
# # # # - Speak naturally like a caring professional
# # # # - Use warm, gentle language
# # # # - Never sound aggressive or demanding

# # # # YOUR GOAL: to remind the due amount and due date while being respectful and understanding."""

# # # #     if is_first_message:
# # # #         return f"""{base_context}

# # # # CONTEXT: Customer just confirmed their identity. This is your FIRST response about the debt.

# # # # WHAT TO SAY: Naturally mention:
# # # # 1. The product: {customer['product_name']}
# # # # 2. The invoice: {customer['invoice_number']}
# # # # 3. The amount due: ₹{customer['due_amount']:,.2f}
# # # # 4. The due date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # # # 5. Then gently ask what the reason for the delay?

# # # # Speak naturally like explaining to a friend. Keep it 20-30 words. Be warm and clear."""
    
# # # #     return f"""{base_context}

# # # # CONVERSATION IN PROGRESS: Respond naturally and politely to what the customer just said.
# # # # Keep responses between 7-25 words."""


# # # # async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
# # # #     """Get AI response using Amazon Nova Pro"""
# # # #     start_time = time.time()
# # # #     log_prefix = f"[{conversation_id[:8]}]"
    
# # # #     logger.info(f"{log_prefix} ⚙️ Starting Nova Pro AI response")
# # # #     logger.info(f"{log_prefix} 📝 User input: '{user_input}'")
    
# # # #     try:
# # # #         if conversation_id not in conversations:
# # # #             logger.info(f"{log_prefix} 🆕 Creating new conversation context")
# # # #             conversations[conversation_id] = []

# # # #         history = conversations[conversation_id]
# # # #         is_first_message = len(history) == 0

# # # #         system_prompt = build_system_prompt(customer_info, is_first_message)
# # # #         messages = []

# # # #         for msg in history[-8:]:
# # # #             messages.append({
# # # #                 "role": msg["role"],
# # # #                 "content": [{"text": msg["content"]}]
# # # #             })

# # # #         if is_first_message:
# # # #             current_text = f"""Customer confirmed identity and said: "{user_input}"

# # # # This is your first mention of the debt. Speak naturally and include:
# # # # - Product: {customer_info['product_name']}
# # # # - Invoice: {customer_info['invoice_number']}
# # # # - Amount: ₹{customer_info['due_amount']:,.2f}
# # # # - Due date: {customer_info['due_date']} ({customer_info['days_overdue']} days overdue)
# # # # - Then gently ask why delay?

# # # # Be conversational and warm. 20-30 words.

# # # # Your response:"""
# # # #         else:
# # # #             payment_keywords = ["last payment", "previous payment", "paid before", "payment history", "transaction", "last paid"]
# # # #             is_payment_query = any(keyword in user_input.lower() for keyword in payment_keywords)
            
# # # #             if is_payment_query:
# # # #                 current_text = f"""Customer asked: "{user_input}"

# # # # They want to know about payment history. Answer politely: Last payment was ₹{customer_info['last_payment_amount']:,.2f} on {customer_info['last_payment_date']}. Current due is ₹{customer_info['due_amount']:,.2f}. Then gently ask why the delay.

# # # # Your response (7-25 words):"""
# # # #             else:
# # # #                 current_text = f"""Customer said: "{user_input}"

# # # # Respond politely and naturally in 7-25 words.

# # # # Your response:"""

# # # #         messages.append({
# # # #             "role": "user",
# # # #             "content": [{"text": f"{system_prompt}\n\n{current_text}"}]
# # # #         })

# # # #         request_body = {
# # # #             "messages": messages,
# # # #             "inferenceConfig": {
# # # #                 "temperature": 0.7,
# # # #                 "max_new_tokens": 120,
# # # #                 "top_p": 0.9
# # # #             }
# # # #         }

# # # #         nova_start = time.time()
# # # #         response = bedrock.invoke_model(
# # # #             modelId="amazon.nova-pro-v1:0",
# # # #             body=json.dumps(request_body),
# # # #             contentType="application/json",
# # # #             accept="application/json"
# # # #         )
# # # #         nova_latency = time.time() - nova_start
# # # #         logger.info(f"{log_prefix} ✅ Nova Pro responded in {nova_latency:.3f}s")

# # # #         response_body = json.loads(response["body"].read())
# # # #         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()

# # # #         ai_response = re.sub(r'^(Agent|Assistant|kiwi|You|Your response):\s*', '', ai_response, flags=re.IGNORECASE)
# # # #         ai_response = ai_response.split("Customer:")[0].split("System:")[0].split("\n")[0].strip()
# # # #         ai_response = re.sub(r'\s+', ' ', ai_response)
# # # #         ai_response = ai_response.strip('"\'')

# # # #         history.extend([
# # # #             {"role": "user", "content": user_input},
# # # #             {"role": "assistant", "content": ai_response}
# # # #         ])
# # # #         if len(history) > 12:
# # # #             conversations[conversation_id] = history[-12:]

# # # #         total_latency = time.time() - start_time
# # # #         word_count = len(ai_response.split())
# # # #         logger.info(f"{log_prefix} ⏱️ Total AI latency: {total_latency:.3f}s")
# # # #         logger.info(f"{log_prefix} 💬 Final AI response ({word_count} words): '{ai_response}'")

# # # #         return ai_response

# # # #     except Exception as e:
# # # #         total_latency = time.time() - start_time
# # # #         logger.error(f"{log_prefix} ❌ Nova Pro error after {total_latency:.3f}s: {str(e)}", exc_info=True)
# # # #         return "I'm sorry, could you please repeat that?"


# # # # @app.post("/voice")
# # # # async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
# # # #     """Handle incoming call with DynamoDB logging"""
# # # #     call_start = time.time()
# # # #     logger.info("=" * 80)
# # # #     logger.info(f"📞 INCOMING CALL RECEIVED")
# # # #     logger.info(f"📞 Call SID: {CallSid}")
# # # #     logger.info(f"📞 From Number: {From}")
# # # #     logger.info("=" * 80)
    
# # # #     response = VoiceResponse()
    
# # # #     try:
# # # #         customer_info = get_customer_info(From)
        
# # # #         # 💾 Log call start to DynamoDB
# # # #         db_logger.log_call_start(
# # # #             call_sid=CallSid,
# # # #             phone_number=From,
# # # #             customer_info=customer_info
# # # #         )
        
# # # #         call_metadata[CallSid] = {
# # # #             "customer_info": customer_info,
# # # #             "call_start": datetime.now().isoformat(),
# # # #             "phone_number": From,
# # # #             "interaction_count": 0
# # # #         }
# # # #         logger.info(f"💾 Call metadata stored for {CallSid}")
        
# # # #         greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi debt collector from J I T Global Financial Services."
# # # #         logger.info(f"👋 Greeting: '{greeting}'")
        
# # # #         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
# # # #         gather = Gather(
# # # #             input='speech',
# # # #             action='/process_speech',
# # # #             method='POST',
# # # #             speechTimeout=2,
# # # #             timeout=5,
# # # #             language='en-US',
# # # #             enhanced=True
# # # #         )
# # # #         response.append(gather)
# # # #         response.redirect('/voice')
        
# # # #         total_latency = time.time() - call_start
# # # #         logger.info(f"⏱️  Total /voice processing: {total_latency:.3f}s")
        
# # # #     except Exception as e:
# # # #         error_latency = time.time() - call_start
# # # #         logger.error(f"❌ Error in /voice after {error_latency:.3f}s: {str(e)}", exc_info=True)
        
# # # #         # 💾 Log error to DynamoDB
# # # #         if CallSid and 'customer_info' in locals():
# # # #             db_logger.log_error(
# # # #                 call_sid=CallSid,
# # # #                 error_message=str(e),
# # # #                 error_type="CALL_START_ERROR",
# # # #                 customer_info=customer_info
# # # #             )
        
# # # #         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
# # # #         response.hangup()
    
# # # #     return Response(content=str(response), media_type="application/xml")


# # # # @app.post("/process_speech")
# # # # async def process_speech(
# # # #     request: Request,
# # # #     SpeechResult: str = Form(None),
# # # #     CallSid: str = Form(...),
# # # #     Confidence: str = Form("0.0")
# # # # ):
# # # #     """Process speech with DynamoDB logging"""
# # # #     processing_start = time.time()
# # # #     log_prefix = f"[{CallSid[:8]}]"
    
# # # #     logger.info("=" * 80)
# # # #     logger.info(f"{log_prefix} 🎤 SPEECH INPUT")
# # # #     logger.info(f"{log_prefix} Text: '{SpeechResult}'")
# # # #     logger.info(f"{log_prefix} Confidence: {Confidence}")
# # # #     logger.info("=" * 80)
    
# # # #     response = VoiceResponse()
# # # #     confidence = float(Confidence) if Confidence else 0.0
    
# # # #     # Low confidence - ask to repeat
# # # #     if confidence < 0.5:
# # # #         logger.warning(f"{log_prefix} ⚠️  Low confidence ({confidence:.2f})")
# # # #         response.say("I'm sorry, I didn't catch that. Could you please repeat?", voice="Polly.Joanna")
# # # #         gather = Gather(
# # # #             input='speech',
# # # #             action='/process_speech',
# # # #             method='POST',
# # # #             speechTimeout=2,
# # # #             timeout=10,
# # # #             language='en-US',
# # # #             enhanced=True
# # # #         )
# # # #         response.append(gather)
# # # #         return Response(content=str(response), media_type="application/xml")

# # # #     # No speech detected
# # # #     if not SpeechResult or SpeechResult.strip().lower() in ["", "none"]:
# # # #         logger.warning(f"{log_prefix} 💤 No speech for 10 seconds — ending call.")
# # # #         response.say("It seems you went quiet. I'll end the call now. Thank you for your time.", voice="Polly.Joanna")
# # # #         response.hangup()
# # # #         return Response(content=str(response), media_type="application/xml")
    
# # # #     try:
# # # #         if CallSid not in call_metadata:
# # # #             logger.error(f"{log_prefix} ❌ No metadata found")
# # # #             response.say("I apologize, there's a session error. Please call again.", voice="Polly.Joanna")
# # # #             response.hangup()
# # # #             return Response(content=str(response), media_type="application/xml")
        
# # # #         customer_info = call_metadata[CallSid]["customer_info"]
# # # #         call_metadata[CallSid]["interaction_count"] += 1
# # # #         interaction_num = call_metadata[CallSid]["interaction_count"]
        
# # # #         logger.info(f"{log_prefix} 👤 Customer: {customer_info['name']} (Turn #{interaction_num})")
        
# # # #         # Get AI response
# # # #         ai_start = time.time()
# # # #         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
# # # #         ai_latency = time.time() - ai_start
# # # #         logger.info(f"{log_prefix} ✅ AI response generated in {ai_latency:.3f}s")
        
# # # #         # 💾 Log conversation turn to DynamoDB
# # # #         db_logger.log_conversation_turn(
# # # #             call_sid=CallSid,
# # # #             turn_number=interaction_num,
# # # #             human_message=SpeechResult,
# # # #             agent_response=ai_response,
# # # #             confidence=confidence,
# # # #             customer_info=customer_info
# # # #         )
        
# # # #         # Convert to speech
# # # #         tts_start = time.time()
# # # #         response.say(ai_response, voice="Polly.Joanna", language="en-US")
# # # #         tts_latency = time.time() - tts_start
# # # #         logger.info(f"{log_prefix} 🔊 TTS completed in {tts_latency:.3f}s")
        
# # # #         gather = Gather(
# # # #             input='speech',
# # # #             action='/process_speech',
# # # #             method='POST',
# # # #             speechTimeout=2,
# # # #             timeout=10,
# # # #             language='en-US',
# # # #             enhanced=True
# # # #         )
# # # #         response.append(gather)
# # # #         response.say("Are you still there?", voice="Polly.Joanna")
# # # #         response.redirect('/process_speech')
        
# # # #         total_latency = time.time() - processing_start
# # # #         logger.info(f"{log_prefix} ⏱️  Total /process_speech: {total_latency:.3f}s")
        
# # # #     except Exception as e:
# # # #         error_latency = time.time() - processing_start
# # # #         logger.error(f"{log_prefix} ❌ Processing error after {error_latency:.3f}s: {str(e)}", exc_info=True)
        
# # # #         # 💾 Log error to DynamoDB
# # # #         if CallSid and 'customer_info' in locals():
# # # #             db_logger.log_error(
# # # #                 call_sid=CallSid,
# # # #                 error_message=str(e),
# # # #                 error_type="SPEECH_PROCESSING_ERROR",
# # # #                 customer_info=customer_info
# # # #             )
        
# # # #         response.say("I apologize, I'm having technical difficulties.", voice="Polly.Joanna")
# # # #         response.hangup()
    
# # # #     return Response(content=str(response), media_type="application/xml")


# # # # @app.post("/call_status")
# # # # async def handle_call_status(request: Request):
# # # #     """Handle call status updates with DynamoDB logging"""
# # # #     form_data = await request.form()
# # # #     call_sid = form_data.get("CallSid")
# # # #     call_status = form_data.get("CallStatus")
# # # #     call_duration = form_data.get("CallDuration", "0")
    
# # # #     log_prefix = f"[{call_sid[:8]}]"
# # # #     logger.info("=" * 80)
# # # #     logger.info(f"{log_prefix} 📊 CALL STATUS UPDATE")
# # # #     logger.info(f"{log_prefix} Status: {call_status}")
# # # #     logger.info(f"{log_prefix} Duration: {call_duration}s")
    
# # # #     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
# # # #         total_turns = 0
# # # #         if call_sid in conversations:
# # # #             total_turns = len(conversations[call_sid]) // 2
# # # #             logger.info(f"{log_prefix} 💬 Total conversation turns: {total_turns}")
        
# # # #         metadata = call_metadata.get(call_sid, {})
# # # #         customer_info = metadata.get("customer_info")
        
# # # #         # 💾 Log call end to DynamoDB
# # # #         if customer_info:
# # # #             db_logger.log_call_end(
# # # #                 call_sid=call_sid,
# # # #                 call_status=call_status,
# # # #                 call_duration=int(call_duration),
# # # #                 total_turns=total_turns,
# # # #                 customer_info=customer_info
# # # #             )
        
# # # #         conversations.pop(call_sid, None)
# # # #         call_metadata.pop(call_sid, None)
# # # #         logger.info(f"{log_prefix} 🧹 Call data cleaned up")
    
# # # #     logger.info("=" * 80)
# # # #     return Response(content="OK")


# # # # @app.get("/health")
# # # # async def health_check():
# # # #     """Health check endpoint"""
# # # #     return {
# # # #         "status": "running",
# # # #         "service": "JIT Global Debt Collection Agent",
# # # #         "model": "Amazon Nova Pro v1.0",
# # # #         "region": REGION,
# # # #         "dynamodb_region": DYNAMODB_REGION,
# # # #         "dynamodb_table": DYNAMODB_TABLE,
# # # #         "active_calls": len(conversations),
# # # #         "timestamp": datetime.now().isoformat()
# # # #     }


# # # # @app.get("/")
# # # # async def root():
# # # #     """Root endpoint with service info"""
# # # #     return {
# # # #         "status": "running",
# # # #         "service": "JIT Global Debt Collection Agent - With DynamoDB Logging",
# # # #         "version": "6.0-NOVA-PRO-DYNAMODB",
# # # #         "model": "amazon.nova-pro-v1:0",
# # # #         "region": REGION,
# # # #         "dynamodb": {
# # # #             "region": DYNAMODB_REGION,
# # # #             "table": DYNAMODB_TABLE,
# # # #             "enabled": True
# # # #         },
# # # #         "endpoints": {
# # # #             "/voice": "Incoming call handler",
# # # #             "/process_speech": "Speech processing",
# # # #             "/call_status": "Call status webhook",
# # # #             "/health": "Health check",
# # # #             "/customers": "View customer info"
# # # #         }
# # # #     }


# # # # @app.get("/customers")
# # # # async def list_customers():
# # # #     """Show customer info"""
# # # #     return {
# # # #         "customer": CUSTOMER_INFO,
# # # #         "note": "Single test customer for all calls"
# # # #     }


# # # # if __name__ == "__main__":
# # # #     import uvicorn
# # # #     logger.info("🚀" * 40)
# # # #     logger.info("🚀 JIT GLOBAL DEBT COLLECTION AGENT")
# # # #     logger.info(f"🚀 Model: Amazon Nova Pro v1.0")
# # # #     logger.info(f"🚀 Bedrock Region: {REGION}")
# # # #     logger.info(f"🚀 DynamoDB: {DYNAMODB_TABLE} in {DYNAMODB_REGION}")
# # # #     logger.info(f"🚀 Customer: {CUSTOMER_INFO['name']}")
# # # #     logger.info(f"🚀 Due Amount: ₹{CUSTOMER_INFO['due_amount']:,.2f}")
# # # #     logger.info(f"🚀 Logging: All conversations stored in DynamoDB")
# # # #     logger.info("🚀" * 40)
    
# # # #     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")







# # # import re
# # # import logging
# # # import json
# # # import asyncio
# # # import boto3
# # # from fastapi import FastAPI, Request, Form
# # # from fastapi.responses import Response
# # # from twilio.twiml.voice_response import VoiceResponse, Gather
# # # import time
# # # from datetime import datetime
# # # from typing import Dict, Optional, List
# # # from decimal import Decimal

# # # # Setup comprehensive logging
# # # logging.basicConfig(
# # #     level=logging.INFO,
# # #     format='%(asctime)s | %(levelname)s | %(message)s',
# # #     datefmt='%Y-%m-%d %H:%M:%S'
# # # )
# # # logger = logging.getLogger(__name__)

# # # REGION = "us-east-1"
# # # DYNAMODB_REGION = "ap-south-1"
# # # DYNAMODB_TABLE = "call_logs"

# # # bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# # # polly = boto3.client("polly", region_name=REGION)

# # # app = FastAPI()

# # # conversations = {}
# # # call_metadata = {}


# # # # ----------------------------------------------------------------
# # # # 🤖 AI EXTRACTION AGENT
# # # # ----------------------------------------------------------------

# # # class ConversationExtractionAgent:
# # #     """AI-powered extraction agent using Nova Pro"""
    
# # #     def __init__(self, bedrock_region: str, dynamodb_region: str, table_name: str):
# # #         self.bedrock = boto3.client("bedrock-runtime", region_name=bedrock_region)
# # #         self.dynamodb = boto3.resource("dynamodb", region_name=dynamodb_region)
# # #         self.table = self.dynamodb.Table(table_name)
# # #         logger.info(f"🤖 AI Extraction Agent initialized")
    
# # #     def _convert_floats_to_decimal(self, obj):
# # #         if isinstance(obj, float):
# # #             return Decimal(str(obj))
# # #         elif isinstance(obj, dict):
# # #             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
# # #         elif isinstance(obj, list):
# # #             return [self._convert_floats_to_decimal(item) for item in obj]
# # #         return obj
    
# # #     def _call_nova_pro_for_extraction(self, conversation_text: str) -> Dict:
# # #         """Use Nova Pro to extract structured insights"""
# # #         try:
# # #             system_prompt = """You are an AI extraction specialist analyzing debt collection conversations.
# # # Respond ONLY with valid JSON. No markdown, no preamble, just pure JSON."""

# # #             extraction_instructions = """
# # # Extract this information from the conversation:

# # # {
# # #     "customer_name": "name or null",
# # #     "phone_number": "phone or null",
# # #     "invoice_number": "invoice or null",
# # #     "product_name": "product or null",
# # #     "amount_due": number or null,
# # #     "due_date": "YYYY-MM-DD or null",
# # #     "days_overdue": number or null,
# # #     "payment_commitment_date": "YYYY-MM-DD if customer committed, or null",
# # #     "payment_commitment_amount": number or null,
# # #     "customer_intent": "willing_to_pay/needs_time/financial_difficulty/disputing/uncooperative or null",
# # #     "call_outcome": "payment_committed/follow_up_needed/dispute_raised/disconnected/no_resolution",
# # #     "customer_reason_for_delay": "brief reason or null",
# # #     "next_follow_up_date": "YYYY-MM-DD or null",
# # #     "customer_sentiment": "cooperative/neutral/frustrated/angry or null",
# # #     "call_summary": "2-3 sentence summary"
# # # }
# # # """

# # #             full_prompt = f"""{system_prompt}

# # # CONVERSATION:
# # # {conversation_text}

# # # {extraction_instructions}

# # # Respond with ONLY the JSON object:"""

# # #             messages = [{"role": "user", "content": [{"text": full_prompt}]}]
            
# # #             request_body = {
# # #                 "messages": messages,
# # #                 "inferenceConfig": {
# # #                     "temperature": 0.1,
# # #                     "max_new_tokens": 500,
# # #                     "top_p": 0.9
# # #                 }
# # #             }
            
# # #             logger.info("🧠 Extracting insights with Nova Pro...")
# # #             response = self.bedrock.invoke_model(
# # #                 modelId="amazon.nova-pro-v1:0",
# # #                 body=json.dumps(request_body),
# # #                 contentType="application/json",
# # #                 accept="application/json"
# # #             )
            
# # #             response_body = json.loads(response["body"].read())
# # #             extracted_text = response_body["output"]["message"]["content"][0]["text"].strip()
            
# # #             # Clean markdown formatting
# # #             extracted_text = re.sub(r'^```json\s*', '', extracted_text)
# # #             extracted_text = re.sub(r'\s*```$', '', extracted_text)
# # #             extracted_text = extracted_text.strip()
            
# # #             extracted_data = json.loads(extracted_text)
# # #             logger.info("✅ Extraction successful")
            
# # #             return extracted_data
            
# # #         except Exception as e:
# # #             logger.error(f"❌ Extraction failed: {e}")
# # #             return {}
    
# # #     def analyze_and_store(
# # #         self,
# # #         call_id: str,
# # #         conversation_exchanges: List[Dict],
# # #         customer_context: Optional[Dict] = None
# # #     ) -> Dict:
# # #         """Analyze conversation and store extracted insights"""
# # #         try:
# # #             logger.info(f"🔍 Analyzing conversation {call_id[:8]}...")
            
# # #             # Build conversation text
# # #             conv_lines = []
# # #             for idx, ex in enumerate(conversation_exchanges, 1):
# # #                 human = ex.get('human', ex.get('human_message', ''))
# # #                 agent = ex.get('agent', ex.get('agent_response', ''))
# # #                 conv_lines.append(f"Turn {idx}:")
# # #                 conv_lines.append(f"HUMAN: {human}")
# # #                 conv_lines.append(f"AGENT: {agent}")
# # #                 conv_lines.append("")
            
# # #             conversation_text = "\n".join(conv_lines)
            
# # #             # Extract using Nova Pro
# # #             extracted = self._call_nova_pro_for_extraction(conversation_text)
            
# # #             if not extracted:
# # #                 logger.warning("⚠️  Extraction returned empty")
# # #                 return {}
            
# # #             # Merge with customer context
# # #             if customer_context:
# # #                 extracted['customer_name'] = extracted.get('customer_name') or customer_context.get('name')
# # #                 extracted['phone_number'] = extracted.get('phone_number') or customer_context.get('phone_number')
# # #                 extracted['invoice_number'] = extracted.get('invoice_number') or customer_context.get('invoice_number')
# # #                 extracted['amount_due'] = extracted.get('amount_due') or customer_context.get('due_amount')
# # #                 extracted['due_date'] = extracted.get('due_date') or customer_context.get('due_date')
# # #                 extracted['days_overdue'] = extracted.get('days_overdue') or customer_context.get('days_overdue')
# # #                 extracted['customer_id'] = customer_context.get('customer_id')
# # #                 extracted['product_name'] = extracted.get('product_name') or customer_context.get('product_name')
            
# # #             # Determine status
# # #             status = self._determine_status(extracted)
            
# # #             # Store to DynamoDB
# # #             item = {
# # #                 "call_id": call_id,
# # #                 "invoice_number": extracted.get('invoice_number', 'UNKNOWN'),
# # #                 "timestamp": datetime.utcnow().isoformat(),
# # #                 "record_type": "EXTRACTED_INSIGHTS",
# # #                 "customer_name": extracted.get('customer_name'),
# # #                 "customer_id": extracted.get('customer_id'),
# # #                 "phone_number": extracted.get('phone_number'),
# # #                 "product_name": extracted.get('product_name'),
# # #                 "amount_due": self._convert_floats_to_decimal(extracted.get('amount_due')),
# # #                 "due_date": extracted.get('due_date'),
# # #                 "days_overdue": extracted.get('days_overdue'),
# # #                 "payment_commitment_date": extracted.get('payment_commitment_date'),
# # #                 "payment_commitment_amount": self._convert_floats_to_decimal(extracted.get('payment_commitment_amount')),
# # #                 "next_follow_up_date": extracted.get('next_follow_up_date'),
# # #                 "call_outcome": extracted.get('call_outcome'),
# # #                 "customer_intent": extracted.get('customer_intent'),
# # #                 "customer_reason_for_delay": extracted.get('customer_reason_for_delay'),
# # #                 "customer_sentiment": extracted.get('customer_sentiment'),
# # #                 "call_summary": extracted.get('call_summary'),
# # #                 "status": status,
# # #                 "total_conversation_turns": len(conversation_exchanges)
# # #             }
            
# # #             # Remove None values
# # #             item = {k: v for k, v in item.items() if v is not None}
            
# # #             self.table.put_item(Item=item)
            
# # #             logger.info(f"💾 Insights stored - Status: {status}, Outcome: {item.get('call_outcome')}")
            
# # #             return extracted
            
# # #         except Exception as e:
# # #             logger.error(f"❌ Analysis failed: {e}", exc_info=True)
# # #             return {}
    
# # #     def _determine_status(self, data: Dict) -> str:
# # #         """Determine status from extracted data"""
# # #         outcome = data.get('call_outcome', '').lower()
# # #         intent = data.get('customer_intent', '').lower()
# # #         has_commitment = bool(data.get('payment_commitment_date'))
        
# # #         if has_commitment or 'payment_committed' in outcome:
# # #             return "COMMITTED"
# # #         elif 'dispute' in outcome or 'disputing' in intent:
# # #             return "DISPUTED"
# # #         elif 'follow_up' in outcome:
# # #             return "FOLLOW_UP_REQUIRED"
# # #         elif 'uncooperative' in intent or 'disconnected' in outcome:
# # #             return "UNCOOPERATIVE"
# # #         elif 'willing_to_pay' in intent or 'needs_time' in intent:
# # #             return "PENDING"
# # #         else:
# # #             return "NEEDS_REVIEW"


# # # # Initialize extraction agent
# # # extraction_agent = ConversationExtractionAgent(
# # #     bedrock_region=REGION,
# # #     dynamodb_region=DYNAMODB_REGION,
# # #     table_name=DYNAMODB_TABLE
# # # )


# # # # ----------------------------------------------------------------
# # # # 📊 BASIC CONVERSATION LOGGER
# # # # ----------------------------------------------------------------

# # # class ConversationLogger:
# # #     """Basic logger for conversation turns"""
    
# # #     def __init__(self, region: str, table_name: str):
# # #         self.dynamodb = boto3.resource("dynamodb", region_name=region)
# # #         self.table = self.dynamodb.Table(table_name)
# # #         logger.info(f"📊 Conversation Logger initialized")
    
# # #     def _convert_floats_to_decimal(self, obj):
# # #         if isinstance(obj, float):
# # #             return Decimal(str(obj))
# # #         elif isinstance(obj, dict):
# # #             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
# # #         return obj
    
# # #     def log_call_start(self, call_sid: str, phone_number: str, customer_info: Dict) -> bool:
# # #         try:
# # #             item = {
# # #                 "call_id": call_sid,
# # #                 "record_type": "CALL_START",
# # #                 "timestamp": datetime.utcnow().isoformat(),
# # #                 "phone_number": phone_number,
# # #                 "customer_name": customer_info.get("name"),
# # #                 "invoice_number": customer_info.get("invoice_number"),
# # #                 "amount_due": self._convert_floats_to_decimal(customer_info.get("due_amount")),
# # #                 "call_status": "INITIATED"
# # #             }
# # #             item = {k: v for k, v in item.items() if v is not None}
# # #             self.table.put_item(Item=item)
# # #             logger.info(f"💾 Call start logged")
# # #             return True
# # #         except Exception as e:
# # #             logger.error(f"❌ Failed to log call start: {e}")
# # #             return False
    
# # #     def log_conversation_turn(
# # #         self, call_sid: str, turn_number: int, human_message: str,
# # #         agent_response: str, confidence: Optional[float] = None,
# # #         customer_info: Optional[Dict] = None
# # #     ) -> bool:
# # #         try:
# # #             item = {
# # #                 "call_id": call_sid,
# # #                 "turn_id": f"{call_sid}#{turn_number}",
# # #                 "record_type": "CONVERSATION_TURN",
# # #                 "timestamp": datetime.utcnow().isoformat(),
# # #                 "turn_number": turn_number,
# # #                 "human_message": human_message,
# # #                 "agent_response": agent_response
# # #             }
            
# # #             if confidence:
# # #                 item["confidence_score"] = self._convert_floats_to_decimal(confidence)
# # #             if customer_info:
# # #                 item["customer_name"] = customer_info.get("name")
# # #                 item["invoice_number"] = customer_info.get("invoice_number")
            
# # #             item = {k: v for k, v in item.items() if v is not None}
# # #             self.table.put_item(Item=item)
# # #             logger.info(f"💾 Turn #{turn_number} logged")
# # #             return True
# # #         except Exception as e:
# # #             logger.error(f"❌ Failed to log turn: {e}")
# # #             return False


# # # db_logger = ConversationLogger(region=DYNAMODB_REGION, table_name=DYNAMODB_TABLE)


# # # # ----------------------------------------------------------------
# # # # 📞 CUSTOMER DATA
# # # # ----------------------------------------------------------------

# # # CUSTOMER_INFO = {
# # #     "customer_id": "CUST001",
# # #     "name": "Praveen Kumar",
# # #     "phone_number": "+916385740104",
# # #     "product_name": "Dell Inspiron 15 Laptop",
# # #     "order_date": "2024-09-10",
# # #     "purchase_date": "2024-09-12",
# # #     "total_amount": 8000.00,
# # #     "advance_amount": 3000.00,
# # #     "total_paid": 3000.00,
# # #     "due_amount": 5000.00,
# # #     "due_date": "2024-10-15",
# # #     "days_overdue": 22,
# # #     "invoice_number": "INV-2024-1015",
# # #     "last_payment_amount": 3000.00,
# # #     "last_payment_date": "2024-09-20"
# # # }


# # # def get_customer_info(phone_number: str) -> Dict:
# # #     logger.info(f"🔍 Call from: {phone_number}")
# # #     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']}")
# # #     return CUSTOMER_INFO


# # # def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
# # #     base_context = f"""You are kiwi, a polite debt collection agent from JIT Global Financial Services.

# # # CUSTOMER DETAILS:
# # # - Name: {customer['name']}
# # # - Product: {customer['product_name']}
# # # - Total Amount: ₹{customer['total_amount']:,.2f}
# # # - Amount Due: ₹{customer['due_amount']:,.2f}
# # # - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # # - Invoice: {customer['invoice_number']}

# # # CONVERSATION STYLE:
# # # - Be polite and respectful
# # # - Keep responses 7-25 words
# # # - Show empathy
# # # - Never be aggressive"""

# # #     if is_first_message:
# # #         return f"""{base_context}

# # # This is your FIRST message. Mention product, invoice, amount due, due date, and ask reason for delay.
# # # Keep it 20-30 words."""
    
# # #     return f"""{base_context}

# # # Respond naturally to customer. Keep it 7-25 words."""


# # # async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
# # #     start_time = time.time()
# # #     log_prefix = f"[{conversation_id[:8]}]"
    
# # #     try:
# # #         if conversation_id not in conversations:
# # #             conversations[conversation_id] = []

# # #         history = conversations[conversation_id]
# # #         is_first_message = len(history) == 0

# # #         system_prompt = build_system_prompt(customer_info, is_first_message)
# # #         messages = []

# # #         for msg in history[-8:]:
# # #             messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

# # #         if is_first_message:
# # #             current_text = f"""Customer said: "{user_input}"

# # # First message: Include product ({customer_info['product_name']}), invoice ({customer_info['invoice_number']}), amount (₹{customer_info['due_amount']:,.2f}), due date ({customer_info['due_date']}), and ask why delay. 20-30 words.

# # # Your response:"""
# # #         else:
# # #             current_text = f"""Customer said: "{user_input}"

# # # Respond politely in 7-25 words."""

# # #         messages.append({"role": "user", "content": [{"text": f"{system_prompt}\n\n{current_text}"}]})

# # #         request_body = {
# # #             "messages": messages,
# # #             "inferenceConfig": {"temperature": 0.7, "max_new_tokens": 120, "top_p": 0.9}
# # #         }

# # #         response = bedrock.invoke_model(
# # #             modelId="amazon.nova-pro-v1:0",
# # #             body=json.dumps(request_body),
# # #             contentType="application/json",
# # #             accept="application/json"
# # #         )

# # #         response_body = json.loads(response["body"].read())
# # #         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()
# # #         ai_response = re.sub(r'^(Agent|Assistant|kiwi):\s*', '', ai_response, flags=re.IGNORECASE)
# # #         ai_response = ai_response.split("Customer:")[0].strip().strip('"\'')

# # #         history.extend([
# # #             {"role": "user", "content": user_input},
# # #             {"role": "assistant", "content": ai_response}
# # #         ])

# # #         logger.info(f"{log_prefix} 💬 AI response: '{ai_response}'")
# # #         return ai_response

# # #     except Exception as e:
# # #         logger.error(f"{log_prefix} ❌ AI error: {e}")
# # #         return "I'm sorry, could you please repeat that?"


# # # @app.post("/voice")
# # # async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
# # #     logger.info("=" * 80)
# # #     logger.info(f"📞 CALL: {CallSid} from {From}")
# # #     logger.info("=" * 80)
    
# # #     response = VoiceResponse()
    
# # #     try:
# # #         customer_info = get_customer_info(From)
        
# # #         db_logger.log_call_start(CallSid, From, customer_info)
        
# # #         call_metadata[CallSid] = {
# # #             "customer_info": customer_info,
# # #             "call_start": datetime.now(),
# # #             "interaction_count": 0
# # #         }
        
# # #         greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi from J I T Global Financial Services."
# # #         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
# # #         gather = Gather(
# # #             input='speech', action='/process_speech', method='POST',
# # #             speechTimeout=2, timeout=5, language='en-US', enhanced=True
# # #         )
# # #         response.append(gather)
# # #         response.redirect('/voice')
        
# # #     except Exception as e:
# # #         logger.error(f"❌ Error: {e}")
# # #         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
# # #         response.hangup()
    
# # #     return Response(content=str(response), media_type="application/xml")


# # # @app.post("/process_speech")
# # # async def process_speech(
# # #     request: Request, SpeechResult: str = Form(None),
# # #     CallSid: str = Form(...), Confidence: str = Form("0.0")
# # # ):
# # #     log_prefix = f"[{CallSid[:8]}]"
# # #     logger.info(f"{log_prefix} 🎤 Input: '{SpeechResult}' (Confidence: {Confidence})")
    
# # #     response = VoiceResponse()
# # #     confidence = float(Confidence) if Confidence else 0.0
    
# # #     if confidence < 0.5:
# # #         response.say("I'm sorry, could you repeat?", voice="Polly.Joanna")
# # #         gather = Gather(input='speech', action='/process_speech', method='POST',
# # #                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
# # #         response.append(gather)
# # #         return Response(content=str(response), media_type="application/xml")

# # #     if not SpeechResult or SpeechResult.strip() == "":
# # #         response.say("It seems you went quiet. Thank you for your time.", voice="Polly.Joanna")
# # #         response.hangup()
# # #         return Response(content=str(response), media_type="application/xml")
    
# # #     try:
# # #         if CallSid not in call_metadata:
# # #             response.say("Session error. Please call again.", voice="Polly.Joanna")
# # #             response.hangup()
# # #             return Response(content=str(response), media_type="application/xml")
        
# # #         customer_info = call_metadata[CallSid]["customer_info"]
# # #         call_metadata[CallSid]["interaction_count"] += 1
# # #         interaction_num = call_metadata[CallSid]["interaction_count"]
        
# # #         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
        
# # #         db_logger.log_conversation_turn(
# # #             CallSid, interaction_num, SpeechResult, ai_response, confidence, customer_info
# # #         )
        
# # #         response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
# # #         gather = Gather(input='speech', action='/process_speech', method='POST',
# # #                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
# # #         response.append(gather)
# # #         response.say("Are you still there?", voice="Polly.Joanna")
# # #         response.redirect('/process_speech')
        
# # #     except Exception as e:
# # #         logger.error(f"{log_prefix} ❌ Error: {e}")
# # #         response.say("Technical difficulties.", voice="Polly.Joanna")
# # #         response.hangup()
    
# # #     return Response(content=str(response), media_type="application/xml")


# # # @app.post("/call_status")
# # # async def handle_call_status(request: Request):
# # #     form_data = await request.form()
# # #     call_sid = form_data.get("CallSid")
# # #     call_status = form_data.get("CallStatus")
# # #     call_duration = form_data.get("CallDuration", "0")
    
# # #     log_prefix = f"[{call_sid[:8]}]"
# # #     logger.info(f"{log_prefix} 📊 Status: {call_status}, Duration: {call_duration}s")
    
# # #     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
# # #         # 🤖 RUN AI EXTRACTION ON CALL END
# # #         if call_sid in conversations and conversations[call_sid]:
# # #             metadata = call_metadata.get(call_sid, {})
# # #             customer_info = metadata.get("customer_info")
            
# # #             # Prepare conversation for extraction
# # #             conv_exchanges = []
# # #             history = conversations[call_sid]
            
# # #             for i in range(0, len(history), 2):
# # #                 if i + 1 < len(history):
# # #                     conv_exchanges.append({
# # #                         "human": history[i]["content"],
# # #                         "agent": history[i + 1]["content"]
# # #                     })
            
# # #             # 🧠 EXTRACT INSIGHTS USING AI
# # #             logger.info(f"{log_prefix} 🤖 Running AI extraction...")
# # #             extraction_agent.analyze_and_store(
# # #                 call_id=call_sid,
# # #                 conversation_exchanges=conv_exchanges,
# # #                 customer_context=customer_info
# # #             )
        
# # #         # Cleanup
# # #         conversations.pop(call_sid, None)
# # #         call_metadata.pop(call_sid, None)
# # #         logger.info(f"{log_prefix} 🧹 Cleaned up")
    
# # #     return Response(content="OK")


# # # @app.get("/health")
# # # async def health_check():
# # #     return {
# # #         "status": "running",
# # #         "service": "JIT Debt Collection with AI Extraction",
# # #         "model": "Amazon Nova Pro v1.0",
# # #         "active_calls": len(conversations)
# # #     }


# # # @app.get("/")
# # # async def root():
# # #     return {
# # #         "status": "running",
# # #         "service": "JIT Debt Collection Agent with AI Extraction",
# # #         "version": "7.0-AI-EXTRACTION",
# # #         "features": ["Nova Pro AI", "DynamoDB Logging", "Intelligent Extraction"],
# # #         "endpoints": {
# # #             "/voice": "Call handler",
# # #             "/process_speech": "Speech processing",
# # #             "/call_status": "Status webhook (triggers AI extraction)",
# # #             "/health": "Health check"
# # #         }
# # #     }


# # # if __name__ == "__main__":
# # #     import uvicorn
# # #     logger.info("🚀" * 40)
# # #     logger.info("🚀 JIT DEBT COLLECTION WITH AI EXTRACTION")
# # #     logger.info(f"🚀 AI Model: Amazon Nova Pro v1.0")
# # #     logger.info(f"🚀 Bedrock: {REGION}")
# # #     logger.info(f"🚀 DynamoDB: {DYNAMODB_TABLE} in {DYNAMODB_REGION}")
# # #     logger.info("🚀 Features: Intelligent conversation extraction")
# # #     logger.info("🚀" * 40)
    
# # #     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")






# # import re
# # import logging
# # import json
# # import asyncio
# # import boto3
# # from fastapi import FastAPI, Request, Form
# # from fastapi.responses import Response, JSONResponse
# # from twilio.twiml.voice_response import VoiceResponse, Gather
# # import time
# # from datetime import datetime
# # from typing import Dict, Optional, List
# # from decimal import Decimal

# # # Setup comprehensive logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format='%(asctime)s | %(levelname)s | %(message)s',
# #     datefmt='%Y-%m-%d %H:%M:%S'
# # )
# # logger = logging.getLogger(__name__)

# # REGION = "us-east-1"
# # DYNAMODB_REGION = "ap-south-1"
# # DYNAMODB_TABLE = "call_logs"

# # bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# # polly = boto3.client("polly", region_name=REGION)

# # app = FastAPI()

# # conversations = {}
# # call_metadata = {}


# # # ----------------------------------------------------------------
# # # 🤖 AI EXTRACTION AGENT
# # # ----------------------------------------------------------------

# # class ConversationExtractionAgent:
# #     """AI-powered extraction agent using Nova Pro"""
    
# #     def __init__(self, bedrock_region: str, dynamodb_region: str, table_name: str):
# #         self.bedrock = boto3.client("bedrock-runtime", region_name=bedrock_region)
# #         self.dynamodb = boto3.resource("dynamodb", region_name=dynamodb_region)
# #         self.table = self.dynamodb.Table(table_name)
# #         logger.info(f"🤖 AI Extraction Agent initialized")
    
# #     def _convert_floats_to_decimal(self, obj):
# #         if isinstance(obj, float):
# #             return Decimal(str(obj))
# #         elif isinstance(obj, dict):
# #             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
# #         elif isinstance(obj, list):
# #             return [self._convert_floats_to_decimal(item) for item in obj]
# #         return obj
    
# #     def _call_nova_pro_for_extraction(self, conversation_text: str) -> Dict:
# #         """Use Nova Pro to extract structured insights"""
# #         try:
# #             system_prompt = """You are an AI extraction specialist analyzing debt collection conversations.
# # Respond ONLY with valid JSON. No markdown, no preamble, just pure JSON."""

# #             extraction_instructions = """
# # Extract this information from the conversation:

# # {
# #     "customer_name": "name or null",
# #     "phone_number": "phone or null",
# #     "invoice_number": "invoice or null",
# #     "product_name": "product or null",
# #     "amount_due": number or null,
# #     "due_date": "YYYY-MM-DD or null",
# #     "days_overdue": number or null,
# #     "payment_commitment_date": "YYYY-MM-DD if customer committed, or null",
# #     "payment_commitment_amount": number or null,
# #     "customer_intent": "willing_to_pay/needs_time/financial_difficulty/disputing/uncooperative or null",
# #     "call_outcome": "payment_committed/follow_up_needed/dispute_raised/disconnected/no_resolution",
# #     "customer_reason_for_delay": "brief reason or null",
# #     "next_follow_up_date": "YYYY-MM-DD or null",
# #     "customer_sentiment": "cooperative/neutral/frustrated/angry or null",
# #     "call_summary": "2-3 sentence summary"
# # }
# # """

# #             full_prompt = f"""{system_prompt}

# # CONVERSATION:
# # {conversation_text}

# # {extraction_instructions}

# # Respond with ONLY the JSON object:"""

# #             messages = [{"role": "user", "content": [{"text": full_prompt}]}]
            
# #             request_body = {
# #                 "messages": messages,
# #                 "inferenceConfig": {
# #                     "temperature": 0.1,
# #                     "max_new_tokens": 500,
# #                     "top_p": 0.9
# #                 }
# #             }
            
# #             logger.info("🧠 Extracting insights with Nova Pro...")
# #             response = self.bedrock.invoke_model(
# #                 modelId="amazon.nova-pro-v1:0",
# #                 body=json.dumps(request_body),
# #                 contentType="application/json",
# #                 accept="application/json"
# #             )
            
# #             response_body = json.loads(response["body"].read())
# #             extracted_text = response_body["output"]["message"]["content"][0]["text"].strip()
            
# #             # Clean markdown formatting
# #             extracted_text = re.sub(r'^```json\s*', '', extracted_text)
# #             extracted_text = re.sub(r'\s*```$', '', extracted_text)
# #             extracted_text = extracted_text.strip()
            
# #             extracted_data = json.loads(extracted_text)
# #             logger.info("✅ Extraction successful")
            
# #             return extracted_data
            
# #         except Exception as e:
# #             logger.error(f"❌ Extraction failed: {e}")
# #             return {}
    
# #     def analyze_and_store(
# #         self,
# #         call_id: str,
# #         conversation_exchanges: List[Dict],
# #         customer_context: Optional[Dict] = None
# #     ) -> Dict:
# #         """Analyze conversation and store extracted insights"""
# #         try:
# #             logger.info("=" * 80)
# #             logger.info(f"🔍 ANALYZING CONVERSATION: {call_id[:12]}...")
# #             logger.info(f"📊 Total Exchanges: {len(conversation_exchanges)}")
# #             logger.info("=" * 80)
            
# #             # Build conversation text
# #             conv_lines = []
# #             for idx, ex in enumerate(conversation_exchanges, 1):
# #                 human = ex.get('human', ex.get('human_message', ''))
# #                 agent = ex.get('agent', ex.get('agent_response', ''))
# #                 conv_lines.append(f"Turn {idx}:")
# #                 conv_lines.append(f"HUMAN: {human}")
# #                 conv_lines.append(f"AGENT: {agent}")
# #                 conv_lines.append("")
            
# #             conversation_text = "\n".join(conv_lines)
# #             logger.info(f"📝 Conversation text prepared ({len(conversation_text)} chars)")
            
# #             # Extract using Nova Pro
# #             extracted = self._call_nova_pro_for_extraction(conversation_text)
            
# #             if not extracted:
# #                 logger.warning("⚠️  Extraction returned empty")
# #                 return {}
            
# #             # Merge with customer context
# #             if customer_context:
# #                 extracted['customer_name'] = extracted.get('customer_name') or customer_context.get('name')
# #                 extracted['phone_number'] = extracted.get('phone_number') or customer_context.get('phone_number')
# #                 extracted['invoice_number'] = extracted.get('invoice_number') or customer_context.get('invoice_number')
# #                 extracted['amount_due'] = extracted.get('amount_due') or customer_context.get('due_amount')
# #                 extracted['due_date'] = extracted.get('due_date') or customer_context.get('due_date')
# #                 extracted['days_overdue'] = extracted.get('days_overdue') or customer_context.get('days_overdue')
# #                 extracted['customer_id'] = customer_context.get('customer_id')
# #                 extracted['product_name'] = extracted.get('product_name') or customer_context.get('product_name')
            
# #             # Determine status
# #             status = self._determine_status(extracted)
            
# #             # Store to DynamoDB
# #             item = {
# #                 "call_id": call_id,
# #                 "invoice_number": extracted.get('invoice_number', 'UNKNOWN'),
# #                 "timestamp": datetime.utcnow().isoformat(),
# #                 "record_type": "EXTRACTED_INSIGHTS",
# #                 "customer_name": extracted.get('customer_name'),
# #                 "customer_id": extracted.get('customer_id'),
# #                 "phone_number": extracted.get('phone_number'),
# #                 "product_name": extracted.get('product_name'),
# #                 "amount_due": self._convert_floats_to_decimal(extracted.get('amount_due')),
# #                 "due_date": extracted.get('due_date'),
# #                 "days_overdue": extracted.get('days_overdue'),
# #                 "payment_commitment_date": extracted.get('payment_commitment_date'),
# #                 "payment_commitment_amount": self._convert_floats_to_decimal(extracted.get('payment_commitment_amount')),
# #                 "next_follow_up_date": extracted.get('next_follow_up_date'),
# #                 "call_outcome": extracted.get('call_outcome'),
# #                 "customer_intent": extracted.get('customer_intent'),
# #                 "customer_reason_for_delay": extracted.get('customer_reason_for_delay'),
# #                 "customer_sentiment": extracted.get('customer_sentiment'),
# #                 "call_summary": extracted.get('call_summary'),
# #                 "status": status,
# #                 "total_conversation_turns": len(conversation_exchanges)
# #             }
            
# #             # Remove None values
# #             item = {k: v for k, v in item.items() if v is not None}
            
# #             self.table.put_item(Item=item)
            
# #             logger.info("=" * 80)
# #             logger.info("💾 EXTRACTION RESULTS STORED")
# #             logger.info(f"✅ Status: {status}")
# #             logger.info(f"✅ Outcome: {item.get('call_outcome')}")
# #             logger.info(f"✅ Intent: {item.get('customer_intent')}")
# #             logger.info(f"✅ Commitment Date: {item.get('payment_commitment_date')}")
# #             logger.info(f"✅ Summary: {item.get('call_summary', '')[:100]}...")
# #             logger.info("=" * 80)
            
# #             return extracted
            
# #         except Exception as e:
# #             logger.error(f"❌ Analysis failed: {e}", exc_info=True)
# #             return {}
    
# #     def _determine_status(self, data: Dict) -> str:
# #         """Determine status from extracted data"""
# #         outcome = data.get('call_outcome', '').lower()
# #         intent = data.get('customer_intent', '').lower()
# #         has_commitment = bool(data.get('payment_commitment_date'))
        
# #         if has_commitment or 'payment_committed' in outcome:
# #             return "COMMITTED"
# #         elif 'dispute' in outcome or 'disputing' in intent:
# #             return "DISPUTED"
# #         elif 'follow_up' in outcome:
# #             return "FOLLOW_UP_REQUIRED"
# #         elif 'uncooperative' in intent or 'disconnected' in outcome:
# #             return "UNCOOPERATIVE"
# #         elif 'willing_to_pay' in intent or 'needs_time' in intent:
# #             return "PENDING"
# #         else:
# #             return "NEEDS_REVIEW"


# # # Initialize extraction agent
# # extraction_agent = ConversationExtractionAgent(
# #     bedrock_region=REGION,
# #     dynamodb_region=DYNAMODB_REGION,
# #     table_name=DYNAMODB_TABLE
# # )


# # # ----------------------------------------------------------------
# # # 📊 BASIC CONVERSATION LOGGER
# # # ----------------------------------------------------------------

# # class ConversationLogger:
# #     """Basic logger for conversation turns"""
    
# #     def __init__(self, region: str, table_name: str):
# #         self.dynamodb = boto3.resource("dynamodb", region_name=region)
# #         self.table = self.dynamodb.Table(table_name)
# #         logger.info(f"📊 Conversation Logger initialized")
    
# #     def _convert_floats_to_decimal(self, obj):
# #         if isinstance(obj, float):
# #             return Decimal(str(obj))
# #         elif isinstance(obj, dict):
# #             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
# #         return obj
    
# #     def log_call_start(self, call_sid: str, phone_number: str, customer_info: Dict) -> bool:
# #         try:
# #             item = {
# #                 "call_id": call_sid,
# #                 "record_type": "CALL_START",
# #                 "timestamp": datetime.utcnow().isoformat(),
# #                 "phone_number": phone_number,
# #                 "customer_name": customer_info.get("name"),
# #                 "invoice_number": customer_info.get("invoice_number"),
# #                 "amount_due": self._convert_floats_to_decimal(customer_info.get("due_amount")),
# #                 "call_status": "INITIATED"
# #             }
# #             item = {k: v for k, v in item.items() if v is not None}
# #             self.table.put_item(Item=item)
# #             logger.info(f"💾 Call start logged")
# #             return True
# #         except Exception as e:
# #             logger.error(f"❌ Failed to log call start: {e}")
# #             return False
    
# #     def log_conversation_turn(
# #         self, call_sid: str, turn_number: int, human_message: str,
# #         agent_response: str, confidence: Optional[float] = None,
# #         customer_info: Optional[Dict] = None
# #     ) -> bool:
# #         try:
# #             item = {
# #                 "call_id": call_sid,
# #                 "turn_id": f"{call_sid}#{turn_number}",
# #                 "record_type": "CONVERSATION_TURN",
# #                 "timestamp": datetime.utcnow().isoformat(),
# #                 "turn_number": turn_number,
# #                 "human_message": human_message,
# #                 "agent_response": agent_response
# #             }
            
# #             if confidence:
# #                 item["confidence_score"] = self._convert_floats_to_decimal(confidence)
# #             if customer_info:
# #                 item["customer_name"] = customer_info.get("name")
# #                 item["invoice_number"] = customer_info.get("invoice_number")
            
# #             item = {k: v for k, v in item.items() if v is not None}
# #             self.table.put_item(Item=item)
# #             logger.info(f"💾 Turn #{turn_number} logged")
# #             return True
# #         except Exception as e:
# #             logger.error(f"❌ Failed to log turn: {e}")
# #             return False


# # db_logger = ConversationLogger(region=DYNAMODB_REGION, table_name=DYNAMODB_TABLE)


# # # ----------------------------------------------------------------
# # # 📞 CUSTOMER DATA
# # # ----------------------------------------------------------------

# # CUSTOMER_INFO = {
# #     "customer_id": "CUST001",
# #     "name": "Praveen Kumar",
# #     "phone_number": "+916385740104",
# #     "product_name": "Dell Inspiron 15 Laptop",
# #     "order_date": "2024-09-10",
# #     "purchase_date": "2024-09-12",
# #     "total_amount": 8000.00,
# #     "advance_amount": 3000.00,
# #     "total_paid": 3000.00,
# #     "due_amount": 5000.00,
# #     "due_date": "2024-10-15",
# #     "days_overdue": 22,
# #     "invoice_number": "INV-2024-1015",
# #     "last_payment_amount": 3000.00,
# #     "last_payment_date": "2024-09-20"
# # }


# # def get_customer_info(phone_number: str) -> Dict:
# #     logger.info(f"🔍 Call from: {phone_number}")
# #     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']}")
# #     return CUSTOMER_INFO


# # def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
# #     base_context = f"""You are kiwi, a polite debt collection agent from JIT Global Financial Services.

# # CUSTOMER DETAILS:
# # - Name: {customer['name']}
# # - Product: {customer['product_name']}
# # - Total Amount: ₹{customer['total_amount']:,.2f}
# # - Amount Due: ₹{customer['due_amount']:,.2f}
# # - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# # - Invoice: {customer['invoice_number']}

# # CONVERSATION STYLE:
# # - Be polite and respectful
# # - Keep responses 7-25 words
# # - Show empathy
# # - Never be aggressive"""

# #     if is_first_message:
# #         return f"""{base_context}

# # This is your FIRST message. Mention product, invoice, amount due, due date, and ask reason for delay.
# # Keep it 20-30 words."""
    
# #     return f"""{base_context}

# # Respond naturally to customer. Keep it 7-25 words."""


# # async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
# #     start_time = time.time()
# #     log_prefix = f"[{conversation_id[:8]}]"
    
# #     try:
# #         if conversation_id not in conversations:
# #             conversations[conversation_id] = []

# #         history = conversations[conversation_id]
# #         is_first_message = len(history) == 0

# #         system_prompt = build_system_prompt(customer_info, is_first_message)
# #         messages = []

# #         for msg in history[-8:]:
# #             messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

# #         if is_first_message:
# #             current_text = f"""Customer said: "{user_input}"

# # First message: Include product ({customer_info['product_name']}), invoice ({customer_info['invoice_number']}), amount (₹{customer_info['due_amount']:,.2f}), due date ({customer_info['due_date']}), and ask why delay. 20-30 words.

# # Your response:"""
# #         else:
# #             current_text = f"""Customer said: "{user_input}"

# # Respond politely in 7-25 words."""

# #         messages.append({"role": "user", "content": [{"text": f"{system_prompt}\n\n{current_text}"}]})

# #         request_body = {
# #             "messages": messages,
# #             "inferenceConfig": {"temperature": 0.7, "max_new_tokens": 120, "top_p": 0.9}
# #         }

# #         response = bedrock.invoke_model(
# #             modelId="amazon.nova-pro-v1:0",
# #             body=json.dumps(request_body),
# #             contentType="application/json",
# #             accept="application/json"
# #         )

# #         response_body = json.loads(response["body"].read())
# #         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()
# #         ai_response = re.sub(r'^(Agent|Assistant|kiwi):\s*', '', ai_response, flags=re.IGNORECASE)
# #         ai_response = ai_response.split("Customer:")[0].strip().strip('"\'')

# #         history.extend([
# #             {"role": "user", "content": user_input},
# #             {"role": "assistant", "content": ai_response}
# #         ])

# #         logger.info(f"{log_prefix} 💬 AI response: '{ai_response}'")
# #         return ai_response

# #     except Exception as e:
# #         logger.error(f"{log_prefix} ❌ AI error: {e}")
# #         return "I'm sorry, could you please repeat that?"


# # @app.post("/voice")
# # async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
# #     logger.info("=" * 80)
# #     logger.info(f"📞 CALL: {CallSid} from {From}")
# #     logger.info("=" * 80)
    
# #     response = VoiceResponse()
    
# #     try:
# #         customer_info = get_customer_info(From)
        
# #         db_logger.log_call_start(CallSid, From, customer_info)
        
# #         call_metadata[CallSid] = {
# #             "customer_info": customer_info,
# #             "call_start": datetime.now(),
# #             "interaction_count": 0
# #         }
        
# #         greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi from J I T Global Financial Services."
# #         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
# #         gather = Gather(
# #             input='speech', action='/process_speech', method='POST',
# #             speechTimeout=2, timeout=5, language='en-US', enhanced=True
# #         )
# #         response.append(gather)
# #         response.redirect('/voice')
        
# #     except Exception as e:
# #         logger.error(f"❌ Error: {e}")
# #         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
# #         response.hangup()
    
# #     return Response(content=str(response), media_type="application/xml")


# # @app.post("/process_speech")
# # async def process_speech(
# #     request: Request, SpeechResult: str = Form(None),
# #     CallSid: str = Form(...), Confidence: str = Form("0.0")
# # ):
# #     log_prefix = f"[{CallSid[:8]}]"
# #     logger.info(f"{log_prefix} 🎤 Input: '{SpeechResult}' (Confidence: {Confidence})")
    
# #     response = VoiceResponse()
# #     confidence = float(Confidence) if Confidence else 0.0
    
# #     if confidence < 0.5:
# #         response.say("I'm sorry, could you repeat?", voice="Polly.Joanna")
# #         gather = Gather(input='speech', action='/process_speech', method='POST',
# #                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
# #         response.append(gather)
# #         return Response(content=str(response), media_type="application/xml")

# #     # TRIGGER EXTRACTION WHEN CALL ENDS (silence detected)
# #     # In /process_speech endpoint - replace this condition:
# #     if not SpeechResult or SpeechResult.strip() == "" or SpeechResult.lower() == "none":
# #         logger.info(f"{log_prefix} 🔚 Call ending - triggering AI extraction...")
        
# #         # Run extraction before ending call
# #         if CallSid in conversations and conversations[CallSid]:
# #             try:
# #                 metadata = call_metadata.get(CallSid, {})
# #                 customer_info = metadata.get("customer_info")
                
# #                 # Prepare conversation for extraction
# #                 conv_exchanges = []
# #                 history = conversations[CallSid]
                
# #                 for i in range(0, len(history), 2):
# #                     if i + 1 < len(history):
# #                         conv_exchanges.append({
# #                             "human": history[i]["content"],
# #                             "agent": history[i + 1]["content"]
# #                         })
                
# #                 # 🧠 EXTRACT INSIGHTS USING AI
# #                 if conv_exchanges:
# #                     extraction_agent.analyze_and_store(
# #                         call_id=CallSid,
# #                         conversation_exchanges=conv_exchanges,
# #                         customer_context=customer_info
# #                     )
# #             except Exception as e:
# #                 logger.error(f"❌ Extraction error: {e}")
# #     # if not SpeechResult or SpeechResult.strip() == "" or SpeechResult == "None":
# #     #     logger.info(f"{log_prefix} 🔚 Call ending - triggering AI extraction...")
        
# #         # Run extraction before ending call
# #         if CallSid in conversations and conversations[CallSid]:
# #             try:
# #                 metadata = call_metadata.get(CallSid, {})
# #                 customer_info = metadata.get("customer_info")
                
# #                 # Prepare conversation for extraction
# #                 conv_exchanges = []
# #                 history = conversations[CallSid]
                
# #                 for i in range(0, len(history), 2):
# #                     if i + 1 < len(history):
# #                         conv_exchanges.append({
# #                             "human": history[i]["content"],
# #                             "agent": history[i + 1]["content"]
# #                         })
                
# #                 # 🧠 EXTRACT INSIGHTS USING AI
# #                 if conv_exchanges:
# #                     extraction_agent.analyze_and_store(
# #                         call_id=CallSid,
# #                         conversation_exchanges=conv_exchanges,
# #                         customer_context=customer_info
# #                     )
# #             except Exception as e:
# #                 logger.error(f"❌ Extraction error: {e}")
        
# #         # Cleanup
# #         conversations.pop(CallSid, None)
# #         call_metadata.pop(CallSid, None)
        
# #         response.say("Thank you for your time. Goodbye.", voice="Polly.Joanna")
# #         response.hangup()
# #         return Response(content=str(response), media_type="application/xml")
    
# #     try:
# #         if CallSid not in call_metadata:
# #             response.say("Session error. Please call again.", voice="Polly.Joanna")
# #             response.hangup()
# #             return Response(content=str(response), media_type="application/xml")
        
# #         customer_info = call_metadata[CallSid]["customer_info"]
# #         call_metadata[CallSid]["interaction_count"] += 1
# #         interaction_num = call_metadata[CallSid]["interaction_count"]
        
# #         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
        
# #         db_logger.log_conversation_turn(
# #             CallSid, interaction_num, SpeechResult, ai_response, confidence, customer_info
# #         )
        
# #         response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
# #         gather = Gather(input='speech', action='/process_speech', method='POST',
# #                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
# #         response.append(gather)
# #         response.say("Are you still there?", voice="Polly.Joanna")
# #         response.redirect('/process_speech')
        
# #     except Exception as e:
# #         logger.error(f"{log_prefix} ❌ Error: {e}")
# #         response.say("Technical difficulties.", voice="Polly.Joanna")
# #         response.hangup()
    
# #     return Response(content=str(response), media_type="application/xml")


# # @app.post("/call_status")
# # async def handle_call_status(request: Request):
# #     """Twilio webhook for call status updates"""
# #     form_data = await request.form()
# #     call_sid = form_data.get("CallSid")
# #     call_status = form_data.get("CallStatus")
# #     call_duration = form_data.get("CallDuration", "0")
    
# #     log_prefix = f"[{call_sid[:8]}]"
# #     logger.info("=" * 80)
# #     logger.info(f"{log_prefix} 📊 CALL STATUS: {call_status}, Duration: {call_duration}s")
# #     logger.info("=" * 80)
    
# #     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
# #         # 🤖 RUN AI EXTRACTION ON CALL END
# #         if call_sid in conversations and conversations[call_sid]:
# #             metadata = call_metadata.get(call_sid, {})
# #             customer_info = metadata.get("customer_info")
            
# #             # Prepare conversation for extraction
# #             conv_exchanges = []
# #             history = conversations[call_sid]
            
# #             for i in range(0, len(history), 2):
# #                 if i + 1 < len(history):
# #                     conv_exchanges.append({
# #                         "human": history[i]["content"],
# #                         "agent": history[i + 1]["content"]
# #                     })
            
# #             # 🧠 EXTRACT INSIGHTS USING AI
# #             if conv_exchanges:
# #                 logger.info(f"{log_prefix} 🤖 Running AI extraction...")
# #                 extraction_agent.analyze_and_store(
# #                     call_id=call_sid,
# #                     conversation_exchanges=conv_exchanges,
# #                     customer_context=customer_info
# #                 )
        
# #         # Cleanup
# #         conversations.pop(call_sid, None)
# #         call_metadata.pop(call_sid, None)
# #         logger.info(f"{log_prefix} 🧹 Cleaned up")
    
# #     return Response(content="OK")


# # # ----------------------------------------------------------------
# # # 🔧 MANUAL EXTRACTION ENDPOINT FOR TESTING
# # # ----------------------------------------------------------------

# # @app.post("/extract/{call_id}")
# # async def manual_extract(call_id: str):
# #     """
# #     Manually trigger extraction for a specific call ID.
# #     Useful for testing or re-processing calls.
    
# #     Example: POST http://localhost:8000/extract/CAa3cad35163616ad76e77e4614d5b4075
# #     """
# #     try:
# #         logger.info(f"🔧 Manual extraction requested for: {call_id}")
        
# #         if call_id not in conversations or not conversations[call_id]:
# #             return JSONResponse(
# #                 status_code=404,
# #                 content={"error": "Call not found or has no conversation data"}
# #             )
        
# #         metadata = call_metadata.get(call_id, {})
# #         customer_info = metadata.get("customer_info")
        
# #         # Prepare conversation
# #         conv_exchanges = []
# #         history = conversations[call_id]
        
# #         for i in range(0, len(history), 2):
# #             if i + 1 < len(history):
# #                 conv_exchanges.append({
# #                     "human": history[i]["content"],
# #                     "agent": history[i + 1]["content"]
# #                 })
        
# #         if not conv_exchanges:
# #             return JSONResponse(
# #                 status_code=400,
# #                 content={"error": "No conversation exchanges found"}
# #             )
        
# #         # Run extraction
# #         result = extraction_agent.analyze_and_store(
# #             call_id=call_id,
# #             conversation_exchanges=conv_exchanges,
# #             customer_context=customer_info
# #         )
        
# #         if result:
# #             return JSONResponse(content={
# #                 "success": True,
# #                 "call_id": call_id,
# #                 "extracted_data": result,
# #                 "message": "Extraction completed and stored in DynamoDB"
# #             })
# #         else:
# #             return JSONResponse(
# #                 status_code=500,
# #                 content={"error": "Extraction failed"}
# #             )
            
# #     except Exception as e:
# #         logger.error(f"❌ Manual extraction error: {e}")
# #         return JSONResponse(
# #             status_code=500,
# #             content={"error": str(e)}
# #         )


# # @app.get("/calls/active")
# # async def list_active_calls():
# #     """List all active calls with conversation data"""
# #     active = []
# #     for call_id, history in conversations.items():
# #         metadata = call_metadata.get(call_id, {})
# #         active.append({
# #             "call_id": call_id,
# #             "customer": metadata.get("customer_info", {}).get("name"),
# #             "turns": len(history) // 2,
# #             "start_time": metadata.get("call_start")
# #         })
    
# #     return JSONResponse(content={
# #         "active_calls": len(active),
# #         "calls": active
# #     })


# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "running",
# #         "service": "JIT Debt Collection with AI Extraction",
# #         "model": "Amazon Nova Pro v1.0",
# #         "active_calls": len(conversations),
# #         "extraction_enabled": True
# #     }


# # @app.get("/")
# # async def root():
# #     return {
# #         "status": "running",
# #         "service": "JIT Debt Collection Agent with AI Extraction",
# #         "version": "7.0-AI-EXTRACTION",
# #         "features": ["Nova Pro AI", "DynamoDB Logging", "Intelligent Extraction"],
# #         "endpoints": {
# #             "/voice": "Call handler",
# #             "/process_speech": "Speech processing (triggers extraction on silence)",
# #             "/call_status": "Status webhook (backup extraction trigger)",
# #             "/extract/{call_id}": "Manual extraction for specific call",
# #             "/calls/active": "List active calls",
# #             "/health": "Health check"
# #         }
# #     }


# # if __name__ == "__main__":
# #     import uvicorn
# #     logger.info("🚀" * 40)
# #     logger.info("🚀 JIT DEBT COLLECTION WITH AI EXTRACTION")
# #     logger.info(f"🚀 AI Model: Amazon Nova Pro v1.0")
# #     logger.info(f"🚀 Bedrock: {REGION}")
# #     logger.info(f"🚀 DynamoDB: {DYNAMODB_TABLE} in {DYNAMODB_REGION}")
# #     logger.info("🚀 Features: Auto-extraction on call end + manual endpoint")
# #     logger.info("🚀" * 40)
    
# #     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")












# import re
# import logging
# import json
# import asyncio
# import boto3
# from fastapi import FastAPI, Request, Form
# from fastapi.responses import Response, JSONResponse
# from twilio.twiml.voice_response import VoiceResponse, Gather
# import time
# from datetime import datetime
# from typing import Dict, Optional, List
# from decimal import Decimal

# # Setup comprehensive logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s | %(levelname)s | %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)

# REGION = "us-east-1"
# DYNAMODB_REGION = "ap-south-1"
# DYNAMODB_TABLE = "call_logs"

# bedrock = boto3.client("bedrock-runtime", region_name=REGION)
# polly = boto3.client("polly", region_name=REGION)

# app = FastAPI()

# conversations = {}
# call_metadata = {}


# # ----------------------------------------------------------------
# # 🤖 AI EXTRACTION AGENT (DYNAMIC)
# # ----------------------------------------------------------------

# class ConversationExtractionAgent:
#     """AI-powered extraction agent using Nova Pro"""
    
#     def __init__(self, bedrock_region: str, dynamodb_region: str, table_name: str):
#         self.bedrock = boto3.client("bedrock-runtime", region_name=bedrock_region)
#         self.dynamodb = boto3.resource("dynamodb", region_name=dynamodb_region)
#         self.table = self.dynamodb.Table(table_name)
#         logger.info(f"🤖 AI Extraction Agent initialized")
    
#     def _convert_floats_to_decimal(self, obj):
#         if isinstance(obj, float):
#             return Decimal(str(obj))
#         elif isinstance(obj, dict):
#             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [self._convert_floats_to_decimal(item) for item in obj]
#         return obj
    
#     def _call_nova_pro_for_extraction(self, conversation_text: str) -> Dict:
#         """Use Nova Pro to extract structured insights from ALL conversation turns"""
#         try:
#             system_prompt = """You are an AI extraction specialist analyzing debt collection conversations.
# Analyze the ENTIRE conversation from start to finish and extract key insights.
# Respond ONLY with valid JSON. No markdown, no preamble, just pure JSON."""

#             extraction_instructions = """
# Extract this information from the COMPLETE conversation:

# {
#     "customer_name": "name or null",
#     "phone_number": "phone or null", 
#     "invoice_number": "invoice or null",
#     "product_name": "product or null",
#     "amount_due": number or null,
#     "due_date": "YYYY-MM-DD or null",
#     "days_overdue": number or null,
#     "payment_commitment_date": "YYYY-MM-DD if customer committed, or null",
#     "payment_commitment_amount": number or null,
#     "customer_intent": "willing_to_pay/needs_time/financial_difficulty/disputing/uncooperative or null",
#     "call_outcome": "payment_committed/follow_up_needed/dispute_raised/disconnected/no_resolution",
#     "customer_reason_for_delay": "brief reason or null",
#     "next_follow_up_date": "YYYY-MM-DD or null",
#     "customer_sentiment": "cooperative/neutral/frustrated/angry or null",
#     "call_summary": "2-3 sentence summary of entire conversation",
#     "key_conversation_points": ["list of 3-5 key points discussed"],
#     "payment_plan_details": "details of any payment arrangement or null"
# }
# """

#             full_prompt = f"""{system_prompt}

# COMPLETE CONVERSATION:
# {conversation_text}

# {extraction_instructions}

# Respond with ONLY the JSON object:"""

#             messages = [{"role": "user", "content": [{"text": full_prompt}]}]
            
#             request_body = {
#                 "messages": messages,
#                 "inferenceConfig": {
#                     "temperature": 0.1,
#                     "max_new_tokens": 600,
#                     "top_p": 0.9
#                 }
#             }
            
#             logger.info("🧠 Extracting insights from complete conversation...")
#             response = self.bedrock.invoke_model(
#                 modelId="amazon.nova-pro-v1:0",
#                 body=json.dumps(request_body),
#                 contentType="application/json",
#                 accept="application/json"
#             )
            
#             response_body = json.loads(response["body"].read())
#             extracted_text = response_body["output"]["message"]["content"][0]["text"].strip()
            
#             # Clean markdown formatting
#             extracted_text = re.sub(r'^```json\s*', '', extracted_text)
#             extracted_text = re.sub(r'\s*```$', '', extracted_text)
#             extracted_text = extracted_text.strip()
            
#             extracted_data = json.loads(extracted_text)
#             logger.info("✅ Dynamic extraction successful")
            
#             return extracted_data
            
#         except Exception as e:
#             logger.error(f"❌ Extraction failed: {e}")
#             return {}
    
#     def analyze_and_store(
#         self,
#         call_id: str,
#         conversation_exchanges: List[Dict],
#         customer_context: Optional[Dict] = None
#     ) -> Dict:
#         """Dynamically analyze ALL conversation turns and store extracted insights"""
#         try:
#             logger.info("=" * 80)
#             logger.info(f"🔍 DYNAMIC ANALYSIS: {call_id[:12]}...")
#             logger.info(f"📊 Total Conversation Turns: {len(conversation_exchanges)}")
#             logger.info("=" * 80)
            
#             # Build complete conversation text with ALL turns
#             conv_lines = []
#             for idx, ex in enumerate(conversation_exchanges, 1):
#                 human = ex.get('human', ex.get('human_message', ''))
#                 agent = ex.get('agent', ex.get('agent_response', ''))
#                 conv_lines.append(f"TURN {idx}:")
#                 conv_lines.append(f"CUSTOMER: {human}")
#                 conv_lines.append(f"AGENT: {agent}")
#                 conv_lines.append("-" * 50)
            
#             conversation_text = "\n".join(conv_lines)
#             logger.info(f"📝 Complete conversation prepared ({len(conversation_text)} chars)")
#             logger.info(f"💬 First customer message: {conversation_exchanges[0].get('human', '')[:100]}...")
#             logger.info(f"💬 First agent response: {conversation_exchanges[0].get('agent', '')[:100]}...")
            
#             # Extract using Nova Pro from COMPLETE conversation
#             extracted = self._call_nova_pro_for_extraction(conversation_text)
            
#             if not extracted:
#                 logger.warning("⚠️  Extraction returned empty")
#                 return {}
            
#             # Dynamically merge with customer context (don't override AI findings)
#             if customer_context:
#                 # Only fill in missing fields, don't override AI extractions
#                 if not extracted.get('customer_name'):
#                     extracted['customer_name'] = customer_context.get('name')
#                 if not extracted.get('phone_number'):
#                     extracted['phone_number'] = customer_context.get('phone_number')
#                 if not extracted.get('invoice_number'):
#                     extracted['invoice_number'] = customer_context.get('invoice_number')
#                 if not extracted.get('product_name'):
#                     extracted['product_name'] = customer_context.get('product_name')
#                 if not extracted.get('amount_due'):
#                     extracted['amount_due'] = customer_context.get('due_amount')
#                 if not extracted.get('due_date'):
#                     extracted['due_date'] = customer_context.get('due_date')
#                 if not extracted.get('days_overdue'):
#                     extracted['days_overdue'] = customer_context.get('days_overdue')
                
#                 extracted['customer_id'] = customer_context.get('customer_id')
            
#             # Determine status based on extracted data
#             status = self._determine_status(extracted)
            
#             # Store comprehensive insights to DynamoDB
#             item = {
#                 "call_id": call_id,
#                 "invoice_number": extracted.get('invoice_number', 'UNKNOWN'),
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "record_type": "DYNAMIC_EXTRACTION",
#                 "customer_name": extracted.get('customer_name'),
#                 "customer_id": extracted.get('customer_id'),
#                 "phone_number": extracted.get('phone_number'),
#                 "product_name": extracted.get('product_name'),
#                 "amount_due": self._convert_floats_to_decimal(extracted.get('amount_due')),
#                 "due_date": extracted.get('due_date'),
#                 "days_overdue": extracted.get('days_overdue'),
#                 "payment_commitment_date": extracted.get('payment_commitment_date'),
#                 "payment_commitment_amount": self._convert_floats_to_decimal(extracted.get('payment_commitment_amount')),
#                 "next_follow_up_date": extracted.get('next_follow_up_date'),
#                 "call_outcome": extracted.get('call_outcome'),
#                 "customer_intent": extracted.get('customer_intent'),
#                 "customer_reason_for_delay": extracted.get('customer_reason_for_delay'),
#                 "customer_sentiment": extracted.get('customer_sentiment'),
#                 "call_summary": extracted.get('call_summary'),
#                 "key_conversation_points": extracted.get('key_conversation_points', []),
#                 "payment_plan_details": extracted.get('payment_plan_details'),
#                 "status": status,
#                 "total_conversation_turns": len(conversation_exchanges),
#                 "extraction_type": "DYNAMIC_FULL_CONVERSATION"
#             }
            
#             # Remove None values
#             item = {k: v for k, v in item.items() if v is not None}
            
#             self.table.put_item(Item=item)
            
#             logger.info("=" * 80)
#             logger.info("💾 DYNAMIC EXTRACTION RESULTS STORED")
#             logger.info(f"✅ Status: {status}")
#             logger.info(f"✅ Outcome: {item.get('call_outcome')}")
#             logger.info(f"✅ Intent: {item.get('customer_intent')}")
#             logger.info(f"✅ Commitment: {item.get('payment_commitment_date')}")
#             logger.info(f"✅ Sentiment: {item.get('customer_sentiment')}")
#             logger.info(f"✅ Key Points: {len(item.get('key_conversation_points', []))} identified")
#             logger.info(f"✅ Summary: {item.get('call_summary', '')[:120]}...")
#             logger.info("=" * 80)
            
#             return extracted
            
#         except Exception as e:
#             logger.error(f"❌ Dynamic analysis failed: {e}", exc_info=True)
#             return {}
    
#     def _determine_status(self, data: Dict) -> str:
#         """Dynamically determine status from extracted data"""
#         outcome = data.get('call_outcome', '').lower()
#         intent = data.get('customer_intent', '').lower()
#         has_commitment = bool(data.get('payment_commitment_date'))
#         sentiment = data.get('customer_sentiment', '').lower()
        
#         if has_commitment or 'payment_committed' in outcome:
#             return "COMMITTED"
#         elif 'dispute' in outcome or 'disputing' in intent:
#             return "DISPUTED"
#         elif 'follow_up' in outcome or 'needs_time' in intent:
#             return "FOLLOW_UP_REQUIRED"
#         elif 'uncooperative' in intent or 'disconnected' in outcome or 'angry' in sentiment:
#             return "UNCOOPERATIVE"
#         elif 'willing_to_pay' in intent or 'cooperative' in sentiment:
#             return "PENDING"
#         else:
#             return "NEEDS_REVIEW"


# # Initialize dynamic extraction agent
# extraction_agent = ConversationExtractionAgent(
#     bedrock_region=REGION,
#     dynamodb_region=DYNAMODB_REGION,
#     table_name=DYNAMODB_TABLE
# )


# # ----------------------------------------------------------------
# # 📊 CONVERSATION LOGGER
# # ----------------------------------------------------------------

# class ConversationLogger:
#     """Logger for conversation turns"""
    
#     def __init__(self, region: str, table_name: str):
#         self.dynamodb = boto3.resource("dynamodb", region_name=region)
#         self.table = self.dynamodb.Table(table_name)
#         logger.info(f"📊 Conversation Logger initialized")
    
#     def _convert_floats_to_decimal(self, obj):
#         if isinstance(obj, float):
#             return Decimal(str(obj))
#         elif isinstance(obj, dict):
#             return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
#         return obj
    
#     def log_call_start(self, call_sid: str, phone_number: str, customer_info: Dict) -> bool:
#         try:
#             item = {
#                 "call_id": call_sid,
#                 "record_type": "CALL_START",
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "phone_number": phone_number,
#                 "customer_name": customer_info.get("name"),
#                 "invoice_number": customer_info.get("invoice_number"),
#                 "amount_due": self._convert_floats_to_decimal(customer_info.get("due_amount")),
#                 "call_status": "INITIATED"
#             }
#             item = {k: v for k, v in item.items() if v is not None}
#             self.table.put_item(Item=item)
#             logger.info(f"💾 Call start logged")
#             return True
#         except Exception as e:
#             logger.error(f"❌ Failed to log call start: {e}")
#             return False
    
#     def log_conversation_turn(
#         self, call_sid: str, turn_number: int, human_message: str,
#         agent_response: str, confidence: Optional[float] = None,
#         customer_info: Optional[Dict] = None
#     ) -> bool:
#         try:
#             item = {
#                 "call_id": call_sid,
#                 "turn_id": f"{call_sid}#{turn_number}",
#                 "record_type": "CONVERSATION_TURN",
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "turn_number": turn_number,
#                 "human_message": human_message,
#                 "agent_response": agent_response
#             }
            
#             if confidence:
#                 item["confidence_score"] = self._convert_floats_to_decimal(confidence)
#             if customer_info:
#                 item["customer_name"] = customer_info.get("name")
#                 item["invoice_number"] = customer_info.get("invoice_number")
            
#             item = {k: v for k, v in item.items() if v is not None}
#             self.table.put_item(Item=item)
#             logger.info(f"💾 Turn #{turn_number} logged")
#             return True
#         except Exception as e:
#             logger.error(f"❌ Failed to log turn: {e}")
#             return False


# db_logger = ConversationLogger(region=DYNAMODB_REGION, table_name=DYNAMODB_TABLE)


# # ----------------------------------------------------------------
# # 📞 CUSTOMER DATA & AI RESPONSE
# # ----------------------------------------------------------------

# CUSTOMER_INFO = {
#     "customer_id": "CUST001",
#     "name": "Praveen Kumar",
#     "phone_number": "+916385740104",
#     "product_name": "Dell Inspiron 15 Laptop",
#     "order_date": "2024-09-10",
#     "purchase_date": "2024-09-12",
#     "total_amount": 8000.00,
#     "advance_amount": 3000.00,
#     "total_paid": 3000.00,
#     "due_amount": 5000.00,
#     "due_date": "2024-10-15",
#     "days_overdue": 22,
#     "invoice_number": "INV-2024-1015",
#     "last_payment_amount": 3000.00,
#     "last_payment_date": "2024-09-20"
# }


# def get_customer_info(phone_number: str) -> Dict:
#     logger.info(f"🔍 Call from: {phone_number}")
#     logger.info(f"✅ Customer: {CUSTOMER_INFO['name']}")
#     return CUSTOMER_INFO


# def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
#     base_context = f"""You are kiwi, a polite debt collection agent from JIT Global Financial Services.

# CUSTOMER DETAILS:
# - Name: {customer['name']}
# - Product: {customer['product_name']}
# - Total Amount: ₹{customer['total_amount']:,.2f}
# - Amount Due: ₹{customer['due_amount']:,.2f}
# - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# - Invoice: {customer['invoice_number']}

# CONVERSATION STYLE:
# - Be polite and respectful
# - Keep responses 7-25 words
# - Show empathy
# - Never be aggressive"""

#     if is_first_message:
#         return f"""{base_context}

# This is your FIRST message. Mention product, invoice, amount due, due date, and ask reason for delay.
# Keep it 20-30 words."""
    
#     return f"""{base_context}

# Respond naturally to customer. Keep it 7-25 words."""


# async def get_ai_response(user_input: str, conversation_id: str, customer_info: Dict) -> str:
#     start_time = time.time()
#     log_prefix = f"[{conversation_id[:8]}]"
    
#     try:
#         if conversation_id not in conversations:
#             conversations[conversation_id] = []

#         history = conversations[conversation_id]
#         is_first_message = len(history) == 0

#         system_prompt = build_system_prompt(customer_info, is_first_message)
#         messages = []

#         for msg in history[-8:]:
#             messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

#         if is_first_message:
#             current_text = f"""Customer said: "{user_input}"

# First message: Include product ({customer_info['product_name']}), invoice ({customer_info['invoice_number']}), amount (₹{customer_info['due_amount']:,.2f}), due date ({customer_info['due_date']}), and ask why delay. 20-30 words.

# Your response:"""
#         else:
#             current_text = f"""Customer said: "{user_input}"

# Respond politely in 7-25 words."""

#         messages.append({"role": "user", "content": [{"text": f"{system_prompt}\n\n{current_text}"}]})

#         request_body = {
#             "messages": messages,
#             "inferenceConfig": {"temperature": 0.7, "max_new_tokens": 120, "top_p": 0.9}
#         }

#         response = bedrock.invoke_model(
#             modelId="amazon.nova-pro-v1:0",
#             body=json.dumps(request_body),
#             contentType="application/json",
#             accept="application/json"
#         )

#         response_body = json.loads(response["body"].read())
#         ai_response = response_body["output"]["message"]["content"][0]["text"].strip()
#         ai_response = re.sub(r'^(Agent|Assistant|kiwi):\s*', '', ai_response, flags=re.IGNORECASE)
#         ai_response = ai_response.split("Customer:")[0].strip().strip('"\'')

#         # Store both human and agent messages for dynamic extraction
#         history.extend([
#             {"role": "user", "content": user_input},
#             {"role": "assistant", "content": ai_response}
#         ])

#         logger.info(f"{log_prefix} 💬 AI response: '{ai_response}'")
#         return ai_response

#     except Exception as e:
#         logger.error(f"{log_prefix} ❌ AI error: {e}")
#         return "I'm sorry, could you please repeat that?"


# @app.post("/voice")
# async def handle_incoming_call(request: Request, From: str = Form(None), CallSid: str = Form(...)):
#     logger.info("=" * 80)
#     logger.info(f"📞 CALL: {CallSid} from {From}")
#     logger.info("=" * 80)
    
#     response = VoiceResponse()
    
#     try:
#         customer_info = get_customer_info(From)
        
#         db_logger.log_call_start(CallSid, From, customer_info)
        
#         call_metadata[CallSid] = {
#             "customer_info": customer_info,
#             "call_start": datetime.now(),
#             "interaction_count": 0
#         }
        
#         greeting = f"Hello, am I speaking with {customer_info['name']}? This is kiwi from J I T Global Financial Services."
#         response.say(greeting, voice="Polly.Joanna", language="en-US")
        
#         gather = Gather(
#             input='speech', action='/process_speech', method='POST',
#             speechTimeout=2, timeout=5, language='en-US', enhanced=True
#         )
#         response.append(gather)
#         response.redirect('/voice')
        
#     except Exception as e:
#         logger.error(f"❌ Error: {e}")
#         response.say("We're experiencing technical difficulties.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/process_speech")
# async def process_speech(
#     request: Request, SpeechResult: str = Form(None),
#     CallSid: str = Form(...), Confidence: str = Form("0.0")
# ):
#     log_prefix = f"[{CallSid[:8]}]"
#     logger.info(f"{log_prefix} 🎤 Input: '{SpeechResult}' (Confidence: {Confidence})")
    
#     response = VoiceResponse()
#     confidence = float(Confidence) if Confidence else 0.0
    
#     if confidence < 0.5:
#         response.say("I'm sorry, could you repeat?", voice="Polly.Joanna")
#         gather = Gather(input='speech', action='/process_speech', method='POST',
#                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
#         response.append(gather)
#         return Response(content=str(response), media_type="application/xml")

#     # TRIGGER DYNAMIC EXTRACTION WHEN CALL ENDS
#     if not SpeechResult or SpeechResult.strip() == "" or SpeechResult.lower() == "none":
#         logger.info(f"{log_prefix} 🔚 Call ending - triggering DYNAMIC AI extraction...")
        
#         # Run dynamic extraction before ending call
#         if CallSid in conversations and conversations[CallSid]:
#             try:
#                 metadata = call_metadata.get(CallSid, {})
#                 customer_info = metadata.get("customer_info")
                
#                 # Prepare ALL conversation exchanges for dynamic extraction
#                 conv_exchanges = []
#                 history = conversations[CallSid]
                
#                 # Process ALL conversation turns (both human and agent)
#                 for i in range(0, len(history), 2):
#                     if i + 1 < len(history):
#                         conv_exchanges.append({
#                             "human": history[i]["content"],  # Customer message
#                             "agent": history[i + 1]["content"]  # Agent response
#                         })
                
#                 # 🧠 DYNAMIC EXTRACTION FROM COMPLETE CONVERSATION
#                 if conv_exchanges:
#                     logger.info(f"{log_prefix} 🤖 Running DYNAMIC extraction on {len(conv_exchanges)} turns...")
#                     extraction_agent.analyze_and_store(
#                         call_id=CallSid,
#                         conversation_exchanges=conv_exchanges,
#                         customer_context=customer_info
#                     )
#                 else:
#                     logger.warning(f"{log_prefix} ⚠️ No conversation exchanges to extract")
                    
#             except Exception as e:
#                 logger.error(f"❌ Dynamic extraction error: {e}")
        
#         # Cleanup
#         conversations.pop(CallSid, None)
#         call_metadata.pop(CallSid, None)
        
#         response.say("Thank you for your time. Goodbye.", voice="Polly.Joanna")
#         response.hangup()
#         return Response(content=str(response), media_type="application/xml")
    
#     try:
#         if CallSid not in call_metadata:
#             response.say("Session error. Please call again.", voice="Polly.Joanna")
#             response.hangup()
#             return Response(content=str(response), media_type="application/xml")
        
#         customer_info = call_metadata[CallSid]["customer_info"]
#         call_metadata[CallSid]["interaction_count"] += 1
#         interaction_num = call_metadata[CallSid]["interaction_count"]
        
#         ai_response = await get_ai_response(SpeechResult, CallSid, customer_info)
        
#         db_logger.log_conversation_turn(
#             CallSid, interaction_num, SpeechResult, ai_response, confidence, customer_info
#         )
        
#         response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
#         gather = Gather(input='speech', action='/process_speech', method='POST',
#                        speechTimeout=2, timeout=10, language='en-US', enhanced=True)
#         response.append(gather)
#         response.say("Are you still there?", voice="Polly.Joanna")
#         response.redirect('/process_speech')
        
#     except Exception as e:
#         logger.error(f"{log_prefix} ❌ Error: {e}")
#         response.say("Technical difficulties.", voice="Polly.Joanna")
#         response.hangup()
    
#     return Response(content=str(response), media_type="application/xml")


# @app.post("/call_status")
# async def handle_call_status(request: Request):
#     """Twilio webhook for call status updates"""
#     form_data = await request.form()
#     call_sid = form_data.get("CallSid")
#     call_status = form_data.get("CallStatus")
#     call_duration = form_data.get("CallDuration", "0")
    
#     log_prefix = f"[{call_sid[:8]}]"
#     logger.info("=" * 80)
#     logger.info(f"{log_prefix} 📊 CALL STATUS: {call_status}, Duration: {call_duration}s")
#     logger.info("=" * 80)
    
#     if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
#         # 🤖 RUN DYNAMIC EXTRACTION ON CALL END (Backup)
#         if call_sid in conversations and conversations[call_sid]:
#             metadata = call_metadata.get(call_sid, {})
#             customer_info = metadata.get("customer_info")
            
#             # Prepare ALL conversation exchanges
#             conv_exchanges = []
#             history = conversations[call_sid]
            
#             for i in range(0, len(history), 2):
#                 if i + 1 < len(history):
#                     conv_exchanges.append({
#                         "human": history[i]["content"],
#                         "agent": history[i + 1]["content"]
#                     })
            
#             # 🧠 DYNAMIC EXTRACTION FROM COMPLETE CONVERSATION
#             if conv_exchanges:
#                 logger.info(f"{log_prefix} 🤖 Running BACKUP dynamic extraction...")
#                 extraction_agent.analyze_and_store(
#                     call_id=call_sid,
#                     conversation_exchanges=conv_exchanges,
#                     customer_context=customer_info
#                 )
        
#         # Cleanup
#         conversations.pop(call_sid, None)
#         call_metadata.pop(call_sid, None)
#         logger.info(f"{log_prefix} 🧹 Cleaned up")
    
#     return Response(content="OK")


# # ----------------------------------------------------------------
# # 🔧 MANUAL DYNAMIC EXTRACTION ENDPOINT
# # ----------------------------------------------------------------

# @app.post("/extract/{call_id}")
# async def manual_extract(call_id: str):
#     """
#     Manually trigger DYNAMIC extraction for a specific call ID
#     """
#     try:
#         logger.info(f"🔧 Manual DYNAMIC extraction requested for: {call_id}")
        
#         if call_id not in conversations or not conversations[call_id]:
#             return JSONResponse(
#                 status_code=404,
#                 content={"error": "Call not found or has no conversation data"}
#             )
        
#         metadata = call_metadata.get(call_id, {})
#         customer_info = metadata.get("customer_info")
        
#         # Prepare ALL conversation exchanges
#         conv_exchanges = []
#         history = conversations[call_id]
        
#         for i in range(0, len(history), 2):
#             if i + 1 < len(history):
#                 conv_exchanges.append({
#                     "human": history[i]["content"],
#                     "agent": history[i + 1]["content"]
#                 })
        
#         if not conv_exchanges:
#             return JSONResponse(
#                 status_code=400,
#                 content={"error": "No conversation exchanges found"}
#             )
        
#         # Run dynamic extraction
#         result = extraction_agent.analyze_and_store(
#             call_id=call_id,
#             conversation_exchanges=conv_exchanges,
#             customer_context=customer_info
#         )
        
#         if result:
#             return JSONResponse(content={
#                 "success": True,
#                 "call_id": call_id,
#                 "extraction_type": "DYNAMIC_FULL_CONVERSATION",
#                 "total_turns_analyzed": len(conv_exchanges),
#                 "extracted_data": result,
#                 "message": "Dynamic extraction completed and stored in DynamoDB"
#             })
#         else:
#             return JSONResponse(
#                 status_code=500,
#                 content={"error": "Dynamic extraction failed"}
#             )
            
#     except Exception as e:
#         logger.error(f"❌ Manual dynamic extraction error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"error": str(e)}
#         )


# @app.get("/calls/active")
# async def list_active_calls():
#     """List all active calls with conversation data"""
#     active = []
#     for call_id, history in conversations.items():
#         metadata = call_metadata.get(call_id, {})
#         active.append({
#             "call_id": call_id,
#             "customer": metadata.get("customer_info", {}).get("name"),
#             "total_turns": len(history) // 2,
#             "start_time": metadata.get("call_start")
#         })
    
#     return JSONResponse(content={
#         "active_calls": len(active),
#         "calls": active
#     })


# @app.get("/health")
# async def health_check():
#     return {
#         "status": "running",
#         "service": "JIT Debt Collection with DYNAMIC AI Extraction",
#         "model": "Amazon Nova Pro v1.0",
#         "active_calls": len(conversations),
#         "extraction_type": "DYNAMIC_FULL_CONVERSATION",
#         "features": [
#             "Real-time conversation analysis",
#             "Dynamic intent detection", 
#             "Multi-turn extraction",
#             "Sentiment analysis",
#             "Payment commitment tracking"
#         ]
#     }


# @app.get("/")
# async def root():
#     return {
#         "status": "running",
#         "service": "JIT Debt Collection Agent with DYNAMIC AI Extraction",
#         "version": "8.0-DYNAMIC-EXTRACTION",
#         "extraction_method": "DYNAMIC_FULL_CONVERSATION_ANALYSIS",
#         "features": [
#             "Nova Pro AI for real-time analysis",
#             "DynamoDB for comprehensive logging", 
#             "Dynamic extraction from ALL conversation turns",
#             "Intelligent status determination",
#             "Multi-dimensional insights"
#         ],
#         "endpoints": {
#             "/voice": "Call handler",
#             "/process_speech": "Speech processing (triggers dynamic extraction)",
#             "/call_status": "Status webhook (backup extraction)",
#             "/extract/{call_id}": "Manual dynamic extraction",
#             "/calls/active": "List active calls",
#             "/health": "Health check"
#         }
#     }


# if __name__ == "__main__":
#     import uvicorn
#     logger.info("🚀" * 50)
#     logger.info("🚀 JIT DEBT COLLECTION WITH DYNAMIC AI EXTRACTION")
#     logger.info(f"🚀 AI Model: Amazon Nova Pro v1.0")
#     logger.info(f"🚀 Bedrock: {REGION}")
#     logger.info(f"🚀 DynamoDB: {DYNAMODB_TABLE} in {DYNAMODB_REGION}")
#     logger.info("🚀 Extraction: DYNAMIC - All conversation turns analyzed")
#     logger.info("🚀 Features: Real-time intent, sentiment, commitment detection")
#     logger.info("🚀" * 50)
    
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


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


# def build_system_prompt(customer: Dict, is_first_message: bool) -> str:
#     base_context = f"""You are kiwi, a polite debt collection agent from JIT Global Financial Services.

# CUSTOMER DETAILS:
# - Name: {customer['name']}
# - Product: {customer['product_name']}
# - Total Amount: ₹{customer['total_amount']:,.2f}
# - Amount Due: ₹{customer['due_amount']:,.2f}
# - Due Date: {customer['due_date']} ({customer['days_overdue']} days overdue)
# - Invoice: {customer['invoice_number']}

# CONVERSATION STYLE:
#  - Be polite, soft-spoken, and respectful at all times
#  - Show empathy and understanding
#  - Keep responses between 7-25 words
#  - Speak naturally like a caring professional
#  - Use warm, gentle language
#  - Never sound aggressive or demanding

#  CONVERSATION FLOW:
# 1. First, mention the overdue payment politely
#  2. Ask gently why they haven't paid yet
#  3. Listen to their reason with empathy



#  HANDLING CUSTOMER QUESTIONS:
# - If they ask about payment history: "Your last payment was ₹{customer['last_payment_amount']:,.2f} on {customer['last_payment_date']}. The current due is ₹{customer['due_amount']:,.2f}."
#  - If they ask about invoice: "The invoice number is {customer['invoice_number']}."
#  - If they ask about due date: "It was due on {customer['due_date']}, that's {customer['days_overdue']} days ago."
# - If they ask about customer ID: "Your customer ID is {customer['customer_id']}."
# - After answering any question, gently bring conversation back to payment

#  RESPONSE EXAMPLES:

#  ✅ GOOD: "Your last payment was three thousand rupees on September twentieth. The remaining five thousand is overdue."
#  ❌ BAD: "You must pay immediately."
# ❌ BAD: "Why are you delaying payment?"
#  ❌ BAD: Long, complex sentences

#  YOUR GOAL: to remind the due amount and due date while being respectful and understanding."""

# CONVERSATION IN PROGRESS: Respond naturally and politely to what the customer just said.
#  - If they ask about payment history or transactions, provide the information clearly
#  - If they give an excuse, show understanding 
#  - If they say "tomorrow" or "soon", politely ask for the specific date (like November 8th)
#  - speak like a humble person 
#  - Always be respectful and soft-spoken

# Keep responses between 7-25 words."""

#     if is_first_message:
#         return f"""{base_context}

# This is your FIRST message. Mention product, invoice, amount due, due date, and ask reason for delay.
# Keep it 20-30 words."""
    
#     return f"""{base_context}

# Respond naturally to customer. Keep it 7-25 words."""


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