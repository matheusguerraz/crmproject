
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .forms import PedidoForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def lista_produtos(request):
    form = ItemCarrinho()
    produtos = Produto.objects.filter(quantidade_em_estoque__gt=0)
    return render(request, 'pedidos/product_list.html', {'produtos': produtos, 'form': form})



def faz_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = Pedido(nome_cliente=form.cleaned_data['nome'], email_cliente=form.cleaned_data['email'])
            pedido.save()
            for produto_id, quantidade in form.cleaned_data['produtos'].items():
                produto = Produto.objects.get(pk=produto_id)
                preco_unitario = produto.preco
                item = ItemPedido(pedido=pedido, produto=produto, quantidade=quantidade, preco_unitario=preco_unitario)
                item.save()
            return redirect('sucesso_pedido')
    else:
        form = PedidoForm()
    return render(request, 'pedidos/faz_pedido.html', {'form': form})

def sucesso_pedido(request):
    return render(request, 'pedidos/sucesso_pedido.html')

@csrf_protect
def adicionar_ao_carrinho(request):
    produto_id = request.POST.get('product_id')
    produto = get_object_or_404(Produto, pk=produto_id)
    item_carrinho, criado = ItemCarrinho.objects.get_or_create(
        produto=produto,
    )
    if not criado:
        item_carrinho.quantidade += 1
        item_carrinho.save()
    return JsonResponse({'success': True})  

@csrf_protect
def carrinho(request):
    carrinho = None
    items = []
    total = 0
    if 'carrinho' in request.session:
        carrinho = request.session['carrinho']
        for item in carrinho:
            produto = get_object_or_404(Produto, pk=item['produto_id'])
            items.append({
                'id': item['produto_id'],
                'produto': produto.nome,
                'quantidade': item['quantidade'],
                'preco_unitario': produto.preco,
                'preco_total': item['quantidade'] * produto.preco,
            })
            total += item['quantidade'] * produto.preco
    return render(request, 'pedidos/carrinho.html', {'items': items, 'total': total})

@csrf_protect
def detalhes_produto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    form = ItemCarrinho()

    if request.method == 'POST':
        form = ItemCarrinho(request.POST)
        if form.is_valid():
            quantidade = form.cleaned_data['quantidade']
            carrinho = []
            if 'carrinho' in request.session:
                carrinho = request.session['carrinho']
            carrinho.append({
                'produto_id': id,
                'quantidade': quantidade,
            })
            request.session['carrinho'] = carrinho

            # Redireciona para a página do carrinho
            return redirect('carrinho')

    return render(request, 'pedidos/product_detail.html', {'produto': produto, 'form': form})
@csrf_protect

def carrinho_ajax(request):
    carrinho = Carrinho.objects.get_or_create(usuario=request.user)[0]
    html = render_to_string('carrinho_ajax.html', {'carrinho': carrinho})
    return JsonResponse({'html': html})
@csrf_protect

def atualizar_carrinho(request):
    carrinho = Carrinho.objects.get(usuario=request.user)
    items = ItemCarrinho.objects.filter(carrinho=carrinho)

    total = 0
    for item in items:
        total += item.quantidade * item.produto.preco

    return JsonResponse({
        'items': [{
            'id': item.id,
            'produto': item.produto.produto,
            'quantidade': item.quantidade,
            'preco_unitario': item.produto.preco,
            'preco_total': item.quantidade * item.produto.preco,
        } for item in items],
        'total': total,
    })