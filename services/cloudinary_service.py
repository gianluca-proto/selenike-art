import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
import os
import requests
from flask import flash, jsonify, request

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)


def get_resources(resource_type, prefix, type_="upload"):
    try:
        response = cloudinary.api.resources(type=type_, prefix=prefix, max_results=100, resource_type=resource_type)
        if not isinstance(response, dict) or 'resources' not in response:
            return []
        return [
            {'filename': img.get('public_id', ''), 'url': img.get('secure_url', '')}
            for img in response.get('resources', [])
        ]
    except cloudinary.exceptions.Error as e:
        return []
    except Exception as e:
        return []


def test_cloudinary_connection():
    try:
        response = cloudinary.api.ping()
        return True
    except Exception as e:
        return False


def upload_image(file):
    cloudinary.config(logging=True)
    try:
        file_data = io.BytesIO(file.read())
        file_data.seek(0)
        upload_result = cloudinary.uploader.upload(
            file_data,
            folder="img/gallery/altro",
            upload_preset="ml_default",
            api_key=os.getenv("CLOUD_API_KEY")
        )
        if upload_result is None:
            raise ValueError("Upload a Cloudinary fallito: risposta None")
        if upload_result.get('secure_url'):
            flash('✅ Immagine caricata con successo!', 'success')
        else:
            flash('❌ Caricamento non riuscito.', 'danger')
    except Exception as e:
        flash(f'❌ Errore nel caricamento.', 'danger')


def delete_image(public_id):
    response = cloudinary.uploader.destroy(public_id, invalidate=True)
    return {'success': response.get('result') == 'ok'}


def move_image():
    try:
        src_public_id = request.form.get('src_public_id')
        dest_folder = request.form.get('dest_folder')
        if not src_public_id or not dest_folder:
            return jsonify({"success": False, "message": "⚠️ Parametri mancanti"}), 400
        file_name = src_public_id.split("/")[-1]
        dest_public_id = f"{dest_folder}/{file_name}"
        response = cloudinary.uploader.rename(src_public_id, dest_public_id, overwrite=True)
        if "public_id" in response:
            return jsonify({"success": True, "message": f"✅ Spostamento riuscito: {response['public_id']}!"})
        else:
            return jsonify({"success": False, "message": "❌ Errore nello spostamento"}), 500
    except Exception as e:
        print(f"❌ Errore Flask: {str(e)}")
        return jsonify({"success": False, "message": f"❌ Errore server: {str(e)}"}), 500


def upload_file_to_cloudinary(local_path, folder="stats", keep_name=True):
    cloudinary.config(logging=True)
    try:
        base_name = os.path.basename(local_path)
        # Forza sempre lo stesso public_id per visits_history.csv
        if base_name == "visits_history.csv":
            public_id = f"{folder}/visits_history.csv"
        else:
            public_id = f"{folder}/{base_name}"
        with open(local_path, "rb") as f:
            upload_result = cloudinary.uploader.upload(
                f,
                folder=folder,
                resource_type="raw",
                public_id=public_id,
                use_filename=True,
                unique_filename=False,
                overwrite=True  # Forzato overwrite sempre
            )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"❌ Errore upload file su Cloudinary: {e}")
        return None


def upload_all_logs_to_cloudinary(log_dir=".", pattern="access.log", folder="logs"):
    import glob
    import os
    log_files = glob.glob(os.path.join(log_dir, pattern + '*'))
    results = {}
    for file_path in log_files:
        url = upload_file_to_cloudinary(file_path, folder=folder, keep_name=True)
        results[file_path] = url
    return results


def sync_logs_with_cloudinary(log_dir=".", pattern="access.log", folder="logs"):
    import glob
    import os
    import datetime
    log_files = glob.glob(os.path.join(log_dir, pattern + '*'))
    results = {}
    for file_path in log_files:
        url = upload_file_to_cloudinary(file_path, folder=folder, keep_name=True)
        results[file_path] = url
    return results


def sync_files_with_cloudinary(local_dir=".", pattern=None, folder="stats"):
    import os
    file_path = os.path.join(local_dir, "visits_history.csv")
    results = {}
    if os.path.exists(file_path):
        url = upload_file_to_cloudinary(file_path, folder=folder, keep_name=True)
        results[file_path] = url
    return results


def download_file_from_cloudinary(public_id, local_path):
    """Scarica un file raw da Cloudinary e lo salva in local_path. Restituisce True se ok."""
    import requests
    try:
        res = cloudinary.api.resource(public_id, resource_type="raw")
        url = res.get("secure_url")
        if not url:
            return False
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            return True
        return False
    except Exception:
        return False
