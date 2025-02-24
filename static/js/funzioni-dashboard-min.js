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

function deleteImage(category, filename) {
    const public_id = `${filename}`;
    if (confirm('Are you sure you want to delete this image?')) {
        fetch(`/delete-image/${encodeURIComponent(public_id)}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(data.success) {
                alert('Image deleted successfully');
                window.location.reload();
            } else {
                alert('Error deleting image: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting image: ' + error.message);
        });
    }
}

function moveImage(selectElement) {
    var fullPath = selectElement.dataset.filename;
    var parts = fullPath.split('/');
    var filename = parts.pop();

    var src_category = selectElement.dataset.category;
    var dest_category = selectElement.value;

    var src_public_id = `img/gallery/${src_category}/${filename}`;
    var dest_public_id = `img/gallery/${dest_category}/${filename}`;

    fetch('/move-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `src_public_id=${encodeURIComponent(src_public_id)}&dest_public_id=${encodeURIComponent(dest_public_id)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if(data.success) {
            location.reload();
        } else {
            alert('Error moving image: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error moving image: ' + error.message);
    });
}

