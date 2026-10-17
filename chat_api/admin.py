from django.contrib import admin
from .models import ChatLog, BotConfig

@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'temperature', 'system_prompt')
@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("user_id", "role", "created_at", "content")
    list_filter = ('role', 'created_at')
    search_fields = ('user_id', 'content')


