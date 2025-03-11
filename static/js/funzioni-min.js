document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM completamente caricato");

    // 📌 Navbar Sticky
    let navbar = document.querySelector('.navbar');
    if (navbar) {
        let stickyTrigger = document.querySelector('.logo-img')?.offsetHeight || 50;
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('sticky', window.pageYOffset > stickyTrigger);
        });
    }

    // 📌 Chiudi automaticamente gli alert dopo 5 secondi
    setTimeout(function () {
        document.querySelectorAll(".alert").forEach(function (alert) {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);

    // 📌 Blocca il tasto destro e impedisce il trascinamento delle immagini
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.querySelectorAll('img').forEach(img => img.addEventListener('dragstart', e => e.preventDefault()));

    // 📌 Migliora il rendering delle immagini
    document.querySelectorAll(".gallery-img").forEach(img => {
        img.onload = function () {
            requestAnimationFrame(() => img.classList.add("loaded"));
        };
    });

    // 📌 Cookie Banner
    let cookieBanner = document.getElementById('cookie-banner');
    if (cookieBanner && localStorage.getItem('cookiesAccepted') === 'true') {
        cookieBanner.style.display = 'none';
    }

    window.acceptCookies = function () {
        console.log("✅ Cookie accettati");
        localStorage.setItem('cookiesAccepted', 'true');
        if (cookieBanner) {
            cookieBanner.style.display = 'none';
        }
    };

    // 📌 Funzione per filtrare la galleria
    window.filterGallery = function (category) {
        console.log(`📌 Filtrando per categoria: ${category}`);

        document.querySelectorAll('.gallery-item').forEach(item => {
            item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
        });
    };

    // 📌 Mostra tutte le immagini di default nella galleria
    filterGallery('all');

    // 📌 Modale per immagini
    let images = [];
    let currentIndex = 0;

    window.openImageModal = function (event, imageSrc) {
        event.preventDefault();
        let modalElement = document.getElementById("imageModal");
        let modalImage = document.getElementById("modalImage");

        if (!modalElement || !modalImage) return console.error("⚠️ Modale o immagine non trovati!");

        let galleryImages = document.querySelectorAll('.swiper-slide img, .gallery-item img');
        images = Array.from(galleryImages).map(img => img.src);
        currentIndex = images.indexOf(imageSrc);

        if (currentIndex === -1) return console.error("⚠️ Immagine non trovata.");

        let modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modalImage.src = imageSrc;
        modal.show();
    };

    window.prevImage = function () {
        if (images.length > 0) {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
            document.getElementById("modalImage").src = images[currentIndex];
        }
    };

    window.nextImage = function () {
        if (images.length > 0) {
            currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
            document.getElementById("modalImage").src = images[currentIndex];
        }
    };

    // 📌 Caricamento Swiper.js solo dopo il rendering
    requestIdleCallback(() => {
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

}); // 🔴 CHIUSURA CORRETTA DEL `DOMContentLoaded`
