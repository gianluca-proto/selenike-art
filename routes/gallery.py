import cloudinary
from flask import Blueprint, render_template, request, jsonify, flash
from services.cloudinary_service import get_resources, delete_image, move_image
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
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        # Implementare la funzione di upload su Cloudinary
        flash('Immagine caricata con successo!', 'success')
    return render_template('admin/upload.html', form=form)

@bp.route('/delete-image/<path:public_id>', methods=['POST'])
def delete_gallery_image(public_id):
    return jsonify(delete_image(public_id))

@bp.route('/move-image', methods=['POST'])
def move_gallery_image():
    return jsonify(move_image(request.form.get('src_public_id'), request.form.get('dest_public_id')))

@bp.route('/manage-gallery')
def manage_gallery():
    categories = ['animals', 'comics', 'illustrations', 'altro']
    images = {}
    for category in categories:
        # Assicurati che 'prefix' sia correttamente specificato
        res = cloudinary.api.resources(type='upload', prefix=f'img/gallery/{category}/', max_results=100)
        if res.get('resources'):
            images[category] = [{'filename': img['public_id'], 'url': img['secure_url']} for img in res['resources']]
        else:
            print(f"No images found in category: {category}")
            images[category] = []
    return render_template('admin/manage_gallery.html', images=images, categories=categories)
