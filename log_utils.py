import os

LOG_PATH = 'access.log'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB

def write_log_line(line: str, log_path: str = LOG_PATH, max_size: int = MAX_LOG_SIZE):
    """
    Scrive una riga nel file di log. Se il file supera max_size,
    elimina la prima riga (più vecchia) e aggiunge la nuova in fondo.
    """
    line = line.rstrip('\n') + '\n'
    if not os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(line)
        return
    size = os.path.getsize(log_path)
    if size < max_size:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line)
    else:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Rimuovi la prima riga (più vecchia)
        if lines:
            lines = lines[1:]
        lines.append(line)
        with open(log_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

