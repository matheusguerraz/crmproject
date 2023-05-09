
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Produto, Pedido, ItemPedido, Carrinho, ItemCarrinho, ProdutoImagem
from .forms import PedidoForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.contrib import messages

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

@login_required
def adicionar_produto_carrinho(request):

    try:
        carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
        produto_id = request.POST.get('produto_id').strip()
        if produto_id is not None:
            produto = get_object_or_404(Produto, pk=produto_id)
            quantidade = int(request.POST.get('quantidade', 1))

            if quantidade > produto.quantidade_em_estoque:
                quantidade_insuficiente = True
                print(f'caiu na condição {produto.produto}')
                return render(request, 'pedidos/lista_produtos.html', {'quantidade_insuficiente': quantidade_insuficiente})

            elif not criado:
                item_carrinho, criado = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto_id=produto_id)
                qtd_carrinho_e_pedido = quantidade + item_carrinho.quantidade

                if qtd_carrinho_e_pedido > produto.quantidade_em_estoque:
                    messages.error(request, f'Você já possui {produto.produto} no carrinho, e a quantidade ultrapassou a disponível em estoque.')

                item_carrinho.quantidade += quantidade
                item_carrinho.full_clean()
                item_carrinho.save()
                print(f'o produto {item_carrinho.produto} foi aumentado em {quantidade}')
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

        next_url = request.GET.get('next', reverse('exibir_carrinho'))
        return redirect(next_url)
    except Exception as e:
        print(f'O erro foi o {e}')
        return HttpResponseServerError(str(e))


@login_required
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



@login_required
def remover_produto_carrinho(request):
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
@login_required
def detalhes_produto(request, id):
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