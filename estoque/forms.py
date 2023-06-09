from django import forms
from .models import Produto, Marca

class EstoqueForm(forms.ModelForm):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all())

    class Meta:
        model = Produto
        fields = ('produto','descricao','sabor','imagem', 'preco','marca', 'quantidade_em_estoque', 'estoque_minimo')

class MarcaForm(forms.ModelForm):

    class Meta:
        model = Marca
        fields = ('nome','descricao')
