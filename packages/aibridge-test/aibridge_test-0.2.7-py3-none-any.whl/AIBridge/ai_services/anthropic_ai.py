from AIBridge.output_validation.convertors import FromJson, IntoJson
import time
import uuid
from AIBridge.exceptions import AnthropicsException, AIBridgeException
from AIBridge.prompts.prompt_completion import Completion
from AIBridge.ai_services.ai_abstraction import AIInterface
from AIBridge.output_validation.active_validator import ActiveValidator
import json
from AIBridge.constant.common import (
    get_function_from_json,
    parse_fromat,
    parse_api_key,
    AnthropicsFunctionCall,
)
from anthropic import Anthropic


class AnthropicService(AIInterface):
    """
    Base class for Anthropics Services
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
        model="claude-3-opus-20240229",
        variation_count: int = 1,
        max_tokens: int = 4000,
        temperature: float = 0.5,
        message_queue=False,
        api_key=None,
        output_format_parse=True,
        stream=False,
        context=[],
    ):
        try:
            if prompts and prompt_ids:
                raise AnthropicsException(
                    "please provide either prompts or prompts ids at atime"
                )
            if not prompts and not prompt_ids:
                raise AnthropicsException(
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
                    "ai_service": "open_ai",
                    "output_format": json.dumps(output_format),
                    "format_structure": json.dumps(format_strcture),
                    "api_key": api_key,
                    "context": context,
                    "stream": True,
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
                stream=stream,
            )
        except AIBridgeException as e:
            raise AnthropicsException(f"Error in generating AI data {e}")

    @classmethod
    def execute_text_prompt(
        self, api_key, model, messages, n, max_tokens=3500, temperature=0.5
    ):
        client = Anthropic(api_key=api_key)
        return client.messages.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    @classmethod
    def execute_prompt_function_calling(
        self,
        api_key,
        model,
        messages,
        n,
        functions_call,
        max_tokens=3500,
        temperature=0.5,
    ):
        client = Anthropic(api_key=api_key)
        return client.messages.create(
            model=model,
            messages=messages,
            system=functions_call,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    @classmethod
    def get_prompt_context(self, context):
        context_list = []
        prev_role = ""
        for _context in context:
            if _context["role"] not in ["user", "system", "assistant"]:
                raise AnthropicsException(
                    "Invalid role provided. Please provide either user or system, assistant"
                )
            key = _context["role"]
            if prev_role == key:
                if key == "user":
                    context_list.append({"role": "assistant", "content": "understood"})
                elif key == "assistant" or key == "system":
                    context_list.append({"role": "user", "content": "thanks"})
            else:
                context_list.append({"role": key, "content": _context["context"]})
            prev_role = key
        if context_list:
            data_test = context_list[-1]
            if data_test["role"] == "user":
                context_list.append({"role": "assistant", "content": "understood"})
        return context_list

    @classmethod
    def get_response(
        self,
        prompts,
        model="claude-3-opus-20240229",
        variation_count=1,
        max_tokens=3500,
        temperature=0.5,
        output_format=[],
        format_structure=[],
        api_key=None,
        context=[],
        stream=False,
    ):
        try:
            if output_format:
                if isinstance(output_format, str):
                    output_format = json.loads(output_format)
            if format_structure:
                if isinstance(format_structure, str):
                    format_structure = json.loads(format_structure)
            if not prompts:
                raise AnthropicsException("No prompts provided")
            api_key = api_key if api_key else parse_api_key("anthropic")
            message_data = self.get_prompt_context(context)
            model_output = []
            token_used = 0
            _formatter = "string"
            func_call = False
            for index, prompt in enumerate(prompts):
                if output_format:
                    _formatter = output_format[index]
                message_data.append({"role": "user", "content": prompt})
                if _formatter not in ["json", "csv", "xml"]:
                    response = self.execute_text_prompt(
                        api_key,
                        model=model,
                        messages=message_data,
                        n=variation_count,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    message_data.append(
                        {
                            "role": response.role,
                            "content": response.content[0].text,
                        }
                    )
                else:
                    func_call = True
                    if _formatter == "csv":
                        schema = IntoJson.csv_to_json(format_structure[index])
                    elif _formatter == "xml":
                        schema = IntoJson.xml_to_json(format_structure[index])
                    elif _formatter == "json":
                        schema = json.loads(format_structure[index])
                    functions = (
                        AnthropicsFunctionCall.construct_format_tool_for_claude_prompt(
                            parameters=schema
                        )
                    )
                    response = self.execute_prompt_function_calling(
                        api_key=api_key,
                        model=model,
                        messages=message_data,
                        n=variation_count,
                        functions_call=functions,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    message_data.append(
                        {
                            "role": response.role,
                            "content": response.content[0].text,
                        }
                    )
                print(response)
                tokens = response.usage.input_tokens + response.usage.output_tokens
                token_used = token_used + tokens
                for index, res in enumerate(response.content):
                    content = res.text
                    if func_call:
                        json_content = IntoJson.xml_to_json(content)
                        print(json_content)
                        content = json_content["function_calls"][0]["invoke"][
                            "parameters"
                        ]
                        if isinstance(content, dict):
                            content = json.dumps(content)

                    if output_format:
                        try:
                            if _formatter == "csv":
                                content = FromJson.json_to_csv(json.loads(content))
                            elif _formatter == "xml":
                                content = FromJson.json_to_xml(json.loads(content))
                        except AIBridgeException as e:
                            raise AnthropicsException(
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
                    "ai_service": "anthropic",
                }
            }
            return message_value
        except AIBridgeException as e:
            raise AnthropicsException(f"{e}")
