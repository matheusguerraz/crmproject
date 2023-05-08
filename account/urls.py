from django.urls import path
from .views import SignUpView

urlpatterns = [
    path('account/', SignUpView.as_view(), name='account'),
]