from django.urls import path
from pedidos.views import faz_pedido, sucesso_pedido, lista_produtos
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('pedidos/', lista_produtos, name='lista_produtos'),
    path('faz-pedido/', faz_pedido, name='faz_pedido'),
    path('sucesso-pedido/', sucesso_pedido, name='sucesso_pedido'),
    path('adicionar-ao-carrinho/<int:id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/<int:id>/', views.carrinho_ajax, name='carrinho'),
    path('produto/<int:id>/', views.detalhes_produto, name='detalhes_produto'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)