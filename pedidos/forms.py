from django import forms

class PedidoForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, max_value=100, label='Quantidade')
