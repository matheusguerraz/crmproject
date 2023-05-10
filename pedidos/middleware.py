from .models import Carrinho
import uuid

class CarrinhoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Se o usuário estiver autenticado, verifique se já tem um carrinho associado a ele.
            # Se não houver um carrinho, crie um novo e associe-o ao usuário.
            carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
        else:
            # Se o usuário não estiver autenticado, verifique se há um carrinho ID no cookie.
            carrinho_id = request.COOKIES.get('carrinho_id')
            if carrinho_id:
                # Se houver um carrinho ID no cookie, verifique se existe um carrinho com esse ID.
                carrinho = Carrinho.objects.filter(id=carrinho_id).first()
            else:
                # Se não houver um carrinho ID no cookie, crie um novo carrinho e salve o ID no cookie.
                carrinho = Carrinho.objects.create()
                response = self.get_response(request)
                response.set_cookie('carrinho_id', carrinho.id)
                return response

        request.carrinho = carrinho
        response = self.get_response(request)
        return response