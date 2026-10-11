from django.shortcuts import render
import time
# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt

def chat_completions_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        body_data = json.loads(request.body.decode('utf-8'))
        messages = body_data.get('messages', [])
        model = body_data.get('model', 'Gemini')
        if messages:
            last_message = messages[-1].get('content', '')
            print(f": {model}): {last_message}")
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
                        "content": "Hello! I am your Django proxy. Connection successful!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }


        body_data = json.loads(request.body.decode('utf-8'))
        messages = body_data.get('messages', [])
        model = body_data.get('model', 'Gemini')
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)


