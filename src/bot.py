import os
import json
import requests
from bs4 import BeautifulSoup


TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
CHAT_ID = os.environ.get("CHAT_ID")

URL = "https://fiesc.pandape.infojobs.com.br/"
FILE_PATH = "src/last_job.json"

#==================================================
# Para evitar spam - manter registro da última vaga
#==================================================
def load_last_job():
    """Carrega a última vaga vista do arquivo JSON."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_last_job(job):
    """Salva a última vaga vista no arquivo JSON."""
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(job, f)

#================================================
# Enviar notificação para o Telegram
#================================================

def send_telegram_notification(message):
    """Envia uma mensagem formatada em HTML para o telegram"""
    if not TOKEN_TELEGRAM or not CHAT_ID:
        print("Erro: Credenciais do Telegram não encontradas no ambiente.")
        return

    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url,json=payload)
        response.raise_for_status()

    except Exception as e:
        print(f"Erro ao enviar para o telegram: {e}")


# Web Scraping
def check_new_jobs():
    print("Iniciando verificação de novas vagas FIESC.....") 

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(URL,headers=headers)
        response.raise_for_status()

    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    cards_jobs = soup.find_all("a", class_="card card-vacancy")
    print(f"Total de vagas lidas na página: {len(cards_jobs)}")

    jobs_view = load_last_job() or []
    new_jobs_find = False

    for card in cards_jobs:
        link_relative = card.get('href')
        if not link_relative:
            continue

        # Extrai id do link ou usa o próprio link relativo como identificador
        parts = [p for p in link_relative.split('/') if p]
        id_job = parts[-1] if parts else link_relative

        if id_job not in jobs_view:
            title_tag = card.find("h3")
            title = title_tag.text.strip() if title_tag else "Título não encontrado"

            link_complete = f"https://fiesc.pandape.infojobs.com.br{link_relative}"

            icon_local = card.find("i", class_="icon-location-pin-1")
            if icon_local and icon_local.parent and icon_local.parent.parent:
                location = icon_local.parent.text.strip()
            else:
                location = "Localização não encontrada"

            message = f"Nova vaga encontrada:\n\n<b>{title}</b>\n\nLocal: {location}\n\n<a href='{link_complete}'>Clique aqui para ver a vaga</a>"

            send_telegram_notification(message)
            jobs_view.append(id_job)
            new_jobs_find = True

            print(f"Nova vaga encontrada: {title} - {location} - {link_complete}")

    if new_jobs_find:
        save_last_job(jobs_view)
        print("Vagas atualizadas no arquivo JSON.")
    else:
        print("Nenhuma nova vaga encontrada.")





if __name__ == "__main__":
    check_new_jobs()