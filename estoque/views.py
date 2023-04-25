from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import F
from .models import Produto, Marca
from widget_tweaks.templatetags import widget_tweaks
from .forms import EstoqueForm, MarcaForm
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.core.files.base import ContentFile

def index(request):
    produtos = Produto.objects.all()
    return render(request, 'estoque/index.html', {'produtos': produtos})

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


def cadastrar_produto(request):
    if request.method == 'POST':
        # Processar formulário de cadastro de produto
        product_form = EstoqueForm(request.POST, request.FILES)
        if product_form.is_valid():
            images = request.FILES.getlist('imagens')
            for image in images:
                img = Image.open(image)
                output_size = (300, 300) # Define aqui o tamanho que você quer redimensionar
                img.thumbnail(output_size)
                # Salvar a imagem redimensionada
                thumb_io = BytesIO()
                img.save(thumb_io, img.format, quality=85)
                thumb_io.seek(0)
                image = ContentFile(thumb_io.getvalue(), name=image.name)
                # Atualizar o form com a imagem redimensionada
                product_form.cleaned_data['imagens'] = image
            product = product_form.save()
            sabor = request.POST['sabor']
            product_name = product.produto
            # Mensagem de sucesso para o usuário
            messages.success(request, f"Produto '{product_name}' adicionado com sucesso!")
            # Redirecionar para a página de listagem de produtos
            return redirect(reverse('product_list') + '?success=true&product_name=' + product_name)
    else:
        # Exibir formulário de cadastro de produto
        product_form = EstoqueForm()
    context = {
        'form': product_form,
    }
    return render(request, 'estoque/cadastrar_produto.html', context)


def remover_produto(request, pk):
    produto_para_remover = Produto.objects.get(pk=pk)
    produto_para_remover.delete()
    messages.success(request, f'O produto {produto_para_remover.produto} foi removido com sucesso!')
    return redirect('index')

def modificar_produto(request, pk):
    produto_para_modificar = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = EstoqueForm(request.POST, instance=produto_para_modificar)
        if form.is_valid():
            produto_para_modificar = form.save(commit=False)
            produto_para_modificar.produto = form.cleaned_data['produto']
            produto_para_modificar.quantidade_em_estoque = form.cleaned_data['quantidade_em_estoque']
            produto_para_modificar.estoque_minimo = form.cleaned_data['estoque_minimo']
            produto_para_modificar.save()
            messages.success(request, f'O produto {produto_para_modificar.produto} foi alterado com sucesso!')
            return redirect('index')
    else:
        form = EstoqueForm(instance=produto_para_modificar)
    return render(request, 'estoque/modificar_produto.html', {'produto': produto_para_modificar, 'form': form})

def produtos_em_falta(request):
    todos_produtos = Produto.objects.all()
    produtos_em_falta = todos_produtos.filter(quantidade_em_estoque__lte = F('estoque_minimo'))
    return render(request, 'estoque/index.html', {'produtos': produtos_em_falta})