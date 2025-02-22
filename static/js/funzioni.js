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
        images = Array.from(document.querySelectorAll('.gallery-item img')).map(img => img.src);
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
    let carousels = document.querySelectorAll(".carousel");

    carousels.forEach(carousel => {
        let carouselInner = carousel.querySelector(".carousel-inner");
        let items = Array.from(carouselInner.children);

        if (items.length > 3) {
            // **Cloniamo le prime 3 immagini e le aggiungiamo alla fine**
            items.slice(0, 3).forEach(item => {
                let clone = item.cloneNode(true);
                clone.classList.remove("active");
                carouselInner.appendChild(clone);
            });

            // **Loop infinito senza scatti**
            carousel.addEventListener("slid.bs.carousel", function () {
                let activeItem = carouselInner.querySelector(".carousel-item.active");
                let activeIndex = [...carouselInner.children].indexOf(activeItem);

                if (activeIndex >= items.length) {
                    setTimeout(() => {
                        $(carousel).carousel(0);
                    }, 500);
                }
            });

            // **Auto-play infinito senza blocchi**
            $(carousel).carousel({
                interval: 3000, // Cambia immagine ogni 3 secondi
                wrap: false
            });
        }
    });
});
