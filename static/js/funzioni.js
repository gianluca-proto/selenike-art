document.addEventListener("DOMContentLoaded", function() {
    var navbar = document.querySelector('.navbar');
    var stickyTrigger = document.querySelector('.logo-img').offsetHeight;

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > stickyTrigger) {
            navbar.classList.add('sticky');
        } else {
            navbar.classList.remove('sticky');
        }
    });
});

$(document).ready(function() {
    $(".alert").delay(5000).slideUp(200, function() {
        $(this).alert('close');
    });
});

$(document).on('click', '[data-toggle="lightbox"]', function(event) {
    event.preventDefault();
    $(this).ekkoLightbox();
});

// Disable right-click on the mouse
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
}, false);

// Prevent image drag and drop
$('img').on('dragstart', function(event) {
    event.preventDefault();
});

function filterGallery(category) {
    var items = document.getElementsByClassName('gallery-item');
    for (var i = 0; i < items.length; i++) {
        if (category === 'all' || items[i].classList.contains(category)) {
            items[i].style.display = 'block';
        } else {
            items[i].style.display = 'none';
        }
    }
}

function acceptCookies() {
    document.getElementById('cookie-banner').style.display = 'none';
    localStorage.setItem('cookiesAccepted', 'true');
}

if (localStorage.getItem('cookiesAccepted') === 'true') {
    document.getElementById('cookie-banner').style.display = 'none';
}

filterGallery('all'); // Show all items by default
