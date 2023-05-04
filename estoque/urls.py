from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),#DONE
    path('remover_produto/<int:pk>/', views.remover_produto, name='remover_produto'),#DONE
    path('modificar_produto/<int:pk>/', views.modificar_produto, name='modificar_produto'),#DONE
    path('produtos_em_falta/', views.produtos_em_falta, name='produtos_em_falta'),#DONE
    path('add_produto/', views.cadastrar_produto, name='add_produto'),

    path('listar_marcas/', views.listar_marcas, name='listar_marcas'),
    path('editar_marca/<int:pk>/', views.editar_marca, name='editar_marca'),
    path('deletar_marca/<int:pk>/', views.deletar_marca, name='deletar_marca'),
    path('cadastrar_marca/', views.cadastrar_marca, name='cadastrar_marca'),


]