"""
Routeurs et endpoints de l'API.

Ce module contient tous les endpoints de l'API pour la gestion des utilisateurs,
incluant la recherche et la récupération par login.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pathlib import Path
import json
import logging
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation du routeur
router = APIRouter(tags=["users"])

# Ajouter le répertoire parent au PYTHONPATH pour résoudre les imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
from api.security import get_current_username
# Chargement sécurisé des données au démarrage
def load_user_data() -> List[Dict[str, Any]]:
    """
    Charge les données utilisateurs depuis le fichier JSON.
    
    Returns:
        List[Dict[str, Any]]: Liste des utilisateurs
        
    Raises:
        FileNotFoundError: Si le fichier de données n'existe pas
        json.JSONDecodeError: Si le fichier JSON est malformé
    """
    try:
        file_path = Path(__file__).resolve().parents[1] / "data" / "filtered_users.json"
        
        if not file_path.exists():
            logger.error(f"Fichier de données introuvable : {file_path}")
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            
        logger.info(f"Données chargées avec succès : {len(data)} utilisateurs")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur lors du parsing JSON : {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement des données : {e}")
        raise


# Chargement des données au démarrage du module
try:
    users_data = load_user_data()
except Exception as e:
    logger.critical(f"Impossible de charger les données : {e}")
    users_data = []


@router.get("/", summary="Page d'accueil de l'API")
async def get_root() -> Dict[str, str]:
    """
    Endpoint racine de l'API.
    
    Returns:
        Dict[str, str]: Message de bienvenue avec informations sur l'API
    """
    return {
        "message": "API Pipeline Users",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@router.get("/users/", 
           summary="Récupérer tous les utilisateurs",
           description="Liste complète des utilisateurs")
async def get_all_users(username: str = Depends(get_current_username)) -> List[Dict[str, Any]]:
    """
    Récupère la liste complète des utilisateurs.
    
    Returns:
        List[Dict[str, Any]]: Liste de tous les utilisateurs
        
    Raises:
        HTTPException: Si aucune donnée n'est disponible
    """
    if not users_data:
        logger.warning("Aucune donnée utilisateur disponible")
        raise HTTPException(
            status_code=503, 
            detail="Service temporairement indisponible : données utilisateurs non chargées"
        )
    
    logger.info(f"Récupération de {len(users_data)} utilisateurs")
    return users_data


@router.get("/users/{login}", 
           summary="Récupérer un utilisateur par login",
           description="Informations détaillées de l'utilisateur")
async def get_user_by_login(login: str, username: str = Depends(get_current_username)) -> Dict[str, Any]:
    """
    Récupère un utilisateur spécifique par son login.
    
    Args:
        login (str): Login de l'utilisateur recherché (insensible à la casse)
        
    Returns:
        Dict[str, Any]: Informations de l'utilisateur
        
    Raises:
        HTTPException: Si l'utilisateur n'est pas trouvé
    """
    if not users_data:
        raise HTTPException(
            status_code=503,
            detail="Service temporairement indisponible"
        )
    
    # Recherche insensible à la casse
    login_normalized = login.strip().lower()
    
    for user in users_data:
        if user.get('login', '').lower() == login_normalized:
            logger.info(f"Utilisateur trouvé : {login}")
            return user
    
    logger.warning(f"Utilisateur non trouvé : {login}")
    raise HTTPException(
        status_code=404, 
        detail=f"Utilisateur avec le login '{login}' introuvable"
    )


@router.get("/users/search/", 
           summary="Rechercher des utilisateurs",
           description="Liste des utilisateurs correspondant à la recherche")
async def search_users(
    q: str = Query(..., 
                   min_length=1, 
                   max_length=12,
                   description="Terme de recherche (minimum 1 caractère)"),
    username: str = Depends(get_current_username)
) -> List[Dict[str, Any]]:
    """
    Recherche des utilisateurs par terme de recherche dans le login.
    
    Args:
        q (str): Terme de recherche (insensible à la casse)
        
    Returns:
        List[Dict[str, Any]]: Liste des utilisateurs correspondants
        
    Raises:
        HTTPException: Si aucun utilisateur ne correspond à la recherche
    """
    if not users_data:
        raise HTTPException(
            status_code=503,
            detail="Service temporairement indisponible"
        )
    
    # Normalisation du terme de recherche
    search_term = q.strip().lower()
    
    if not search_term:
        raise HTTPException(
            status_code=400,
            detail="Le terme de recherche ne peut pas être vide"
        )
    
    # Recherche insensible à la casse
    matching_users = [
        user for user in users_data 
        if search_term in user.get('login', '').lower()
    ]
    
    if not matching_users:
        logger.info(f"Aucun résultat pour la recherche : '{q}'")
        raise HTTPException(
            status_code=404,
            detail=f"Aucun utilisateur trouvé pour la recherche '{q}'"
        )
    
    logger.info(f"Recherche '{q}' : {len(matching_users)} résultat(s)")
    return matching_users


@router.get("/etat", 
           summary="Vérification de l'état de etat de l'API",
           description="Statut de l'API et des données")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de vérification de l'état de etat de l'API.
    
    Returns:
        Dict[str, Any]: Informations sur l'état de l'API
    """
    return {
        "status": "healthy",
        "users_loaded": len(users_data),
        "data_available": bool(users_data)
    }
    
@router.get("/users/secret/", dependencies=[Depends(get_current_username)])
def get_secret_users():
    return {"secret": "tu as accédé à une route protégée"}