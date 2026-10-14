"""
Model.py - Gestion de la base de données SQLite
Responsabilité : Toutes les opérations sur la base de données
"""

import sqlite3
from typing import List, Tuple, Optional

class BibliothequeModel:
    """Modèle pour gérer la base de données de la bibliothèque"""
   
    def __init__(self, db_name: str = "bibliotheque.db"):
        """Initialise la connexion à la base de données"""
        self.db_name = db_name
        self.init_database()
   
    def init_database(self):
        """Crée la table livres si elle n'existe pas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                annee INTEGER NOT NULL,
                genre TEXT NOT NULL
            )
        ''')
       
        conn.commit()
        conn.close()
   
    def ajouter_livre(self, titre: str, auteur: str, annee: int, genre: str) -> bool:
        """
        Ajoute un livre à la base de données
        Retourne True si succès, False sinon
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
           
            cursor.execute('''
                INSERT INTO livres (titre, auteur, annee, genre)
                VALUES (?, ?, ?, ?)
            ''', (titre, auteur, annee, genre))
           
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout: {e}")
            return False
   
    def rechercher(self, critere: str, valeur: str) -> List[Tuple]:
        """
        Recherche des livres selon un critère
        critere: 'titre', 'auteur', 'annee', ou 'genre'
        valeur: la valeur à rechercher
        Retourne une liste de tuples (id, titre, auteur, annee, genre)
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
           
            if critere == "tous":
                cursor.execute('SELECT * FROM livres')
            else:
                query = f'SELECT * FROM livres WHERE {critere} LIKE ?'
                cursor.execute(query, (f'%{valeur}%',))
           
            resultats = cursor.fetchall()
            conn.close()
            return resultats
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
   
    def tout_afficher(self) -> List[Tuple]:
        """Retourne tous les livres de la base"""
        return self.rechercher("tous", "")
   
    def modifier(self, id_livre: int, titre: str, auteur: str, annee: int, genre: str) -> bool:
        """
        Modifie un livre existant
        Retourne True si succès, False sinon
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
           
            cursor.execute('''
                UPDATE livres
                SET titre = ?, auteur = ?, annee = ?, genre = ?
                WHERE id = ?
            ''', (titre, auteur, annee, genre, id_livre))
           
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de la modification: {e}")
            return False
   
    def supprimer(self, id_livre: int) -> bool:
        """
        Supprime un livre de la base
        Retourne True si succès, False sinon
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
           
            cursor.execute('DELETE FROM livres WHERE id = ?', (id_livre,))
           
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
   
    def get_livre_by_id(self, id_livre: int) -> Optional[Tuple]:
        """Récupère un livre par son ID"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
           
            cursor.execute('SELECT * FROM livres WHERE id = ?', (id_livre,))
            livre = cursor.fetchone()
           
            conn.close()
            return livre
        except Exception as e:
            print(f"Erreur lors de la récupération: {e}")
            return None