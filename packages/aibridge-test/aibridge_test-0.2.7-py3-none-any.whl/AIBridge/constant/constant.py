PRIORITY = [
    "high",
    "medium",
    "equal",
    "low",
]
FORMATTER = ["json", "csv", "xml"]
AI_SERVICES = [
    "open_ai",
    "palm_api",
    "stable_diffusion",
    "cohere_api",
    "ai21_api",
    "gemini_ai",
    "anthropic",
]
DB_TYPES = ["sql", "nosql"]
CUSTOM_CONFIG_PATH = "AIBRIDGE_CONFIG"
LINUX_MACOS_PATH = "/etc/aibridge/aibridge_config.yaml"
OPENAI_IMAGE_TYPE = ["create", "variation", "edit"]
OPENAI_IMAGE_SIZES = ["256x256", "512x512", "1024x1024"]
STABLE_DIFFUSION_TYPES = [
    "text2img",
    "img2img",
    "inpaint",
]
FUNCTION_CALL_FORMAT = {
    "name": "Give_Information",
    "description": "Generate output in given key and valid json formate",
    "parameters": {},
}

COHERE_FUNCTION_CALL_FORMAT = {
    "name": "Give_Information",
    "description": "Generate output in given key and valid json formate",
    "parameter_definitions": {},
}
