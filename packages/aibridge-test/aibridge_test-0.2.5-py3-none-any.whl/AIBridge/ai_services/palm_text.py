import time
import uuid
from AIBridge.exceptions import PalmTextException, AIBridgeException
from AIBridge.prompts.prompt_completion import Completion
from AIBridge.ai_services.ai_abstraction import AIInterface
from AIBridge.output_validation.active_validator import ActiveValidator
import json
from AIBridge.constant.common import parse_fromat, parse_api_key
import google.generativeai as palm
from AIBridge.output_validation.convertors import FromJson, IntoJson


class PalmText(AIInterface):
    """
    Base class for PalmText's Services
    """

    @classmethod
    def generate(
        self,
        prompts: list[str] = [],
        prompt_ids: list[str] = [],
        prompt_data: list[dict] = [],
        variables: list[dict] = [],
        output_format: list[str] = [],
        format_strcture: list[str] = [],
        model="models/text-bison-001",
        variation_count: int = 1,
        max_tokens: int = 10000,
        temperature: float = 0.5,
        message_queue=False,
        api_key=None,
        output_format_parse=True,
        context=[],
    ):
        try:
            if prompts and prompt_ids:
                raise PalmTextException(
                    "please provide either prompts or prompts ids at atime"
                )
            if not prompts and not prompt_ids:
                raise PalmTextException(
                    "Either provide prompts or prompts ids to genrate the data"
                )
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
            if output_format:
                if len(output_format) != len(prompts_list):
                    raise AIBridgeException(
                        "length of output_format must be equal to length of the prompts"
                    )
            if format_strcture:
                if len(format_strcture) != len(prompts_list):
                    raise AIBridgeException(
                        "length of format_strcture must be equal to length of the prompts"
                    )
            updated_prompts = []
            for _prompt in prompts_list:
                format = None
                format_str = None
                if output_format:
                    format = output_format[prompts_list.index(_prompt)]
                if format_strcture:
                    format_str = format_strcture[prompts_list.index(_prompt)]
                if output_format_parse:
                    u_prompt = parse_fromat(
                        _prompt, format=format, format_structure=format_str
                    )
                    updated_prompts.append(u_prompt)
            if not updated_prompts:
                updated_prompts = prompts_list
            if message_queue:
                id = uuid.uuid4()
                message_data = {
                    "id": str(id),
                    "prompts": json.dumps(updated_prompts),
                    "model": model,
                    "variation_count": variation_count,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "ai_service": "palm_api",
                    "output_format": json.dumps(output_format),
                    "format_structure": json.dumps(format_strcture),
                    "api_key": api_key,
                    "context": context,
                }
                message = {"data": json.dumps(message_data)}
                from AIBridge.queue_integration.message_queue import MessageQ

                MessageQ.mq_enque(message=message)
                return {"response_id": str(id)}
            return self.get_response(
                updated_prompts,
                model,
                variation_count,
                max_tokens,
                temperature,
                output_format,
                format_strcture,
                api_key=api_key,
                context=context,
            )
        except AIBridgeException as e:
            raise PalmTextException(f"Error in generating AI data {e}")

    @classmethod
    def get_tokens(Self, model, text):
        tokens = palm.count_text_tokens(model=model, prompt=text)
        return tokens["token_count"]

    @classmethod
    def get_prompt_context(self, context):
        context_string = ""
        for _context in context:
            if _context["role"] not in ["user", "system", "assistant"]:
                raise PalmTextException(
                    "Invalid role provided. Please provide either user or system, assistant"
                )
            context_string = (
                context_string + f"{_context['role']}:{_context['context']}" + "\n"
            )
        return context_string

    @classmethod
    def get_response(
        self,
        prompts,
        model="models/text-bison-001",
        variation_count=1,
        max_tokens=10000,
        temperature=0.5,
        output_format=[],
        format_structure=[],
        api_key=None,
        context=[],
    ):
        try:
            if output_format:
                if isinstance(output_format, str):
                    output_format = json.loads(output_format)
            if format_structure:
                if isinstance(format_structure, str):
                    format_structure = json.loads(format_structure)
            if not prompts:
                raise PalmTextException("No prompts provided")
            api_key = api_key if api_key else parse_api_key("palm_api")
            palm.configure(api_key=api_key)
            model_output = []
            token_used = 0
            context_string = self.get_prompt_context(context)
            for index, prompt in enumerate(prompts):
                prompt = context_string + "\n" + prompt
                response = palm.generate_text(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    candidate_count=variation_count,
                )
                token_used = token_used + self.get_tokens(model, prompt)
                for res in response.candidates:
                    content = res["output"]
                    token_used = token_used + self.get_tokens(model, content)
                    if output_format:
                        _formatter = output_format[index]
                        try:
                            if _formatter == "csv":
                                content = FromJson.json_to_csv(json.loads(content))
                            elif _formatter == "xml":
                                content = FromJson.json_to_xml(json.loads(content))
                        except AIBridgeException as e:
                            raise PalmTextException(
                                f"Ai response is not in valid {_formatter}"
                            )
                        if _formatter == "json":
                            _validate_obj = ActiveValidator.get_active_validator(
                                _formatter
                            )
                            try:
                                content = _validate_obj.validate(
                                    content,
                                    schema=(
                                        format_structure[index]
                                        if format_structure
                                        else None
                                    ),
                                )
                            except AIBridgeException as e:
                                content_error = {
                                    "error": f"{e}",
                                    "ai_response": content,
                                }
                                content = json.dumps(content_error)
                    if index >= len(model_output):
                        model_output.append({"data": [content]})
                    else:
                        model_output[index]["data"].append(content)
            message_value = {
                "items": {
                    "response": model_output,
                    "token_used": token_used,
                    "created_at": time.time(),
                    "ai_service": "palm_api",
                }
            }
            return message_value
        except AIBridgeException as e:
            raise PalmTextException(f"{e}")
