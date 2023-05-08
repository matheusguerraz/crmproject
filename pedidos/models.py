from django.db import models
from estoque.models import Produto, ProdutoImagem
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class Pedido(models.Model):
    nome_cliente = models.CharField(max_length=255)
    email_cliente = models.EmailField()
    produtos = models.ManyToManyField(Produto, through='ItemPedido')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='aberto')

    def __str__(self):
        return f"Pedido de {self.nome_cliente} em {self.data_pedido:%Y-%m-%d %H:%M}"

class ItemPedido(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

class Carrinho(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

class ItemCarrinho(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
