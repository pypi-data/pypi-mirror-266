from AIBridge.ai_services.cohere_llm import CohereApi
from AIBridge.ai_services.palm_chat import PalmChat
from AIBridge.ai_services.palm_text import PalmText
from AIBridge.queue_integration.response_class import (
    OpenAiImageRes,
    PalmTextRes,
    OpenAiRes,
    PalmChatRes,
    StableDuffusionRes,
    CohereRes,
    JarasicTextRes,
    GeminiAiRes,
    AnthropicRes,
)
from AIBridge.ai_services.openai_images import OpenAIImage
from AIBridge.ai_services.stable_diffusion_image import StableDiffusion
from AIBridge.exceptions import ProcessMQException
from AIBridge.ai_services.ai21labs_text import JurasicText
from AIBridge.ai_services.geminin_services import GeminiAIService
from AIBridge.ai_services.anthropic_ai import AnthropicService


class ProcessMQ:
    @classmethod
    def get_process_mq(self, process_name):
        from AIBridge.ai_services.openai_services import OpenAIService

        process_obj = {
            "open_ai": OpenAIService(),
            "open_ai_image": OpenAIImage(),
            "palm_api": PalmText(),
            "palm_chat": PalmChat(),
            "stable_diffusion": StableDiffusion(),
            "cohere_api": CohereApi(),
            "ai21_api": JurasicText(),
            "gemini_ai": GeminiAIService(),
            "anthropic": AnthropicService(),
        }
        response_obj = {
            "open_ai": OpenAiRes(),
            "open_ai_image": OpenAiImageRes(),
            "palm_api": PalmTextRes(),
            "palm_chat": PalmChatRes(),
            "stable_diffusion": StableDuffusionRes(),
            "cohere_api": CohereRes(),
            "ai21_api": JarasicTextRes(),
            "gemini_ai": GeminiAiRes(),
            "anthropic": AnthropicService(),
        }
        if process_name not in process_obj:
            raise ProcessMQException(
                f"Process of message queue Not Found process->{process_name}"
            )
        return process_obj[process_name], response_obj[process_name]
