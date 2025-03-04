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
    categories = ['animals', 'comics', 'illustrations']
    images = []
    for category in categories:
        res = get_resources('upload', f'img/gallery/{category}/')
        for img in res:
            images.append({'filename': img['filename'], 'url': img['url'], 'category': category})

    return render_template('gallery.html', images=images)

@bp.route('/admin/upload', methods=['GET', 'POST'])
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
                upload_preset="ml_default"
            )

            print(f"✅ Upload riuscito: {upload_result}")

            if upload_result.get('secure_url'):
                flash(f'✅ Immagine {file.filename} caricata con successo!', 'success')
            else:
                flash(f'❌ Caricamento di {file.filename} non riuscito.', 'danger')

        return redirect(url_for('gallery.upload_image'))

    return render_template('admin/upload.html', form=form)


@bp.route('/delete-image/<path:public_id>', methods=['POST'])
@jwt_required  # 🔹 Protegge la cancellazione con JWT
@csrf.exempt
def delete_gallery_image(public_id):
    return jsonify(delete_image(public_id))

@bp.route('/move-image', methods=['POST'])
@jwt_required
@csrf.exempt
def move_image():
    try:
        print("📡 Richiesta ricevuta per spostare un'immagine!")
        # 🔍 Controlla il tipo di dati ricevuto
        print("📝 Contenuto di request.data:", request.data)
        print("📝 Contenuto di request.get_json():", request.get_json())
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"success": False,
                            "message": "⚠️ Dati ricevuti in un formato non valido"}), 400
        if not data:
            return jsonify({"success": False,
                            "message": "⚠️ Nessun dato ricevuto dalla richiesta"}), 400
        src_public_id = data.get('src_public_id')
        dest_public_id = data.get('dest_public_id')
        if not src_public_id or not dest_public_id:
            return jsonify({"success": False,
                            "message": "⚠️ Parametri mancanti"}), 400
        print(
            f"📂 Spostamento richiesto da {src_public_id} a {dest_public_id}")
        response = cloudinary.uploader.rename(src_public_id,
                                              dest_public_id)
        if 'public_id' in response:
            print("✅ Spostamento riuscito!")
            return jsonify({'success': True,
                            'message': f"✅ Spostamento riuscito: {response['public_id']}!"})
        else:
            print("❌ Errore nello spostamento:", response)
            return jsonify({'success': False,
                            'message': "❌ Errore nello spostamento"}), 500
    except Exception as e:
        print(f"❌ Errore server: {str(e)}")
        return jsonify({'success': False,
                        'message': f"❌ Errore server: {str(e)}"}), 500


@bp.route('/manage-gallery')
@jwt_required  # 🔹 Protegge la gestione della galleria con login
def manage_gallery():
    categories = ['animals', 'comics', 'illustrations', 'altro']
    images = {category: get_resources('upload', f'img/gallery/{category}/') for category in categories}

    return render_template('admin/manage_gallery.html', images=images, categories=categories)
