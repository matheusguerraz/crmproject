window.addEventListener("DOMContentLoaded", function() {
    document.getElementById("logout-modal").addEventListener("click", function() {
      window.location.href = "{% url 'lista_produtos' %}?logout=true";
      console.log('era pra passar');
    });
  });

