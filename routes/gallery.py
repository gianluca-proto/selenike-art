import cloudinary
from flask import Blueprint, render_template, request, jsonify, flash, \
    redirect, url_for

from config import validate_image
from services import cloudinary_service
from services.auth import jwt_required
from services.cloudinary_service import get_resources, delete_image, \
    move_image, test_cloudinary_connection
from flask_wtf.csrf import CSRFProtect
from forms.upload_form import UploadForm

bp = Blueprint('gallery', __name__)
csrf = CSRFProtect()

@bp.route('/art-gallery')  # ✅ Route registrata sotto 'gallery'
def art_gallery():
    # Recupera tutte le immagini sotto img/gallery/ senza sottocartelle e con tipo 'image'
    res = get_resources('image', 'img/gallery/')
    images = []
    for img in res:
        public_id = img['filename']
        # Estrai la categoria dal public_id: img/gallery/<categoria>/resto...
        parts = public_id.split('/')
        category = parts[2] if len(parts) > 2 else 'altro'
        images.append({'filename': img['filename'], 'url': img['url'], 'category': category})
    print(f"[DEBUG] Totale immagini trovate: {len(images)}")
    return render_template('gallery.html', images=images)

@bp.route('/art-gallery-debug')
def art_gallery_debug():
    # Recupera tutte le immagini sotto img/gallery/ (senza filtro categoria)
    res = get_resources('image', 'img/gallery/')
    return render_template('gallery.html', images=[{'filename': img['filename'], 'url': img['url'], 'category': 'debug'} for img in res])


@bp.route('/antro-1986/upload', methods=['GET', 'POST'])
@jwt_required
@csrf.exempt
def upload_image():
    form = UploadForm()

    if request.method == 'POST':
        print("🛠 Flask ha ricevuto una richiesta POST!")

        if 'images' not in request.files:
            print("❌ Nessun file trovato in request.files!")
            flash('Nessun file selezionato.', 'danger')
            return redirect(request.url)

        files = request.files.getlist('images')
        print(f"📸 File ricevuti: {[file.filename for file in files]}")

        if not files or files[0].filename == '':
            print("❌ Nessun file valido selezionato!")
            flash('Nessun file selezionato.', 'danger')
            return redirect(request.url)

        for file in files:
            print(f"🔄 Tentativo di upload: {file.filename}")

            upload_result = cloudinary.uploader.upload(
                file,
                folder='img/gallery/altro',
                upload_preset="ml_default",
                format="webp"  # 🚀 Conversione diretta in WebP
            )

            print(f"✅ Upload riuscito: {upload_result}")

            if upload_result.get('secure_url'):
                flash(f'✅ Immagine {file.filename} caricata con successo come WebP!', 'success')
            else:
                flash(f'❌ Caricamento di {file.filename} non riuscito.', 'danger')

        return redirect(url_for('gallery.upload_image'))

    return render_template('antro-1986/upload.html', form=form)



@bp.route('/delete-image/<path:public_id>', methods=['POST'])
@jwt_required  # 🔹 Protegge la cancellazione con JWT
@csrf.exempt
def delete_gallery_image(public_id):
    return jsonify(delete_image(public_id))


import re

@bp.route('/move-image', methods=['POST'])
@jwt_required
@csrf.exempt
def move_image():
    try:
        print("📡 Richiesta ricevuta per spostare un'immagine!")

        # Debug: stampiamo il JSON ricevuto PRIMA della pulizia
        data = request.get_json()
        print("📝 JSON ricevuto:", data)

        if not data:
            return jsonify({"success": False, "message": "⚠️ Nessun dato ricevuto dalla richiesta"}), 400

        src_public_id = data.get('src_public_id')
        dest_public_id = data.get('dest_public_id')

        print(f"🔎 Prima della pulizia: src_public_id = {src_public_id}")
        print(f"🔎 Prima della pulizia: dest_public_id = {dest_public_id}")

        if not src_public_id or not dest_public_id:
            return jsonify({"success": False, "message": "⚠️ Parametri mancanti"}), 400

        # Puliamo i percorsi errati
        src_public_id = re.sub(r'(img/gallery/)+', 'img/gallery/', src_public_id)
        dest_public_id = re.sub(r'(img/gallery/)+', 'img/gallery/', dest_public_id)

        print(f"✅ Dopo la pulizia: src_public_id = {src_public_id}")
        print(f"✅ Dopo la pulizia: dest_public_id = {dest_public_id}")

        response = cloudinary.uploader.rename(src_public_id, dest_public_id)

        if 'public_id' in response:
            print("✅ Spostamento riuscito!")
            return jsonify({'success': True, 'message': f"✅ Spostamento riuscito: {response['public_id']}!"})
        else:
            print("❌ Errore nello spostamento:", response)
            return jsonify({'success': False, 'message': "❌ Errore nello spostamento"}), 500

    except Exception as e:
        print(f"❌ Errore server: {str(e)}")
        return jsonify({'success': False, 'message': f"❌ Errore server: {str(e)}"}), 500



@bp.route('/manage-gallery')
@jwt_required  # 🔹 Protegge la gestione della galleria con login
def manage_gallery():
    categories = ['novita', 'commissioni', 'fanart', 'ideepersonali', 'altro']
    images = {category: get_resources('image', f'img/gallery/{category}/') for category in categories}

    return render_template('antro-1986/manage_gallery.html', images=images, categories=categories)
