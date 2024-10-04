function openModal(image) {
    var modal = document.getElementById("modal");
    var modalImage = document.getElementById("modalImage");
  
    modal.style.display = "block";
    modalImage.src = image.src;
  }
  
  function closeModal() {
    var modal = document.getElementById("modal");
    modal.style.display = "none";
  }
  

  