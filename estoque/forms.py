from django import forms
from .models import Produto, Marca, ProdutoImagem
from multiupload.fields import MultiFileField

class EstoqueForm(forms.ModelForm):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all())

    class Meta:
        model = Produto
        fields = ('produto','descricao','sabor' ,'preco','marca', 'quantidade_em_estoque', 'estoque_minimo')

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ('nome','descricao')

class ProdutoImagemForm(forms.ModelForm):
    imagem = MultiFileField(min_num=1, max_num=5, max_file_size=1024*1024*5)
    class Meta:
        model = ProdutoImagem
        fields = ['imagem']
