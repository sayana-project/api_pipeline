import os
import json
import time
from datetime import datetime
from requests import get
from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint

# Charger le .env depuis la racine du projet
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# Récupérer le token GitHub
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("Le token GitHub est manquant dans le fichier .env")

headers = {"Authorization": f"token {token}"}
MAX_USERS = 1000
USERS_PER_PAGE = 30
OUTPUT_PATH = Path(__file__).resolve().parents[1]/"data"/"users.json"

def get_rate_limit_info(response):
    remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
    return remaining, reset_time

def wait_for_rate_limit(reset_timestamp):
    wait_seconds = reset_timestamp - int(time.time()) + 1
    print(f"Quota API atteint. Pause de {wait_seconds} secondes")
    time.sleep(wait_seconds)
    
    
def get_user(max_user=MAX_USERS):
    data_tempo =[]
    since=10361261
    
    while len(data_tempo) < max_user:
        
        url = f"https://api.github.com/users?since={since}"
        result = get(url, headers=headers)
        remaining, reset_time = get_rate_limit_info(result)
        
        if result.status_code == 403 and remaining == 0:
            wait_for_rate_limit(reset_time)
            continue
        elif result.status_code == 429:
            print("Trop de requêtes. Pause de 60 secondes...")
            time.sleep(60)
            continue
        elif result.status_code >= 500:
            print("Erreur serveur GitHub. Nouvelle tentative dans 30s...")
            time.sleep(30)
            continue
        elif not result.ok:
            print(f"Erreur HTTP {result.status_code}")
            break
            
        json_result = result.json()

        for i, data_json in enumerate(json_result,start=len(data_tempo) + 1):
            login = data_json["login"]
            url_user = f"https://api.github.com/users/{login}"

            result_user = get(url_user, headers=headers)
            json_result_user = result_user.json()

            bio = json_result_user.get("bio")

            data_tempo.append({
                "login": login,
                "id": data_json["id"],
                "avatar_url": data_json["avatar_url"],
                "created_at":json_result_user.get("created_at"),
                "bio": bio
            })
        since=json_result[-1]["id"]
        
        
    print(f"le nombre API restant est de : {remaining} appel API")
    print(f"le reset time est a {datetime.fromtimestamp(reset_time)}") 
    return data_tempo

def save_users(users, output_path=OUTPUT_PATH):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"{len(users)} utilisateurs sauvegardés dans {output_path}")
    
user_data=get_user()
print(user_data)
save_users(user_data)

