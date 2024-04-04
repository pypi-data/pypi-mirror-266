from abc import ABC, abstractmethod
import json


class Caller(ABC):
    @abstractmethod
    def get_response(self, service_obj, message_data):
        pass


class OpenAiRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            context=message_data["context"],
        )
        return data


class GeminiAiRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            stop_subsequence=message_data["stop_subsequence"],
            stream=message_data["stream"],
            context=message_data["context"],
        )
        return data


class AnthropicRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            stop_subsequence=message_data["stop_subsequence"],
            stream=message_data["stream"],
            context=message_data["context"],
        )
        return data


class OpenAiImageRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            image_data=json.loads(message_data["image_data"]),
            mask_image=json.loads(message_data["mask_image"]),
            variation_count=message_data["variation_count"],
            size=message_data["size"],
            process_type=message_data["process_type"],
            api_key=message_data["api_key"],
            model=message_data["api_key"],
            quality=message_data["quality"],
        )
        return data


class PalmTextRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            context=message_data["context"],
        )
        return data


class PalmChatRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            messages=message_data["messages"],
            context=message_data["context"],
            examples=message_data["examples"],
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            temperature=message_data["temperature"],
            api_key=message_data["api_key"],
        )
        return data


class StableDuffusionRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            image_data=json.loads(message_data["image_data"]),
            mask_image=json.loads(message_data["mask_image"]),
            negative_prompt=message_data["negative_prompt"],
            width=message_data["width"],
            height=message_data["height"],
            samples=message_data["samples"],
            num_inference_steps=message_data["num_inference_steps"],
            safety_checker=message_data["safety_checker"],
            enhance_prompt=message_data["enhance_prompt"],
            guidance_scale=message_data["guidance_scale"],
            strength=message_data["strength"],
            seed=message_data["seed"],
            webhook=message_data["webhook"],
            track_id=message_data["track_id"],
            multi_lingual=message_data["multi_lingual"],
            panorama=message_data["panorama"],
            self_attention=message_data["self_attention"],
            upscale=message_data["upscale"],
            embeddings_model=message_data["embeddings_model"],
            action=message_data["action"],
            message_queue=message_data["message_queue"],
            api_key=message_data["api_key"],
        )
        return data


class CohereRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            context=message_data["context"],
        )
        return data


class JarasicTextRes(Caller):
    @classmethod
    def get_response(self, service_obj, message_data):
        data = service_obj.get_response(
            prompts=json.loads(message_data["prompts"]),
            model=message_data["model"],
            variation_count=message_data["variation_count"],
            max_tokens=message_data["max_tokens"],
            temperature=message_data["temperature"],
            output_format=message_data["output_format"],
            format_structure=message_data["format_structure"],
            api_key=message_data["api_key"],
            context=message_data["context"],
        )
        return data
