from django.shortcuts import render
import time
# Create your views here.
import json
import logging
from openai import AsyncOpenAI, OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BotConfig, ChatLog
from .agent_tools import AVAILABLE_TOOLS, TOOLS_SCHEMA
import os

@csrf_exempt
async def chat_completions_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        body_data = json.loads(request.body.decode('utf-8'))
        messages = body_data.get('messages', [])
        model = body_data.get('model', 'openai/gpt-oss-120b')
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
            base_url=os.getenv("base_url"), 
            api_key=os.getenv("api_key")
        )
        MAX_TOOL_CALLS = 4
        tool_call_count = 0
        ai_response_text = ""
        while True:
            ai_response = await client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=full_messages,
                temperature=config.temperature,
                tools=TOOLS_SCHEMA,  
                tool_choice="auto"
            )
            response_message = ai_response.choices[0].message
            finish_reason = ai_response.choices[0].finish_reason
            if finish_reason == "tool_calls" and response_message.tool_calls:
                print("Tool calling detected!")
                if tool_call_count >= MAX_TOOL_CALLS:
                    break
                tool_call_count += 1
                full_messages.append(response_message.model_dump(exclude_none=True,
        exclude={"annotations"}))
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    print("Tool called:", function_name)
                    function_args_str = tool_call.function.arguments
                    tool_call_id = tool_call.id
                    try:
                        function_args = json.loads(function_args_str)
                    except Exception:
                        function_args = {}
                    if function_name in AVAILABLE_TOOLS:
                        try:
                            function_to_call = AVAILABLE_TOOLS[function_name]
                            tool_output = function_to_call(**function_args)
                        except Exception as exec_error:
                            tool_output = f"Error executing tool {function_name}: {str(exec_error)}"
                    else:
                        tool_output = f"Error: Tool '{function_name}' not found."
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": str(tool_output)
                    })
                continue 
            else:
                # استخراج متن نهایی دقیقاً با نام متغیر مورد نظر شما
                ai_response_text = response_message.content or ""
                break
        
        if ai_response_text:
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





