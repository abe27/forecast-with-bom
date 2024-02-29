window.onload = function () {

    var show_password = document.getElementById("show-password");
    if (show_password) {
        show_password.addEventListener('click', function () {
            var x = document.getElementById("password");
            x.type = "text";
            var eye = document.querySelectorAll(".feather-eye");
            eye[0].classList.add("d-none");
            var eyeslash = document.querySelectorAll(".feather-eye-slash");
            eyeslash[0].classList.remove("d-none");
        });
    }
    // Hide password
    var hide_password = document.getElementById("hide-password");
    if (hide_password) {
        hide_password.addEventListener('click', function () {
            var x = document.getElementById("password");
            x.type = "password";
            var eye = document.querySelectorAll(".feather-eye");
            eye[0].classList.remove("d-none");
            var eyeslash = document.querySelectorAll(".feather-eye-slash");
            eyeslash[0].classList.add("d-none");
        });
    }
} 
