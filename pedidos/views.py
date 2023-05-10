
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Produto, Pedido, ItemPedido, Carrinho, ItemCarrinho, ProdutoImagem
from .forms import PedidoForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.sessions.backends.db import SessionStore


class CarrinhoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if 'carrinho_id' not in request.session:
                carrinho = Carrinho.objects.create()
                request.session['carrinho_id'] = carrinho.id
            else:
                carrinho_id = request.session['carrinho_id']
                carrinho = Carrinho.objects.filter(id=carrinho_id).first()
                if carrinho is None:
                    carrinho = Carrinho.objects.create()
                    request.session['carrinho_id'] = carrinho.id
        else:
            carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

        request.carrinho = carrinho
        response = self.get_response(request)

        return response

def lista_produtos(request):
    form = ItemCarrinho()
    produtos = Produto.objects.filter(quantidade_em_estoque__gt=0)
    imagens = ProdutoImagem.objects .all()
    return render(request, 'pedidos/product_list.html', {'produtos': produtos,'imagens': imagens ,'form': form})


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


@csrf_exempt
@csrf_protect
def adicionar_produto_carrinho(request):

    if request.method == 'POST' and request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        print('chegou aqui')
        data = json.loads(request.body)
        valor = data.get('valor')
        print(f'a quantidade inserida botão foi {valor}')
        
        if (int(valor) + item_carrinho.quantidade) > quantidade_estoque:
            return JsonResponse({'quantidae_acima': True})
    
    try:
        if request.user.is_authenticated:
            carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
            produto_id = request.POST.get('produto_id').strip()
        else:
            carrinho, criado = Carrinho.objects.get_or_create(usuario=None)
            produto_id = request.POST.get('produto_id').strip()
        
        itens_carrinho = ItemCarrinho.objects.filter(Q(carrinho__usuario=request.user) | Q(carrinho__usuario__isnull=True))

        if produto_id is not None:
            produto = get_object_or_404(Produto, pk=produto_id)
            quantidade = int(request.POST.get('quantidade', 1))

            quantidade_estoque = produto.quantidade_em_estoque


            if not criado:
                item_carrinho, criado = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto_id=produto_id)
                qtd_carrinho_e_pedido = quantidade + item_carrinho.quantidade
                    
                item_carrinho.quantidade += quantidade
                item_carrinho.full_clean()
                item_carrinho.save()
            else:
                item_carrinho.quantidade = quantidade
                item_carrinho.full_clean()
                item_carrinho.save()
            
            

        else:
            print(f'produto é none {produto_id}')
        context = {
            'carrinho': carrinho,
            'itens_carrinho': ItemCarrinho.objects.filter(carrinho=carrinho),
        }


        context['produto_adicionado'] = True
        next_url = request.GET.get('next', reverse('exibir_carrinho'))
        print(context)
        return redirect('{}?produto_adicionado=true'.format(next_url))

    except Exception as e:
        print(f'O erro foi o {e}')
        return HttpResponseServerError(str(e))
    
def exibir_carrinho(request):
    carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
    itemcarrinho = ItemCarrinho.objects.filter(carrinho=carrinho)
    produtos = []
    imagens = ProdutoImagem.objects.all()

    total_pedido = 0
    for item in itemcarrinho:
        produto = get_object_or_404(Produto, pk=item.produto_id)
        item.total_item = item.quantidade * produto.preco
        produtos.append(produto)

        if request.method == 'POST':
            item_id = request.POST.get(f'item{item.id}')
            nova_quantidade = request.POST.get(f'quantidade{item.id}')
            if item_id and nova_quantidade:
                item.quantidade = int(nova_quantidade)
                item.total_item = item.quantidade * produto.preco
                item.save()

        total_pedido += item.total_item

    context = {'carrinho': carrinho, 'itemcarrinho': zip(itemcarrinho, produtos), 'imagens': imagens, 'total_pedido': total_pedido}
    return render(request, 'pedidos/carrinho_navbar.html', context)



def remover_produto_carrinho(request):

    if request.user.is_authenticated:
        carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
        produto_id = request.POST['produto_id']
        produto = get_object_or_404(Produto, pk=produto_id)
        item_carrinho = carrinho.itemcarrinho_set.filter(produto=produto).first()
    if item_carrinho:
        if item_carrinho.quantidade > 1:
            item_carrinho.quantidade -= 1
            item_carrinho.full_clean()
            item_carrinho.save()
        else:
            item_carrinho.delete()
    return redirect('exibir_carrinho')

@csrf_protect
def detalhes_produto(request, id):
    if request.user.is_authenticated:
        carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)

    else:
        carrinho = Carrinho.objects.create()
    
    produto = get_object_or_404(Produto, pk=id)
    item_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho, produto=produto).first()
    
    if item_carrinho:
        quantidade_no_carrinho = item_carrinho.quantidade
    else:
        quantidade_no_carrinho = 0

    if request.method == 'POST':
        data = json.loads(request.body)
        valor = data.get('valor')
        
        qtd_carrinho_e_estoque = quantidade_no_carrinho + produto.quantidade_em_estoque
        print(valor)
        print(qtd_carrinho_e_estoque)
        if (int(valor) + quantidade_no_carrinho) > produto.quantidade_em_estoque:
            print(f'o valor selecionado é {valor} e o total disponível é {produto.quantidade_em_estoque}')
            return JsonResponse({'valorMaiorQueDisponivel': True})
        
        else:
            return JsonResponse({'valorMaiorQueDisponivel': False})

    
        
    produto = get_object_or_404(Produto, pk=id)
    form = ItemCarrinho()
    imagens = ProdutoImagem.objects.all()

    return render(request, 'pedidos/product_detail.html', {'produto': produto, 'form': form, 'imagens': imagens})

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