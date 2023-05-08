from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .forms import CustomUserCreationForm
from .models import CustomUser


class SignUpView(CreateView):
    model = CustomUser
    template_name = 'account/index.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

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




    def form_valid_ajax(self, form):
        # Verifica se uma senha foi fornecida
        if not form.cleaned_data.get('password'):
            return JsonResponse({'error': 'É necessário fornecer uma senha.'})

        # Salva o usuário no banco de dados
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password'))
        user.save()

        # Retorna uma resposta em JSON com a mensagem de sucesso
        return JsonResponse({'success': 'Usuário criado com sucesso!'})

    def form_invalid_ajax(self, form):
        errors = {}

        # Validação de senha fraca
        password = form.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            errors.update({'password': e.messages})

        # Validação de usuário já cadastrado
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            errors.update({'email': ['Já existe um usuário cadastrado com este e-mail.']})

        # Validação de e-mail inválido
        try:
            CustomUser().clean_email(email)
        except ValidationError as e:
            errors.update({'email': [e.message]})

        if 'password' in errors or 'email' in errors:
            return JsonResponse({'error': errors})
        else:
            return super().form_invalid_ajax(form)

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
    