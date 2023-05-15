function getParameterByName(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  }
  
    $(document).ready(function() {
        console.log(getParameterByName('produto_adicionado')); // adicione essa linha
    
        if (getParameterByName('produto_adicionado') === 'true') {
        $('#modal_produto_adicionado').modal('show');
        history.replaceState(null, '', window.location.pathname + '?produto_adicionado=false');
        }
    });
    
document.querySelectorAll('.quantidade-botao').forEach(botao => {
    botao.addEventListener('click', event => {
    event.preventDefault();

const campoQuantidade = document.querySelector(`#quantidade-${botao.dataset.itemId}`);
const quantidadeAtual = parseInt(campoQuantidade.value);
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // obtém o token CSRF do input

const novaQuantidade = botao.dataset.operacao === 'adicionar' ? quantidadeAtual + 1 : quantidadeAtual - 1;
if (novaQuantidade < 1 || novaQuantidade > parseInt(campoQuantidade.max)) {
return;
}
campoQuantidade.value = novaQuantidade;
const url = '/atualizar-carrinho/'
const formData = new FormData();
formData.append('quantidade{{ item.id }}', novaQuantidade);
formData.append('item_id', botao.dataset.itemId);

fetch(url, {
method: 'POST',
body: formData,
headers: {
'X-CSRFToken':  csrfToken
}
})
.then(response => {
if (response.ok) {
return response.json();
}
throw new Error('Erro ao enviar dados');
})
.then(data => {
console.log(data);
location.reload(true);
// faça algo com a resposta da view
})

})
});