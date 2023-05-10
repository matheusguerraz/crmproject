from django.urls import path
from pedidos.views import faz_pedido, sucesso_pedido, lista_produtos
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('pedidos/', lista_produtos, name='lista_produtos'),
    path('faz-pedido/', faz_pedido, name='faz_pedido'),
    path('sucesso-pedido/', sucesso_pedido, name='sucesso_pedido'),
    path('adicionar-ao-carrinho/', views.adicionar_produto_carrinho, name='adicionar_produto_carrinho'),
    path('carrinho/', views.exibir_carrinho, name='exibir_carrinho'),
    path('remover-do-carrinho/', views.remover_produto_carrinho, name='remover_produto_carrinho'),
    path('produto/<id>/', views.detalhes_produto, name='detalhes_produto'),
    path('file-traffic/', views.adicionar_produto_carrinho, name='fale-traffic'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)