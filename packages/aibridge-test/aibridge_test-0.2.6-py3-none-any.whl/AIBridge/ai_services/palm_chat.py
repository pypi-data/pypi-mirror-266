import time
import uuid
from AIBridge.exceptions import PalmTextException, AIBridgeException
from AIBridge.ai_services.ai_abstraction import AIInterface
import json
from AIBridge.constant.common import parse_fromat, parse_api_key
import google.generativeai as palm


class PalmChat(AIInterface):
    """
    Base class for PalmChat's Services
    """

    @classmethod
    def generate(
        self,
        messages: str,
        context: str = "",
        examples: list[str] = [],
        model="models/chat-bison-001",
        variation_count: int = 1,
        temperature: float = 0.5,
        message_queue=False,
        api_key=None,
    ):
        try:
            if message_queue:
                id = uuid.uuid4()
                message_data = {
                    "id": str(id),
                    "messages": messages,
                    "context": context,
                    "examples": examples,
                    "model": model,
                    "variation_count": variation_count,
                    "temperature": temperature,
                    "ai_service": "palm_chat",
                    "api_key": api_key,
                }
                message = {"data": json.dumps(message_data)}
                from AIBridge.queue_integration.message_queue import MessageQ

                MessageQ.mq_enque(message=message)
                return {"response_id": str(id)}
            return self.get_response(
                messages,
                context,
                examples,
                model,
                variation_count,
                temperature,
                api_key=api_key,
            )
        except AIBridgeException as e:
            raise PalmTextException(f"Error in generating AI data {e}")

    @classmethod
    def get_response(
        self,
        messages,
        context,
        examples,
        model="models/chat-bison-001",
        variation_count=1,
        temperature=0.5,
        api_key=None,
    ):
        try:
            api_key = api_key if api_key else parse_api_key("palm_api")
            palm.configure(api_key=api_key)
            response = palm.chat(
                model=model,
                context=context,
                examples=examples,
                messages=messages,
                candidate_count=variation_count,
            )
            message_value = {
                "items": {
                    "response": {
                        "messages": response.messages,
                        "candiates": response.candidates,
                    },
                    "created_at": time.time(),
                    "token_used": None,
                    "ai_service": "palm_chat",
                }
            }
            return message_value
        except AIBridgeException as e:
            raise PalmTextException(f"{e}")
