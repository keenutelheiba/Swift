// js code for pop up window

// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// js code for pop up window end
// Get the modal and form elements
var modal = document.getElementById("myModal");
var paymentForm = document.getElementById("paymentForm");
var btn = document.getElementById("myBtn");
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
if (btn) {
    btn.onclick = function() {
        modal.style.display = "block";
    }
}

// When the user clicks on <span> (x), close the modal
if (span) {
    span.onclick = function() {
        modal.style.display = "none";
    }
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Handle payment form submission
if (paymentForm) {
    paymentForm.onsubmit = function(e) {
        e.preventDefault();
        
        // Validate required fields
        var payMethod = document.querySelector('input[name="ptype"]:checked');
        var payPhone = document.getElementById("phone").value;
        var trxId = document.getElementById("trxid").value;
        
        if (!payMethod || !payPhone || !trxId) {
            alert("Please fill all required fields");
            return false;
        }
        
        // Submit the form
        this.submit();
    }
}