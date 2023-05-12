window.addEventListener("DOMContentLoaded", function() {

  document.getElementById("logout-modal").addEventListener("click", function(event) {
    if (event.target.classList.contains("logout-btn")) {
      console.log('entrou na condição do js')
      window.location.href = "{% url 'lista_produtos' %}?logout=true";
    }
  });

  document.getElementById("form-login-modal").addEventListener("submit", function(event) {
    // aqui você pode colocar o código para validar os campos do formulário antes de submeter
    console.log('entrou na submissão do form')
  });
});
