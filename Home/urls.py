from django.urls import path
from .views import (Home)

urlpatterns = [
    path('welcome/', Home, name='welcome'),
    
]
