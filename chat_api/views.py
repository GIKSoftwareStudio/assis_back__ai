from django.shortcuts import render
import time
# Create your views here.
import json
import logging
from openai import AsyncOpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BotConfig, ChatLog

@csrf_exempt
async def chat_completions_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        body_data = json.loads(request.body.decode('utf-8'))
        messages = body_data.get('messages', [])
        model = body_data.get('model', 'gen-lang-client-0049376852')
        user_message = ""
        user_id = "default_user"
        if messages:
            last_message = messages[-1].get('content', '')
            print(f"({model}): {last_message}") # logging is better here i guess
            user_message = last_message
        if user_message:
            await ChatLog.objects.acreate(
                user_id = user_id,
                role = "user",
                content = user_message
            )
        config, created = await BotConfig.objects.aget_or_create(
            id=1,
            defaults={ 
                "system_prompt": "You are a helpful assistant.",
                "model_name": model,
                "temperature": 0.7
                }
        )
        system_message = {
            "role": "system",
            "content": config.system_prompt
        }
        full_messages = [system_message] + messages
        client = AsyncOpenAI(
            base_url="http://localhost:11434/v1",  # for example 
            api_key="ollama"
        )
        
        ai_response = await client.chat.completions.create(
            model = config.model_name,
            messages=full_messages,
            temperature=config.temperature
        )
        ai_response_text = ai_response.choices[0].message.content
        await ChatLog.objects.acreate(
            user_id = user_id,
            role = "assistant",
            content = ai_response_text
        )
        response_data = {
            "id": "gen-lang-client-0049376852",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": ai_response_text
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception:
        logging.exception("Chat completion failed")
        return JsonResponse(
            {"error": "Internal server error"},
            status = 500
        )
        



@csrf_exempt
def models_list_view(request):
    models_data = {
        "object": "list",
        "data": [
            {
                "id": "gen-lang-client-0049376852",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "Default Gemini Project"
            }
        ]
    }
    return JsonResponse(models_data)


        



