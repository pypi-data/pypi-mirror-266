from AIBridge.prompts.prompt_completion import Completion
from AIBridge.ai_services.ai_abstraction import AIInterface
from AIBridge.exceptions import StableDiffusionException, AIBridgeException
import json
import uuid
from AIBridge.constant.constant import STABLE_DIFFUSION_TYPES
from AIBridge.constant.common import parse_api_key, check_url
import requests
import time


class StableDiffusion(AIInterface):
    @classmethod
    def generate(
        self,
        prompts: list[str] = [],
        prompt_ids: list[str] = [],
        prompt_data: list[dict] = [],
        variables: list[dict] = [],
        image_data: list[str] = [],
        mask_image: list[str] = [],
        negative_prompt: str = "",
        width: str = "512",
        height: str = "512",
        variation_count: int = 1,
        enhance_prompt: str = "Yes",
        num_inference_steps: str = "20",
        guidance_scale: float = 7.5,
        strength: float = 0.7,
        safety_checker: str = "yes",
        multi_lingual: str = "no",
        panorama: str = "no",
        self_attention: str = "no",
        upscale: str = "no",
        embeddings_model=None,
        webhook=None,
        track_id=None,
        seed=None,
        action="text2img",
        message_queue=False,
        api_key=None,
    ):
        try:
            if prompts and prompt_ids:
                raise StableDiffusionException(
                    "please provide either prompts or prompts ids at atime"
                )
            if not prompts and not prompt_ids:
                raise StableDiffusionException(
                    "Either provide prompts or prompts ids to genrate the data"
                )
            if action not in STABLE_DIFFUSION_TYPES:
                raise StableDiffusionException(
                    f"action should be one of the{STABLE_DIFFUSION_TYPES}"
                )
            if action == "image2image" or action == "inpaint":
                if not image_data:
                    raise StableDiffusionException(
                        "Please enter image link in image data"
                    )
            if action == "inpaint" and not mask_image:
                raise StableDiffusionException(
                    "Please enter mask image link in mask image"
                )
            if mask_image:
                if len(mask_image) != len(image_data):
                    raise StableDiffusionException(
                        "mask_image length should be equal to image_data length",
                    )
                check_url(image_data)
            if prompt_ids:
                prompts_list = Completion.create_prompt_from_id(
                    prompt_ids=prompt_ids,
                    prompt_data_list=prompt_data,
                    variables_list=variables,
                )
            if prompts:
                if prompt_data or variables:
                    prompts_list = Completion.create_prompt(
                        prompt_list=prompts,
                        prompt_data_list=prompt_data,
                        variables_list=variables,
                    )
                else:
                    prompts_list = prompts
            if image_data:
                if prompts_list:
                    if len(image_data) != len(prompts_list):
                        raise StableDiffusionException(
                            "image_data length should be equal to prompts length",
                        )
                check_url(image_data)
            if message_queue:
                id = uuid.uuid4()
                message_data = {
                    "id": str(id),
                    "prompts": json.dumps(prompts_list),
                    "negative_prompt": negative_prompt,
                    "ai_service": "stable_diffusion",
                    "image_data": json.dumps(image_data),
                    "mask_image": json.dumps(mask_image),
                    "action": action,
                    "width": width,
                    "height": height,
                    "samples": str(variation_count),
                    "num_inference_steps": num_inference_steps,
                    "safety_checker": safety_checker,
                    "enhance_prompt": enhance_prompt,
                    "guidance_scale": guidance_scale,
                    "strength": strength,
                    "seed": seed,
                    "webhook": webhook,
                    "track_id": track_id,
                    "multi_lingual": multi_lingual,
                    "panorama": panorama,
                    "self_attention": self_attention,
                    "upscale": upscale,
                    "embeddings_model": embeddings_model,
                    "message_queue": message_queue,
                    "api_key": api_key,
                }
                message = {"data": json.dumps(message_data)}
                from AIBridge.queue_integration.message_queue import MessageQ

                MessageQ.mq_enque(message=message)
                return {"response_id": str(id)}
            return self.get_response(
                prompts=prompts_list,
                image_data=image_data,
                mask_image=mask_image,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                samples=str(variation_count),
                num_inference_steps=num_inference_steps,
                safety_checker=safety_checker,
                enhance_prompt=enhance_prompt,
                guidance_scale=guidance_scale,
                strength=strength,
                seed=seed,
                webhook=webhook,
                track_id=track_id,
                multi_lingual=multi_lingual,
                panorama=panorama,
                self_attention=self_attention,
                upscale=upscale,
                embeddings_model=embeddings_model,
                action=action,
                message_queue=message_queue,
                api_key=api_key,
            )
        except AIBridgeException as e:
            raise StableDiffusionException(f"{e}")

    @classmethod
    def get_response(
        self,
        prompts,
        image_data=[],
        mask_image=[],
        negative_prompt: str = "",
        width: str = "512",
        height: str = "512",
        samples: str = "1",
        enhance_prompt: str = "Yes",
        num_inference_steps: str = "20",
        guidance_scale: float = 7.5,
        strength: float = 0.7,
        safety_checker: str = "yes",
        multi_lingual: str = "no",
        panorama: str = "no",
        self_attention: str = "no",
        upscale: str = "no",
        embeddings_model=None,
        webhook=None,
        track_id=None,
        seed=None,
        action="text2img",
        message_queue=False,
        api_key=None,
    ):
        api_key = api_key if api_key else parse_api_key("stable_diffusion")
        payload = {
            "key": api_key,
            "prompt": "",
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "samples": samples,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "guidance_scale": guidance_scale,
            "safety_checker": safety_checker,
            "multi_lingual": multi_lingual,
            "panorama": panorama,
            "self_attention": self_attention,
            "upscale": upscale,
            "embeddings_model": embeddings_model,
            " enhance_prompt": enhance_prompt,
            "strength": strength,
            "webhook": webhook,
            "track_id": track_id,
        }
        headers = {"Content-Type": "application/json"}
        url = "https://stablediffusionapi.com/api/v3/text2img"
        if action == "img2img":
            url = "https://stablediffusionapi.com/api/v3/img2img"
        if action == "inpaint":
            url = "https://stablediffusionapi.com/api/v3/inpaint"
        data = []
        for index, prompt in enumerate(prompts):
            payload["prompt"] = prompt
            if image_data:
                payload["init_image"] = image_data[index]
            if mask_image:
                payload["mask_image"] = mask_image[index]
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            res = response.json()
            if not message_queue:
                if res["status"] == "error" or res["status"] == "failed":
                    raise StableDiffusionException(res["message"])
            _data = [json.dumps({"url": url}) for url in res["output"]]
            data.append({"data": _data})
        message_value = {
            "items": {
                "response": data,
                "token_used": 0,
                "created_at": time.time(),
                "ai_service": "stable_diffusion",
            }
        }
        return message_value

    @classmethod
    def fetch_image(self, fetch_id):
        api_key = parse_api_key("stable_diffusion")
        payload = {
            "key": api_key,
        }
        url = "https://stablediffusionapi.com/api/v3/fetch/{id}"
        url = url.format(id=fetch_id)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        res = response.json()
        if res["status"] == "error" or res["status"] == "failed":
            raise StableDiffusionException(res["message"])
        return res

    @classmethod
    def system_load(self):
        api_key = parse_api_key("stable_diffusion")
        payload = {
            "key": api_key,
        }
        headers = {"Content-Type": "application/json"}
        url = "https://stablediffusionapi.com/api/v3/system_load"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        res = response.json()
        if "status" in res:
            if res["status"] == "error" or res["status"] == "failed":
                raise StableDiffusionException(res["message"])
        return res
