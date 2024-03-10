document.addEventListener("DOMContentLoaded", function () {
    const navLinks = document.querySelectorAll('ul.topnav li a');
    navLinks.forEach(function (navLink) {
        navLink.addEventListener('click', function (event) {
            navLinks.forEach(function (link) {
                link.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
});
let mybutton = document.getElementById("topBtn");
window.onscroll = function () {
    scrollFunction();
};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}

function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}