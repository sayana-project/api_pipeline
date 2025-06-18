"""
Package API Pipeline Users.

Ce package contient l'API FastAPI pour la gestion des utilisateurs
avec fonctionnalités de recherche et récupération.
"""

__version__ = "1.0.0"
__author__ = "Votre Nom"
__email__ = "votre.email@example.com"

from .main import app, create_app
from .routes import router

__all__ = ["app", "create_app", "router"]