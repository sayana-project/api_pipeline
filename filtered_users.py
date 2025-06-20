import pandas as pd
from pandas import json_normalize
import json
from pathlib import Path
from pprint import pprint
import datetime

#class qui permet automatiquement de mettre au format Json les date dans la fonction save_filtered_users
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)

user_file = Path(__file__).resolve().parents[0]/"data"/"users.json"

user_filtered_file = Path(__file__).resolve().parents[0]/"data"/"filtered_users.json"
#chargement des utilisateur dans la variable data
def load_users(filepath):
    with open(filepath,encoding="utf8") as f:
        data= json.load(f)
    return data
#Supprime les utilisateurs en doublon
def remove_duplicates(users):
    seen_keys = set()
    new_list = []
    for d in users:
        if d["id"] not in seen_keys:
            seen_keys.add(d["id"])
            new_list.append(d)
    return(new_list)

#Fonction qui filtre les utilisateurs en fonction de (login, id, bio, avatar...)
#Si les variable ne sont pas vide ou sont null on les supprimes
def filter_users(users):
    df = json_normalize(users)

    # Conversion de created_at en datetime
    df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')

    # Filtrage selon les critères
    df_filtered = df[
        (df["bio"].notnull()) &
        (df["bio"] != "") &
        (df["avatar_url"].notnull()) &
        (df["avatar_url"] != "") &
        (df["created_at"] > "2015-01-01")
    ]

    # Affichage du résultat filtré
    users_filterer = df_filtered.to_dict(orient="records")
    print(f"\n {len(df_filtered)} utilisateurs valides sur {len(df)} au total.")
    return users_filterer
    

#Fonction qui permet de save les data en fichier json formatter
def save_filtered_users(users, output_path=user_filtered_file):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False,cls=DateTimeEncoder)
    print(f"{len(users)} utilisateurs sauvegardés dans {output_path}")

#Fonction qui permet de savoir le nombre d'utilisateur retiré qui n'est pas conforme au critére
#de selection
def resume_filtered_users(users:dict,rm_duplicate_user:dict,filtered_user:dict)->None:
    duplicate_rm=len(users)-len(rm_duplicate_user)
    filtered_rm=len(rm_duplicate_user)-len(filtered_user)
    message =f'''
    Utilisateurs chargés : {len(filtered_user)}
    Doublons supprimés : {duplicate_rm}
    Utilisateurs filtrés : {filtered_rm}
    '''
    print(message) 

user=load_users(user_file)
rmduplicate_id_user=remove_duplicates(user)
filter_users_data=filter_users(rmduplicate_id_user)
resume_filtered_users(user,rmduplicate_id_user,filter_users_data)
save_filtered_users(filter_users_data)