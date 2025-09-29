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


def upload_file_to_cloudinary(local_path, folder="stats", keep_name=False):
    """
    Carica un file generico (CSV, log, ecc.) su Cloudinary nella cartella specificata.
    Se keep_name è True, il file viene caricato sempre con lo stesso nome (senza timestamp) e sovrascritto.
    Se keep_name è False, aggiunge un timestamp per evitare sovrascritture (default per altri file non log).
    Restituisce la URL sicura del file caricato.
    """
    import datetime
    cloudinary.config(logging=True)
    try:
        base_name = os.path.basename(local_path)
        if keep_name:
            unique_name = base_name
        else:
            # Aggiungi timestamp al nome file per evitare sovrascritture
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(base_name)
            unique_name = f"{name}_{timestamp}{ext}"
        with open(local_path, "rb") as f:
            upload_result = cloudinary.uploader.upload(
                f,
                folder=folder,
                resource_type="raw",  # Importante per file non immagine
                public_id=f"{folder}/{unique_name}",
                use_filename=True,
                unique_filename=not keep_name,  # Forza unicità solo se non keep_name
                overwrite=keep_name  # Sovrascrivi solo se keep_name
            )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"❌ Errore upload file su Cloudinary: {e}")
        return None


def upload_all_logs_to_cloudinary(log_dir=".", pattern="access.log", folder="logs"):
    """
    Carica tutti i file di log access.log* presenti nella directory specificata su Cloudinary.
    Ogni file viene caricato con lo stesso nome (senza timestamp) e sovrascritto.
    """
    import glob
    import os
    log_files = glob.glob(os.path.join(log_dir, pattern + '*'))
    results = {}
    for file_path in log_files:
        url = upload_file_to_cloudinary(file_path, folder=folder, keep_name=True)
        results[file_path] = url
    return results

def sync_logs_with_cloudinary(log_dir=".", pattern="access.log", folder="logs"):
    """
    Sincronizza i file di log locali con quelli su Cloudinary:
    - Carica solo i file nuovi o modificati (in base a data di modifica locale e nome base).
    - Non sovrascrive mai file già presenti su Cloudinary.
    - Restituisce un dizionario con i file caricati e le rispettive URL.
    """
    import glob
    import os
    import datetime
    # Recupera la lista dei file già presenti su Cloudinary
    cloud_files = get_resources(tipo="raw", prefix=folder)
    cloud_basenames = set()
    for f in cloud_files:
        # Estrai il nome base senza timestamp e senza estensione
        public_id = f['filename']
        # Esempio: logs/access.log_20240928_153000
        base = os.path.basename(public_id)
        if '_' in base:
            base = base.split('_')[0] + os.path.splitext(base)[1]
        cloud_basenames.add(base)
    # Scansiona i file locali
    log_files = glob.glob(os.path.join(log_dir, pattern + '*'))
    results = {}
    for file_path in log_files:
        base_name = os.path.basename(file_path)
        # Se il file base (senza timestamp) non è su Cloudinary, caricalo
        if base_name not in cloud_basenames:
            url = upload_file_to_cloudinary(file_path, folder=folder)
            results[file_path] = url
        else:
            results[file_path] = None  # Già presente, non caricato
    return results

def sync_files_with_cloudinary(local_dir=".", pattern="*.csv", folder="stats"):
    """
    Sincronizza i file locali (es. CSV) con quelli su Cloudinary:
    - Carica solo i file nuovi o modificati (in base a nome base).
    - Non sovrascrive mai file già presenti su Cloudinary.
    - Restituisce un dizionario con i file caricati e le rispettive URL.
    """
    import glob
    import os
    # Recupera la lista dei file già presenti su Cloudinary
    cloud_files = get_resources(tipo="raw", prefix=folder)
    cloud_basenames = set()
    for f in cloud_files:
        public_id = f['filename']
        base = os.path.basename(public_id)
        if '_' in base:
            base = base.split('_')[0] + os.path.splitext(base)[1]
        cloud_basenames.add(base)
    # Scansiona i file locali
    local_files = glob.glob(os.path.join(local_dir, pattern))
    results = {}
    for file_path in local_files:
        base_name = os.path.basename(file_path)
        if base_name not in cloud_basenames:
            url = upload_file_to_cloudinary(file_path, folder=folder)
            results[file_path] = url
        else:
            results[file_path] = None  # Già presente, non caricato
    return results
