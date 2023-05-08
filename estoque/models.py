from django.db import models
    
class Marca(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    SABOR_CHOICES = [
        ('chocolate', 'Chocolate'),
        ('morango', 'Morango'),
        ('baunilha', 'Baunilha'),
        ('sem_sabor', 'Sem sabor'),
    ]
    produto = models.CharField(max_length=200)
    descricao = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    estoque_minimo = models.PositiveIntegerField(default=0)
    quantidade_em_estoque = models.PositiveIntegerField(default=0)
    sabor = models.CharField(max_length=20, choices=SABOR_CHOICES)
    

    def __str__(self):
        return self.produto

class ProdutoImagem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='produtoimagem')
    imagem = models.ImageField(upload_to='media/produtos/%Y/%m/%d')

    def __str__(self):
        return f"Imagem do produto {self.produto.produto}"
