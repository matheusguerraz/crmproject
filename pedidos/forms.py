from django import forms

class PedidoForm(forms.Form):
    produto_id = forms.IntegerField(widget=forms.HiddenInput())
    quantidade = forms.IntegerField(min_value=1, max_value=100, label='Quantidade')
    
class RemoverProdutoCarrinhoForm(forms.Form):
    produto_id = forms.IntegerField(widget=forms.HiddenInput())

