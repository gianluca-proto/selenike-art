// Variabili globali per la gestione del Modale della galleria
let galleryImages = [];
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
    /* ==========================================================
       Inizializzazioni della Navbar (Sticky)
    ========================================================== */
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // Imposta l'altezza della navbar per evitare "jump" in fase di sticky
        navbar.style.height = navbar.offsetHeight + "px";
        const stickyTrigger = document.querySelector('.logo-img')?.offsetHeight || 50;
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > stickyTrigger) {
                navbar.classList.add('sticky');
            } else {
                navbar.classList.remove('sticky');
            }
        });
    }

    /* ==========================================================
       Auto-Chiusura degli Alert
    ========================================================== */
    setTimeout(function () {
        document.querySelectorAll(".alert").forEach(function (alert) {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);

    /* ==========================================================
       Inizializzazione del Lightbox (GLightbox, se presente)
    ========================================================== */
    if (typeof GLightbox !== "undefined") {
        GLightbox({ selector: '.lightbox' });
    }

    /* ==========================================================
       Disabilita il tasto destro e il drag delle immagini
    ========================================================== */
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    }, false);
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('dragstart', function (e) {
            e.preventDefault();
        });
    });

    /* ==========================================================
       Effetto fade-in per il caricamento delle immagini della galleria
    ========================================================== */
    document.querySelectorAll(".gallery-img").forEach(img => {
        img.onload = function () {
            img.classList.add("loaded");
        };
    });

    /* ==========================================================
       Funzione per filtrare la galleria
    ========================================================== */
    window.filterGallery = function (category) {
        document.querySelectorAll('.gallery-item').forEach(item => {
            // Mostra l'elemento se appartiene alla categoria selezionata o se viene richiesto "all"
            item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
        });
    };

    // Visualizza tutte le immagini di default
    filterGallery('all');

    /* ==========================================================
       Gestione dei Cookie: accettazione e banner
    ========================================================== */
    const cookieBanner = document.getElementById('cookie-banner');
    // Nascondi il banner se i cookie sono già stati accettati
    if (cookieBanner && localStorage.getItem('cookiesAccepted') === 'true') {
        cookieBanner.style.display = 'none';
    }
    window.acceptCookies = function () {
        localStorage.setItem('cookiesAccepted', 'true');
        if (cookieBanner) {
            cookieBanner.style.display = 'none';
        }
    };

    /* ==========================================================
       Gestione del Modale per le immagini della galleria
    ========================================================== */
    window.openImageModal = function (event, imageSrc) {
        event.preventDefault();

        const modalElement = document.getElementById("imageModal");
        const modalImage = document.getElementById("modalImage");

        if (!modalElement || !modalImage) {
            console.error("⚠️ Modale o immagine non trovati!");
            return;
        }
        // Verifica che Bootstrap sia disponibile
        if (typeof bootstrap === "undefined") {
            console.error("⚠️ Bootstrap non è caricato! Verifica che sia incluso prima di questo file.");
            return;
        }

        // Cerca tutte le immagini nella galleria e nello Swiper
        const galleryImgs = document.querySelectorAll('.swiper-slide img, .gallery-item img');
        galleryImages = Array.from(galleryImgs).map(img => img.src);

        currentIndex = galleryImages.indexOf(imageSrc);
        if (currentIndex === -1) {
            console.error("⚠️ Immagine non trovata nella lista.");
            return;
        }
        // Utilizza l'istanza esistente o creane una nuova
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modalImage.src = imageSrc;
        modal.show();
    };

    window.prevImage = function () {
        if (galleryImages.length > 0) {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : galleryImages.length - 1;
            document.getElementById('modalImage').src = galleryImages[currentIndex];
        }
    };

    window.nextImage = function () {
        if (galleryImages.length > 0) {
            currentIndex = (currentIndex < galleryImages.length - 1) ? currentIndex + 1 : 0;
            document.getElementById('modalImage').src = galleryImages[currentIndex];
        }
    };

    /* ==========================================================
       Inizializzazione degli Swiper (Carousel)
    ========================================================== */
    document.querySelectorAll(".swiper-container").forEach(swiperEl => {
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
