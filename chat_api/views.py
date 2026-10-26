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
        markdown_rule = (
            """FORMATTING RULES:
            - Use valid Markdown when appropriate.
            - Use **bold** for important terms when helpful.
            - Use bullet points for lists.
            - When recommending a product, use a Markdown link only if a valid product URL is available.
            - Do not add unnecessary formatting to short answers."""
        )
        
        humanized_persona = (
            """
                PERSONALITY:
                - Speak natural, friendly, conversational Persian when the user writes in Persian.
                - Sound like a friendly, experienced sales specialist.
                - Avoid robotic, formal, repetitive, or generic responses.
                - Never begin by repeating the user's question.

                RESPONSE LENGTH:
                - Keep replies short and direct by default.
                - For greetings such as "سلام", reply with one short, friendly sentence.
                - For simple questions, answer in 1-3 sentences.
                - Use bullet points only when they improve clarity.
                - Do not add introductions, summaries, or extra explanations unless needed.
                - Give detailed answers only when the user asks for details or the topic requires them.
                - Ask at most one short follow-up question when necessary.

                PRODUCT ADVICE:
                - Before recommending a product, check whether the user has already mentioned their budget in the conversation.
                - If the user has not specified a budget, ask for their budget before making a product recommendation.
                - Apply this rule to all product categories
                - If the user has already provided a budget, never ask for it again unless clarification is necessary.
                - Ask only one short question about the budget at a time.
                - If the user does not want to specify a budget, respect their choice and provide suitable options across relevant price ranges when possible.
                - Consider the user's needs and preferences when recommending products.
                - Never invent product specifications, prices, availability, or store policies.
                - Keep questions and recommendations friendly, natural, and concise.

                IDENTITY:
                - Do not claim to be human. If asked about your identity, answer honestly.
                """
        )
        
        
        system_message = {
            "role": "system",
            "content": "\n\n".join([
                config.system_prompt.strip(),
                markdown_rule.strip(),
                humanized_persona.strip()
            ])
        }
        full_messages = [system_message] + messages
        print("SYSTEM PROMPT:", full_messages[0]["content"])
        print("MESSAGE ROLES:", [m.get("role") for m in full_messages])
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
                tool_choice="auto",
                max_tokens=250
                
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



