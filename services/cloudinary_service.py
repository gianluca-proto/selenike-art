import cloudinary.uploader
import cloudinary.api
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import requests
from flask import request, jsonify
import cloudinary.uploader

from flask import flash, request, jsonify

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)

def get_resources(tipo, prefix):
    try:
        response = cloudinary.api.resources(type=tipo, prefix=prefix, max_results=100)
        return [{'filename': img.get('public_id', ''), 'url': img.get('secure_url', '')} for img in response.get('resources', [])]
    except Exception as e:
        print(f"❌ Errore nel recupero delle immagini ({prefix}): {str(e)}")
        return []


def test_cloudinary_connection():
    url = f"https://api.cloudinary.com/v1_1/{cloudinary.config().cloud_name}/ping"
    try:
        response = requests.get(url)
        print(f"🌐 Stato connessione Cloudinary: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione a Cloudinary: {e}")
        return False


def upload_image(file):
    cloudinary.config(logging=True)  # Abilita il logging avanzato di Cloudinary

    try:
        file_data = io.BytesIO(file.read())  # Clona il file in memoria
        file_data.seek(0)  # Reset puntatore

        print("🔄 Tentativo di upload su Cloudinary...")

        cloudinary.config(logging=True)  # Abilita il logging

        upload_result = cloudinary.uploader.upload(
            file_data,
            folder="img/gallery/altro",
            upload_preset="ml_default",
            api_key=os.getenv("CLOUD_API_KEY")
            # Passiamo l'API Key esplicitamente
        )
        print(f"📌 Cloudinary Response: {upload_result}")
        print(f"✅ Upload riuscito: {upload_result.get('secure_url')}")

        print(f"✅ Risultato upload: {upload_result}")  # Stampa il risultato dell'upload

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

        # Estrarre il nome del file dall'ID pubblico
        file_name = src_public_id.split("/")[-1]  # Ottiene solo il nome del file

        # Nuovo percorso completo
        dest_public_id = f"{dest_folder}/{file_name}"

        # Spostamento con rename e `to_folder`
        response = cloudinary.uploader.rename(src_public_id, dest_public_id, overwrite=True)

        if "public_id" in response:
            return jsonify({"success": True, "message": f"✅ Spostamento riuscito: {response['public_id']}!"})
        else:
            return jsonify({"success": False, "message": "❌ Errore nello spostamento"}), 500

    except Exception as e:
        print(f"❌ Errore Flask: {str(e)}")
        return jsonify({"success": False, "message": f"❌ Errore server: {str(e)}"}), 500


def upload_file_to_cloudinary(local_path, folder="stats"):
    """
    Carica un file generico (CSV, log, ecc.) su Cloudinary nella cartella specificata.
    Restituisce la URL sicura del file caricato.
    """
    cloudinary.config(logging=True)
    try:
        with open(local_path, "rb") as f:
            upload_result = cloudinary.uploader.upload(
                f,
                folder=folder,
                resource_type="raw",  # Importante per file non immagine
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"❌ Errore upload file su Cloudinary: {e}")
        return None


def upload_all_logs_to_cloudinary(log_dir=".", pattern="access.log", folder="logs"):
    """
    Carica tutti i file di log access.log* presenti nella directory specificata su Cloudinary.
    """
    import glob
    import os
    log_files = glob.glob(os.path.join(log_dir, pattern + '*'))
    results = {}
    for file_path in log_files:
        url = upload_file_to_cloudinary(file_path, folder=folder)
        results[file_path] = url
    return results
