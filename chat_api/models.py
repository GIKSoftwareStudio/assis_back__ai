from django.db import models

class BotConfig(models.Model):
    system_prompt = models.TextField(default="You are a helpful assistant.")
    model_name = models.CharField(max_length=100, default="oc/deepseek-v4.1-flash-free")
    temperature = models.FloatField(default=0.7)


def __str__(self):
    return f"Config (Model: {self.model_name})"



class ChatLog(models.Model):
    user_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    



def __str__(self):
    content = self.content[:30]
    if len(self.content) > 30:
        content += "..."
        return f"[{self.role}] User {self.user_id} : {content}"
