from django.db import models
from django.core.validators import MinValueValidator


    
class Marca(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    def __str__(self):
        return self.nome

class Produto(models.Model):
    produto = models.CharField(max_length=200)
    descricao = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    marca = models.ForeignKey(Marca, 
                            on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='produtos/%Y/%m/%d', blank=True)
    estoque_minimo = models.PositiveIntegerField(default=0)
    quantidade_em_estoque = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.produto
    
