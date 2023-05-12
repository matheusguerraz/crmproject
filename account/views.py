from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse
import hashlib
from passlib.hash import pbkdf2_sha256
import os
from urllib.parse import urlencode


class SignUpView(CreateView):
    model = CustomUser
    template_name = 'account/index.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('lista_produtos')

    def form_invalid(self, form):
        errors = {}

        # Validação de senha fraca
        password = form.cleaned_data.get('password')
        if password is not None:
            try:
                validate_password(password)
            except ValidationError as e:
                errors.update({'password': e.messages})
        else:
            errors.update({'password': ['A senha não pode ser vazia.']})

        # Validação de usuário já cadastrado
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            errors.update({'email': ['Já existe um usuário cadastrado com este e-mail.']})

        # Validação de e-mail inválido
        try:
            form.full_clean()
        except ValidationError as e:
            errors.update({'email': [e.message]})

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': errors})
        else:
            # Mensagens de erro específicas
            if 'password' in errors:
                messages.error(self.request, errors['password'][0])
            if 'email' in errors:
                messages.error(self.request, errors['email'][0])
            if 'non_field_errors' in form.errors:
                messages.error(self.request, form.errors['non_field_errors'][0])
            return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=raw_password)

        # Verifica as credenciais do usuário
        if user is not None:
            # Inicia a sessão do usuário
            login(self.request, user)

            # Retorna a resposta
            return response
        else:
            messages.error(self.request, 'Credenciais inválidas.')
            return redirect('signup')

    def form_valid_ajax(self, form):
        # Verifica se uma senha foi fornecida
        if not form.cleaned_data.get('password'):
            return JsonResponse({'error': 'É necessário fornecer uma senha.'})

        # Salva o usuário no banco de dados
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password'))

        # Gera o salt para o usuário
        salt = os.urandom(32)
        user.salt = salt.hex()

        # Gera o hash da senha com o salt
        password = form.cleaned_data.get('password').encode('utf-8')
        hash_obj = hashlib.sha256(password + salt)
        user.password = hash_obj.hexdigest()

        user.save()

        # Retorna uma resposta em JSON com a mensagem de sucesso
        return JsonResponse({'success': 'Usuário criado com sucesso!'})


    def form_invalid_ajax(self, form):
        errors = {}

        # Validação de senha fraca
        password = form.cleaned_data.get('password')
        if password is not None:
            try:
                validate_password(password)
            except ValidationError as e:
                errors.update({'password': e.messages})
        else:
            errors.update({'password': ['A senha não pode ser vazia.']})

        # Validação de usuário já cadastrado
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            errors.update({'email': ['Já existe um usuário cadastrado com este e-mail.']})

        # Validação de e-mail inválido
        try:
            CustomUser().clean_email(email)
        except ValidationError as e:
            errors.update({'email': [e.message]})

        if not errors:
            # Gera um salt aleatório
            salt = pbkdf2_sha256.using(rounds=10000, salt_size=16).gen_salt()

            # Gera o hash da senha com o salt
            password_hash = pbkdf2_sha256.using(rounds=10000, salt=salt).hash(form.cleaned_data.get('password'))

            # Salva o usuário no banco de dados com a senha criptografada
            user = form.save(commit=False)
            user.password = password_hash
            user.salt = salt
            user.save()

            return JsonResponse({'success': 'Usuário criado com sucesso!'})
        else:
            return JsonResponse({'error': errors})


    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if form.is_valid():
                return self.form_valid_ajax(form)
            else:
                return self.form_invalid_ajax(form)
        else:
            return super().post(request, *args, **kwargs)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        print('passou na view')
        if form.is_valid():
            # Tenta autenticar o usuário
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Autentica o usuário e redireciona para a página de destino
                login(request, user)
                return redirect('lista_produtos')
            else:
                # Informa que as credenciais são inválidas
                form.add_error(None, 'Credenciais inválidas. Por favor, tente novamente.')

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
        
def logout_view(request):
    
    params = {'logout': 'true'}
    query_string = urlencode(params)
    url = f"{reverse('lista_produtos')}?{query_string}"
    logout(request)
    return redirect(url)