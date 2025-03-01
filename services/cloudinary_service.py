import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)

def get_resources(tipo, prefix):
    """ Recupera le immagini da Cloudinary. """
    try:
        response = cloudinary.api.resources(type=tipo, prefix=prefix, max_results=100)
        return [{'filename': img.get('public_id', ''), 'url': img.get('secure_url', '')} for img in response.get('resources', [])]
    except Exception as e:
        print(f"❌ Errore nel recupero delle immagini ({prefix}): {str(e)}")
        return []

def upload_image(file):
    return cloudinary.uploader.upload(file, folder='img/gallery/altro', format='webp')

def delete_image(public_id):
    response = cloudinary.uploader.destroy(public_id, invalidate=True)
    return {'success': response.get('result') == 'ok'}

def move_image(src_public_id, dest_public_id):
    response = cloudinary.uploader.rename(src_public_id, dest_public_id)
    return {'success': 'error' not in response}
