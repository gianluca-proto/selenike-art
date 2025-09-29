print('[DEBUG] Modulo cloudinary_service.py caricato')

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

# Log di debug per le variabili d'ambiente (senza secret)
print(f"[DEBUG] CLOUD_NAME: {os.getenv('CLOUD_NAME')}")
print(f"[DEBUG] CLOUD_API_KEY: {os.getenv('CLOUD_API_KEY')}")


def get_resources(resource_type, prefix, type_="upload"):
    try:
        response = cloudinary.api.resources(type=type_, prefix=prefix, max_results=100, resource_type=resource_type)
        # Verifica che la risposta sia un dict e contenga 'resources'
        if not isinstance(response, dict) or 'resources' not in response:
            print(f"❌ Risposta inattesa da Cloudinary per il prefisso '{prefix}': {response}")
            # Se la risposta è HTML, mostra solo un estratto
            if isinstance(response, str) and response.strip().startswith('<!DOCTYPE html'):
                print(f"[DEBUG] Estratto risposta HTML: {response[:120]} ...")
            return []
        return [
            {'filename': img.get('public_id', ''), 'url': img.get('secure_url', '')}
            for img in response.get('resources', [])
        ]
    except cloudinary.exceptions.Error as e:
        # Gestione errori di parsing server response (404) o HTML
        msg = str(e)
        if 'Error parsing server response' in msg and '404' in msg:
            print(f"⚠️ Cartella o risorsa non trovata su Cloudinary per il prefisso '{prefix}' (404). Probabile cartella vuota o inesistente.")
            return []
        if hasattr(e, 'http_status') and e.http_status == 404:
            print(f"⚠️ Nessuna risorsa trovata o cartella inesistente su Cloudinary per il prefisso '{prefix}'")
        else:
            print(f"❌ Errore nel recupero delle immagini ({prefix}): {msg}")
        return []
    except Exception as e:
        import traceback
        print(f"❌ Errore sconosciuto nel recupero delle immagini ({prefix}): {str(e)}")
        traceback.print_exc()
        return []


def test_cloudinary_connection():
    print("[DEBUG] Avvio test_cloudinary_connection...")
    try:
        response = cloudinary.api.ping()
        print(f"🌐 Stato connessione Cloudinary: {response}")
        return True
    except Exception as e:
        import traceback
        print(f"❌ Errore Cloudinary: {e}")
        traceback.print_exc()
        return False


def upload_image(file):
    cloudinary.config(logging=True)
    try:
        file_data = io.BytesIO(file.read())
        file_data.seek(0)
        print("🔄 Tentativo di upload su Cloudinary...")
        cloudinary.config(logging=True)
        upload_result = cloudinary.uploader.upload(
            file_data,
            folder="img/gallery/altro",
            upload_preset="ml_default",
            api_key=os.getenv("CLOUD_API_KEY")
        )
        print(f"📌 Cloudinary Response: {upload_result}")
        print(f"✅ Upload riuscito: {upload_result.get('secure_url')}")
        print(f"✅ Risultato upload: {upload_result}")
        if upload_result is None:
            raise ValueError("❌ Upload a Cloudinary fallito: risposta None")
        if upload_result.get('secure_url'):
            flash('✅ Immagine caricata con successo!', 'success')
        else:
            flash('❌ Caricamento non riuscito.', 'danger')
    except Exception as e:
        print(f"❌ Errore Cloudinary: {str(e)}")
        flash(f'❌ Errore nel caricamento: {str(e)}', 'danger')


def delete_image(public_id):
    response = cloudinary.uploader.destroy(public_id, invalidate=True)
    return {'success': response.get('result') == 'ok'}


def move_image():
    try:
        src_public_id = request.form.get('src_public_id')
        dest_folder = request.form.get('dest_folder')
        print(f"📂 Spostamento ricevuto: {src_public_id} → {dest_folder}")
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


def upload_file_to_cloudinary(local_path, folder="stats", keep_name=False):
    import datetime
    cloudinary.config(logging=True)
    try:
        base_name = os.path.basename(local_path)
        if keep_name:
            unique_name = base_name
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(base_name)
            unique_name = f"{name}_{timestamp}{ext}"
        with open(local_path, "rb") as f:
            upload_result = cloudinary.uploader.upload(
                f,
                folder=folder,
                resource_type="raw",
                public_id=f"{folder}/{unique_name}",
                use_filename=True,
                unique_filename=not keep_name,
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


def sync_files_with_cloudinary(local_dir=".", pattern="*.csv", folder="stats"):
    import glob
    import os
    local_files = glob.glob(os.path.join(local_dir, pattern))
    results = {}
    for file_path in local_files:
        url = upload_file_to_cloudinary(file_path, folder=folder, keep_name=True)
        results[file_path] = url
    return results
