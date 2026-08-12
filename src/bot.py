import os
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
CHAT_ID = os.environ.get("CHAT_ID")
MESES_PT = {
    1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
    7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"
}
HOME_OFFICE = ["home office", "remoto", "trabalho remoto", "teletrabalho", "trabalho à distância"]

COMPANIES = {

    "fiesc": {
        "url": "https://fiesc.pandape.infojobs.com.br/",
        "file": os.path.join(os.path.dirname(os.path.abspath(__file__)),"last_job_fiesc.json"),
    },
    "iel": {
        "url": "https://iel.pandape.infojobs.com.br/",
        "file": os.path.join(os.path.dirname(os.path.abspath(__file__)),"last_job_iel.json"),
    },
}

#======================================================
# Captura a data atual e formata para o padrão do site
#======================================================
def get_current_date():
    """Retorna a data atual formatada como 'dd mmm' (ex: '30 jul')."""
    today = datetime.now()
    return f"{today.day} {MESES_PT[today.month]}" 


#==================================================
# Para evitar spam - manter registro da última vaga
#==================================================
def load_last_job(file_path):
    """Carrega a última vaga vista do arquivo JSON."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_last_job(job,file_path):
    """Salva a última vaga vista no arquivo JSON."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(job, f)

#=====================================
# Enviar notificação para o Telegram
#=====================================
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
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

    except Exception as e:
        print(f"Erro ao enviar para o telegram: {e}")


#=======================
# Realiza o Web Scraping
#=======================

def fetch_jobs_page(url, company_name):
    """Faz a requisição da página de vagas e retorna o conteúdo HTML."""
    print(f"Iniciando verificação de novas vagas {company_name.upper()}...")


    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return None

    
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


#==================================================
# Captura as informações do card da página de vagas
#==================================================

def parse_job_card(card, base_url):
    link_relative = card.get('href')
    if not link_relative:
        return None

    parts = [p for p in link_relative.split('/') if p]
    id_job = parts[-1] if parts else link_relative

    data_tag = card.find("div", class_="vacancy-date")
    data_vaga = data_tag.text.strip().lower() if data_tag else "Data não encontrada"

    title_tag = card.find("h3")
    title = title_tag.text.strip() if title_tag else "Título não encontrado"

    link_complete = f"{base_url.rstrip('/')}/{link_relative.lstrip('/')}"

    location_tag = card.find_all("div", class_="align-middle mr-20 mb-10")
    location = location_tag[1].text.strip() if len(location_tag) > 1 else "Localização não encontrada"

    office  = "Home Office" if any(term in location.lower() for term in HOME_OFFICE) else "Presencial"

    #print(f"Debug vaga: titulo='{title}' | local='{location}' | data='{data_vaga}' | tipo='{office}'")
    return{
        "id_job": id_job,
        "data_vaga": data_vaga,
        "title": title,
        "link_complete": link_complete,
        "location": location,
        "tipo": office
    }



#===========================================================
# Checa por novas vagas e envia notificação para o Telegram
#===========================================================

def check_new_jobs(company_name, config):

    data_today = get_current_date()

    print(f"Data atual capturada pelo bot: '{data_today}'")
    soup = fetch_jobs_page(config["url"], company_name)

    if soup is None:
        return

    cards_jobs = soup.find_all("a", class_="card card-vacancy mb-20")
    print(f"Total de vagas lidas na página: {len(cards_jobs)}")

    jobs_view = load_last_job(config["file"]) or []
    new_jobs_find = False

    for card in cards_jobs:
        job = parse_job_card(card, config["url"])
        if job is None:
            continue

        if data_today in job["data_vaga"] and job["id_job"] not in jobs_view:
            message = (
                f"<b>[{company_name.upper()}]</b> Nova vaga encontrada:\n\n<b>{job['title']}</b>\n\n"
                f"Data: {job['data_vaga']}\n\n"
                f"Local: {job['location']}\n\n"
                f"<a href='{job['link_complete']}'>Clique aqui para ver a vaga</a>"
            )

            send_telegram_notification(message)
            jobs_view.append(job["id_job"])
            new_jobs_find = True
            print(f"Nova vaga encontrada: {job['title']} - {job['location']} - {job['link_complete']}")

            time.sleep(1)

    if new_jobs_find:
        jobs_view = list(dict.fromkeys(jobs_view))[-40:]  # Mantém apenas as últimas 40 vagas sem repetição
        save_last_job(jobs_view, config["file"])
        print(f"Vagas atualizadas no arquivo JSON ({company_name}).")
    else:
        print(f"Nenhuma vaga nova encontrada ({company_name}).")
    

if __name__ == "__main__":
    for company_name, config in COMPANIES.items():
        check_new_jobs(company_name, config)