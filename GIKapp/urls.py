from django.urls import path



from .views import chat_completions_view
urlpatterns = [
    path('chat/completions/', chat_completions_view, name='chat_completions'),
]


