
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Produto, Pedido, ItemPedido, Carrinho, ItemCarrinho, ProdutoImagem
from django.db.models import Q
from .forms import PedidoForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.utils import timezone
from django.contrib import messages


#View da tela inicial
def lista_produtos(request):
    
    #Verifica se existe querystring de pesquisa, e armazena na variável query
    query = request.GET.get('search')

    #Se tiver pesquisa, faz a query no banco pesquisando pelo nome e descrição
    if query:
        produtos = Produto.objects.filter(
            Q(produto__icontains=query) |
            Q(descricao__icontains=query) 
        )

        #Se não tiver resultado, passa o context nothing para exibição do erro 
        if not produtos:
            nothing = True

    #Se não tem pesquisa, faz a query com todos os produtos e imagens para listar ao usuário
    else:

        form = ItemCarrinho()
        produtos = Produto.objects.filter(quantidade_em_estoque__gt=0)
        imagens = ProdutoImagem.objects .all()
        return render(request, 'pedidos/product_list.html', {'produtos': produtos,'imagens': imagens ,'form': form})
    nothing = len(produtos) == 0
    
    #Retorna o template product_list com o context dos produtos e o parâmetro nothing
    return render(request, 'pedidos/product_list.html', {
                                                        'produtos': produtos, 
                                                        'nothing': nothing
                                                        })

@csrf_protect
def detalhes_produto(request, id):

    carrinho = request.carrinho
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

@csrf_exempt
@csrf_protect
def adicionar_produto_carrinho(request):
    if request.method == 'POST' and request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        data = json.loads(request.body)
        valor = data.get('valor')
        print(f'a quantidade inserida botão foi {valor}')
        
        if (int(valor) + item_carrinho.quantidade) > quantidade_estoque:
            return JsonResponse({'quantidade_acima': True})
    
    try:
        carrinho = request.carrinho
        produto_id = request.POST.get('produto_id')
    
        if produto_id is not None:
            produto = get_object_or_404(Produto, pk=produto_id)
            quantidade = int(request.POST.get('quantidade', 1))

            quantidade_estoque = produto.quantidade_em_estoque
            
            # Verifica se o item já existe no carrinho
            item_carrinho, criado = ItemCarrinho.objects.get_or_create(
                carrinho=carrinho,
                produto_id=produto_id,
            )
            
            # Atualiza a quantidade do item se ele já existe no carrinho
            if not criado:
                qtd_carrinho_e_pedido = quantidade + item_carrinho.quantidade
                if qtd_carrinho_e_pedido > quantidade_estoque:
                    return JsonResponse({'quantidade_acima': True})
                
                item_carrinho.quantidade = qtd_carrinho_e_pedido
            else:
                if quantidade > quantidade_estoque:
                    return JsonResponse({'quantidade_acima': True})
                
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
    carrinho_id = request.session.get('carrinho_id')
    if carrinho_id:
        carrinho = Carrinho.objects.get(id=carrinho_id)
    else:
        carrinho = Carrinho.objects.create()
        request.session['carrinho_id'] = carrinho.id
    carrinho = request.carrinho
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


@require_POST
def remover_produto_carrinho(request):
    print('estou entrando na view remover')
    item_id = request.POST.get('item_id')
    if not item_id:
        return redirect('exibir_carrinho')

    carrinho = None
    if request.user.is_authenticated:
        carrinho = get_object_or_404(Carrinho, usuario=request.user)
    else:
        carrinho_id = request.COOKIES.get('carrinho_id')
        if carrinho_id:
            carrinho = get_object_or_404(Carrinho, id=carrinho_id)

    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)
    print(f'o item para ser removido é o {item}')
    item.delete()
    messages.success(request, 'Produto removido do carrinho com sucesso!')
    response = redirect('exibir_carrinho')
    if not request.user.is_authenticated:
        response.set_cookie('carrinho_id', carrinho.id, expires=timezone.now() + timezone.timedelta(days=30))
    return response



@csrf_protect
def atualizar_carrinho(request):
    if request.user.is_authenticated:
        carrinho = Carrinho.objects.get(usuario=request.user)
    else:
        if 'carrinho_temp' not in request.session:
            request.session['carrinho_temp'] = {}
        carrinho = Carrinho(request, request.session['carrinho_temp'])
    items = ItemCarrinho.objects.select_related('produto').filter(carrinho=carrinho)

    total = 0

    if request.method == 'POST':
        print('entrou no post')
        item_id = request.POST.get('item_id')
        quantidade = request.POST.get('quantidade')
        item = ItemCarrinho.objects.filter(id=item_id, carrinho=carrinho).first()
        print(f'item é {item} e quantidade é {quantidade}')
        if item and quantidade is not None:
            try:
                quantidade = int(quantidade)
                print(quantidade)
            except ValueError:
                
                quantidade = 0
                print('entrou no except valueerror')
            if quantidade > 0 and quantidade <= item.produto.quantidade_em_estoque:
                print(f'itemquantidade era {item.quantidade} e quantidade é {quantidade}')

                item.quantidade = quantidade
                item.save()
                messages.success(request, 'Carrinho atualizado com sucesso!')
        return JsonResponse({
            'items': [{
                'id': item.id,
                'quantidade': item.quantidade,
                'preco_unitario': item.produto.preco,
                'preco_total': item.quantidade * item.produto.preco,
            } for item in items],
            'total': total,
        })
        
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

#in construction
def finalizar_pedido(request):
    print('entrou na view')
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
            return JsonResponse({'success': True, 'redirect_url': reverse('lista_produtos')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        if request.user.is_authenticated:
            carrinho = Carrinho.objects.get(usuario=request.user)
            if carrinho.itens.count() > 0:
                form = PedidoForm(initial={
                    'nome': request.user.nome,
                    'email': request.user.email,
                })
                return render(request, 'pedidos/finalize_order_modal.html', {'form': form})
            else:
                return JsonResponse({'success': False, 'errors': {'carrinho': 'Carrinho vazio'}})
        else:
            return JsonResponse({'success': False, 'errors': {'login': 'Faça login para continuar'}})

#in construction
def sucesso_pedido(request):
    return render(request, 'pedidos/product_list.html')