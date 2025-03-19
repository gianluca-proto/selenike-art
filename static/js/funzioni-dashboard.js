$(document).ready(function() {
    $(".alert").delay(5000).slideUp(200, function() {
        $(this).alert('close');
    });

    $(document).on('click', '[data-toggle="lightbox"]', function(event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    });

    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    }, false);

    $('img').on('dragstart', function(event) {
        event.preventDefault();
    });
});

function filterGallery(category) {
    var items = document.getElementsByClassName('gallery-item');
    Array.from(items).forEach(item => {
        item.classList.remove('show');
        if (category === 'all' || item.classList.contains(category)) {
            item.classList.add('show');
        }
    });
}

function acceptCookies() {
    localStorage.setItem('cookiesAccepted', 'true');
    document.getElementById('cookie-banner').style.display = 'none';
}

window.onload = function() {
    if (localStorage.getItem('cookiesAccepted') === 'true') {
        document.getElementById('cookie-banner').style.display = 'none';
    }
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function deleteImage(category, filename) {
    const public_id = `${filename}`;

    Swal.fire({
        title: "Sei sicuro?",
        text: "Questa azione è irreversibile!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sì, elimina!",
        cancelButtonText: "Annulla"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-image/${encodeURIComponent(public_id)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => {
                console.log("📡 Risposta ricevuta:", response);
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(`Errore HTTP ${response.status}: ${text}`); });
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Risultato eliminazione:", data);
                if (data.success) {
                    Swal.fire({
                        title: "Eliminata!",
                        text: "L'immagine è stata eliminata con successo.",
                        icon: "success",
                        confirmButtonColor: "#3085d6"
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Errore!",
                        text: "Non è stato possibile eliminare l'immagine.",
                        icon: "error",
                        confirmButtonColor: "#d33"
                    });
                }
            })
            .catch(error => {
                console.error("❌ Errore Fetch:", error);
                Swal.fire({
                    title: "Errore di connessione!",
                    text: error.message,
                    icon: "error",
                    confirmButtonColor: "#d33"
                });
            });
        }
    });
}


function moveImage(selectElement) {
    // Il valore già contiene il percorso completo
    var filename = selectElement.dataset.filename; // es: "img/gallery/commissioni/images_tulthh"
    var currentCategory = selectElement.dataset.category; // es: "commissioni"
    var dest_category = selectElement.value; // es: "ideepersonali"

    console.log("🔍 Debug Frontend: filename:", filename);
    console.log("🔍 Debug Frontend: currentCategory:", currentCategory);
    console.log("🔍 Debug Frontend: dest_category:", dest_category);

    // Usa il filename così com'è come src_public_id
    var src_public_id = filename;

    // Per creare il dest_public_id, sostituisci la parte della categoria in filename
    var parts = filename.split('/');
    // Assumiamo che filename abbia la forma: "img/gallery/{oldCategory}/{rest}"
    if (parts.length >= 4) {
        // Sostituisci la terza parte (indice 2) con la nuova categoria
        parts[2] = dest_category;
        var dest_public_id = parts.join('/');
    } else {
        // Fallback se la struttura non è quella attesa
        var dest_public_id = `img/gallery/${dest_category}/${filename}`;
    }

    console.log("📂 src_public_id inviato al backend:", src_public_id);
    console.log("📂 dest_public_id inviato al backend:", dest_public_id);

    if (src_public_id === dest_public_id) {
        Swal.fire({
            title: "⚠️ Attenzione!",
            text: "L'immagine è già in questa categoria!",
            icon: "warning",
            confirmButtonColor: "#3085d6"
        });
        return;
    }

    Swal.fire({
        title: "Sicuro di voler spostare l'immagine?",
        text: `L'immagine verrà spostata da ${currentCategory} a ${dest_category}.`,
        icon: "question",
        showCancelButton: true,
        confirmButtonColor: "#28a745",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sì, sposta!",
        cancelButtonText: "Annulla"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/move-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    src_public_id: src_public_id,
                    dest_public_id: dest_public_id
                })
            })
            .then(response => {
                console.log("📡 Risposta ricevuta:", response);
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(`Errore HTTP ${response.status}: ${text}`); });
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Risultato spostamento:", data);
                if (data.success) {
                    Swal.fire({
                        title: "Spostato!",
                        text: "L'immagine è stata spostata con successo.",
                        icon: "success",
                        confirmButtonColor: "#3085d6"
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Errore!",
                        text: "Non è stato possibile spostare l'immagine.",
                        icon: "error",
                        confirmButtonColor: "#d33"
                    });
                }
            })
            .catch(error => {
                console.error("❌ Errore Fetch:", error);
                Swal.fire({
                    title: "Errore di connessione!",
                    text: error.message,
                    icon: "error",
                    confirmButtonColor: "#d33"
                });
            });
        }
    });
}

