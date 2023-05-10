const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

async function enviarRequisicaoAJAX(event, valor) {
    const path = window.location.pathname;
    const match = path.match(/\/produto\/(\d+)\//);
    const id = match ? match[1] : null;
    if (!id) {
        console.error('ID não encontrado na URL.');
        return;
    }
    
    // Envia uma requisição AJAX para o backend com o valor inserido pelo usuário
    const response = await fetch(`/produto/${id}/`, {
        method: 'POST',
        body: JSON.stringify({valor: valor}),
        headers: {'Content-Type': 'application/json',
                  'X-CSRFToken': csrftoken,
                  }
    });
    
    const data = await response.json();

    // Verifica se o valor é maior do que o disponível
    if (data.valorMaiorQueDisponivel) {
        // Exibe a mensagem de erro para o usuário
        $('#modal_estoque_insuficiente').modal('show');
        return true;
    } else {
        // Oculta a mensagem de erro
        return false;
    }
}

// Listener do input quantidade
const inputElement = document.getElementById('quantidade');
inputElement.addEventListener('input', async function() {
    const valor = inputElement.value;
    await enviarRequisicaoAJAX(null, valor);
});

// Listener do botão adicionar carrinho
const botaoAdicionarCarrinho = document.getElementById('btn-adicionar-carrinho');
botaoAdicionarCarrinho.addEventListener('click', async function(event) {
    event.preventDefault();
    const valor = inputElement.value;
    const valorMaiorQueDisponivel = await enviarRequisicaoAJAX(event, valor);
    if (valorMaiorQueDisponivel) {
        console.log('Deveria bloquear');
        event.preventDefault();
    } else {
        console.log('Deveria adicionar ao carrinho');
        botaoAdicionarCarrinho.form.submit();
    }
});







///////////////////////////////////////////AJAX PARA O BOTÃO DE ADICIONAR AO CARRINHO   
                                             ///////////////////////////////////////////////
/* const btnAdicionarCarrinho = document.querySelector('#btn-adicionar-carrinho');

btnAdicionarCarrinho.addEventListener('click', function() {
        event.preventDefault(); 
    const valor = document.getElementById('quantidade').value;
    const url = '/file-traffic/';
    fetch(url, {
        method: 'POST',
        body: JSON.stringify({valor: valor}),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.pode_adicionar) {
            // Se pode adicionar, redireciona o usuário para o carrinho
            window.location.href = '/carrinho/';
        } else {
            // Se não pode adicionar, exibe a modal de erro
            $('#modal_estoque_insuficiente').modal('show');
        }
    });
});
                                             
 */