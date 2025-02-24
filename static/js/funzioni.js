document.addEventListener("DOMContentLoaded", function () {
    // 📌 Navbar Sticky
    let navbar = document.querySelector('.navbar');
    if (navbar) {
        let stickyTrigger = document.querySelector('.logo-img')?.offsetHeight || 50;
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('sticky', window.pageYOffset > stickyTrigger);
        });
    }

    // 📌 Chiudi automaticamente gli alert dopo 5 secondi
    if (typeof jQuery !== "undefined") {
        $(".alert").delay(5000).slideUp(200, function () {
            $(this).alert('close');
        });
    }

    // 📌 Abilita Ekko Lightbox per le immagini con data-toggle="lightbox"
    $(document).on('click', '[data-toggle="lightbox"]', function (event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    });

    // 📌 Blocca il tasto destro per impedire il salvataggio delle immagini
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    }, false);

    // 📌 Impedisce il trascinamento delle immagini
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('dragstart', function (event) {
            event.preventDefault();
        });
    });

    // 📌 Effetto fade-in per il caricamento delle immagini
    document.querySelectorAll(".gallery-img").forEach(img => {
        img.onload = function () {
            img.classList.add("loaded");
        };
    });

    // 📌 Funzione per filtrare la galleria senza ricaricare la pagina
    window.filterGallery = function (category) {
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
        });
    };

    // 📌 Mostra tutte le immagini di default nella galleria
    filterGallery('all');

    // 📌 Modale per visualizzare e scorrere tra le immagini
    let images = [];
    let currentIndex = 0;

    window.openImageModal = function (event, imageSrc) {
        event.preventDefault();
        images = Array.from(document.querySelectorAll('.swiper-slide img, .gallery-item img')).map(img => img.src);
        currentIndex = images.indexOf(imageSrc);

        let modalImage = document.getElementById('modalImage');
        if (modalImage) {
            modalImage.src = imageSrc;
            let modal = new bootstrap.Modal(document.getElementById('imageModal'));
            modal.show();
        }
    };

    window.prevImage = function () {
        if (images.length > 0) {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
            document.getElementById('modalImage').src = images[currentIndex];
        }
    };

    window.nextImage = function () {
        if (images.length > 0) {
            currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
            document.getElementById('modalImage').src = images[currentIndex];
        }
    };

    // 📌 Banner dei Cookie: Nascondi se già accettato
    let cookieBanner = document.getElementById('cookie-banner');
    if (cookieBanner && localStorage.getItem('cookiesAccepted') === 'true') {
        cookieBanner.style.display = 'none';
    }

    // 📌 Funzione globale per accettare i cookie
    window.acceptCookies = function () {
        localStorage.setItem('cookiesAccepted', 'true');
        if (cookieBanner) {
            cookieBanner.style.display = 'none';
        }
    };
});

document.addEventListener("DOMContentLoaded", function () {
    let swipers = document.querySelectorAll(".swiper-container");

    swipers.forEach(swiperEl => {
        new Swiper(swiperEl, {
            slidesPerView: 1,
            spaceBetween: 10,
            loop: true,
            autoplay: {
                delay: 3000,
                disableOnInteraction: false,
            },
            speed: 1000,
            navigation: {
                nextEl: swiperEl.querySelector('.swiper-button-next'),
                prevEl: swiperEl.querySelector('.swiper-button-prev'),
            },
            pagination: {
                el: swiperEl.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                768: {
                    slidesPerView: 3,
                    slidesPerGroup: 1
                }
            }
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    let swipers = document.querySelectorAll(".swiper-container");

    swipers.forEach(swiperEl => {
        new Swiper(swiperEl, {
            slidesPerView: 1,
            spaceBetween: 10,
            loop: true,
            autoplay: {
                delay: 3000,
                disableOnInteraction: false,
            },
            speed: 1000,
            navigation: {
                nextEl: swiperEl.querySelector('.swiper-button-next'),
                prevEl: swiperEl.querySelector('.swiper-button-prev'),
            },
            pagination: {
                el: swiperEl.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                768: {
                    slidesPerView: 3,
                    slidesPerGroup: 1
                }
            }
        });
    });
});

let images = [];
let currentIndex = 0;

function openImageModal(event, imageSrc) {
    event.preventDefault(); // Evita il comportamento predefinito dei link

    let modalElement = document.getElementById("imageModal");
    let modalImage = document.getElementById("modalImage");

    if (!modalElement || !modalImage) {
        console.error("Modal or image element not found!");
        return;
    }

    let modal = new bootstrap.Modal(modalElement);

    // Trova tutte le immagini sia dello Swiper sia della galleria
    let galleryImages = document.querySelectorAll('.gallery-item img, .swiper-slide img');
    images = Array.from(galleryImages).map(img => img.src);

    // Trova l'indice dell'immagine cliccata
    currentIndex = images.indexOf(imageSrc);

    if (currentIndex === -1) {
        console.error("Image not found in the list.");
        return;
    }

    // Imposta la sorgente dell'immagine nel modale
    modalImage.src = imageSrc;
    modal.show();
}
// Funzione per passare all'immagine precedente
function prevImage() {
    if (images.length > 0) {
        currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
        document.getElementById("modalImage").src = images[currentIndex];
    }
}

// Funzione per passare all'immagine successiva
function nextImage() {
    if (images.length > 0) {
        currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
        document.getElementById("modalImage").src = images[currentIndex];
    }
}




