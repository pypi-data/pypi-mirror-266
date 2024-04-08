from pprint import pprint
from src.core_pro.chat_bot import OpenAIChat


# chat
json = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}]
}
response = OpenAIChat().chat(json)
pprint(response)

# function call
json = {
    "messages": [
        {
            "role": "system",
            "content": "Extract information on product name"
        },
        {
            "role": "user",
            "content": "Tinh dầu dưỡng tóc Moroccanoil Treatment chai 10ml không box"
        }
    ],
    'functions': [
        {
            "name": "get_product_info",
            "description": "Get product's name and size from document",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the product, e.g. SunSilk"
                    },
                    "size": {
                        "type": "string",
                        "description": "The size of the product, e.g. 100g"
                    },
                },
                "required": ["name"]
            },
        },
    ]
}
response = OpenAIChat().chat(json)
pprint(response)
