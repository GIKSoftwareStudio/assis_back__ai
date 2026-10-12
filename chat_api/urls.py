from django.urls import path



from .views import chat_completions_view
from .views import models_list_view
urlpatterns = [
    path('chat/completions/', chat_completions_view, name='chat_completions'),
    path('models/', models_list_view, name='models_list')
]


