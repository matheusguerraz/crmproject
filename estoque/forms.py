from django import forms
from .models import Produto, Marca, ProdutoImagem

class EstoqueForm(forms.ModelForm):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all())

    class Meta:
        model = Produto
        fields = ('produto','descricao','sabor' ,'preco','marca', 'quantidade_em_estoque', 'estoque_minimo')
        exclude = []

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ('nome','descricao')

class ProdutoImagemForm(forms.ModelForm):
    class Meta:
        model = ProdutoImagem
        fields = ['imagem']
