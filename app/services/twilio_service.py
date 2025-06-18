from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.core.config import settings
from typing import Dict, Any
import json

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    def initiate_call(self, to_number: str, interview_id: str) -> Dict[str, Any]:
        """
        Initiate a call to the candidate
        """
        try:
            webhook_url = f"{settings.PUBLIC_BASE_URL}/api/v1/interviews/{interview_id}/twiml"
            status_callback_url = f"{settings.PUBLIC_BASE_URL}/api/v1/interviews/{interview_id}/status"
            
            print(f"DEBUG: Initiating call to {to_number}")
            print(f"DEBUG: Webhook URL: {webhook_url}")
            print(f"DEBUG: Status callback URL: {status_callback_url}")
            print(f"DEBUG: From number: {self.phone_number}")
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=webhook_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            print(f"DEBUG: Call created successfully. SID: {call.sid}, Status: {call.status}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status
            }
        except Exception as e:
            print(f"DEBUG: Error creating call: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def generate_twiml(self, questions: list, current_question_index: int = 0) -> str:
        """
        Generate TwiML for the interview
        """
        response = VoiceResponse()
        
        if current_question_index < len(questions):
            question = questions[current_question_index]
            
            # Add the question
            gather = Gather(
                input='speech',
                action=f'/interview/response/{current_question_index}',
                method='POST',
                speech_timeout='auto',
                language='en-US'
            )
            gather.say(question['question'], voice='Polly.Amy')
            response.append(gather)
            
            # If no input is received, repeat the question
            response.say("I didn't catch that. Let me repeat the question.", voice='Polly.Amy')
            response.redirect(f'/interview/question/{current_question_index}')
        else:
            # End of interview
            response.say("Thank you for completing the interview. We will review your responses and get back to you soon.", voice='Polly.Amy')
            response.hangup()
        
        return str(response)

    def handle_call_status(self, call_sid: str, call_status: str) -> Dict[str, Any]:
        """
        Handle call status updates
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def end_call(self, call_sid: str) -> Dict[str, Any]:
        """
        End an active call
        """
        try:
            call = self.client.calls(call_sid).update(status="completed")
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 