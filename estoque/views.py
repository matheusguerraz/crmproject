from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import F
from .models import Produto, Marca, ProdutoImagem
from .forms import EstoqueForm, MarcaForm, ProdutoImagemForm
from django.contrib.auth.decorators import login_required

# Funções do CRUD da marca do sistema
def cadastrar_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            mensagem = 'Marca cadastrada com sucesso!'
            return render(request, 'marca/cadastrar_marca.html', {'form': form, 'mensagem': mensagem})
    else:
        form = MarcaForm()
    return render(request, 'marca/cadastrar_marca.html', {'form': form})

def listar_marcas(request):
    marcas = Marca.objects.all()
    return render(request, 'marca/listar_marcas.html', {'marcas': marcas})

def cadastrar_marca(request):
    form = MarcaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Marca cadastrada com sucesso.')
        return redirect('listar_marcas')
    return render(request, 'marca/cadastrar_marca.html', {'form': form})

def editar_marca(request, pk):
    marca_para_editar = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca_para_editar)
        if form.is_valid():
            marca_para_editar = form.save(commit=False)
            marca_para_editar.nome = form.cleaned_data['nome']
            marca_para_editar.descricao = form.cleaned_data['descricao']
            marca_para_editar.save()
            messages.success(request, f'A marca {marca_para_editar.produto} foi alterada com sucesso!')
            return redirect('listar_marcas')
    else:
        form = MarcaForm(instance=marca_para_editar)
    return render(request, 'marca/modificar_marca.html', {'produto': marca_para_editar, 'form': form})

@login_required
def deletar_marca(request, pk):
    marca_para_deletar = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        if 'confirmado' in request.GET:
            marca_para_deletar.delete()
            messages.success(request, f'A marca {marca_para_deletar.nome} foi excluída com sucesso!')
            return redirect('listar_marcas')
    else:
        return render(request, 'marca/confirmar_exclusao_marca.html', {'marca': marca_para_deletar})





def remover_produto(request, pk):
    produto_para_remover = Produto.objects.get(pk=pk)
    produto_para_remover.delete()
    messages.success(request, f'O produto {produto_para_remover.produto} foi removido com sucesso!')
    return redirect('index')

def modificar_produto(request, pk):
    produto_para_modificar = get_object_or_404(Produto, pk=pk)
    imagem_para_modificar = produto_para_modificar.imagem_produto
    if request.method == 'POST':
        form = EstoqueForm(request.POST, instance=produto_para_modificar)
        imagem_form = ProdutoImagemForm(request.POST, request.FILES, instance=imagem_para_modificar)
        if form.is_valid() and imagem_form.is_valid():
            produto_para_modificar = form.save(commit=False)
            produto_para_modificar.save()
            imagem_para_modificar = imagem_form.save(commit=False)
            imagem_para_modificar.produto = produto_para_modificar
            imagem_para_modificar.save()
            messages.success(request, f'O produto {produto_para_modificar.produto} foi alterado com sucesso!')
            return redirect('index')
    else:
        form = EstoqueForm(instance=produto_para_modificar)
        imagem_form = ProdutoImagemForm(instance=imagem_para_modificar)
    return render(request, 'estoque/modificar_produto.html', {'produto': produto_para_modificar, 'form': form, 'imagem_form': imagem_form})


def produtos_em_falta(request):
    todos_produtos = Produto.objects.all()
    produtos_em_falta = todos_produtos.filter(quantidade_em_estoque__lte = F('estoque_minimo'))
    return render(request, 'estoque/index.html', {'produtos': produtos_em_falta})

def cadastrar_produto(request):
    if request.method == 'POST':
        produto_form = EstoqueForm(request.POST)
        imagem_form = ProdutoImagemForm(request.POST, request.FILES)
        if produto_form.is_valid() and imagem_form.is_valid():
            produto = produto_form.save()
            produto.save()
            for imagem in request.FILES.getlist('imagem'):
                ProdutoImagem.objects.create(imagem=imagem, produto=produto)
            mensagem = 'Produto adicionado com sucesso!'
            messages.success(request, mensagem)
            return redirect('index')
        else:
            messages.error(request, "Houve um erro ao adicionar o produto. Verifique os campos abaixo.")
    else:
        produto_form = EstoqueForm()
        imagem_form = ProdutoImagemForm()
    return render(request, 'estoque/cadastrar_produto.html', {'produto_form': produto_form, 'imagem_form': imagem_form})

    

def index(request):
    produtos = Produto.objects.all()
    produto_adicionado = request.COOKIES.get('produto_adicionado', False)
    response = render(request, 'estoque/index.html', {'produtos': produtos, 'produto_adicionado': produto_adicionado})
    
    if produto_adicionado:
        response.delete_cookie('produto_adicionado')
    return response


