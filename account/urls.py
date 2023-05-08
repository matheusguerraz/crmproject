from django.urls import path
from .views import SignUpView, login_view, logout_view

urlpatterns = [
    path('account/', SignUpView.as_view(), name='account'), #DONE, criação de conta
    path('login/', login_view, name='login'), #Process, login de usuário
    path('logout/', logout_view, name='logout'),
]