"""
test_data.py - Script pour ajouter des données de test
Ajoute plusieurs livres d'exemple dans la bibliothèque
"""

from model import BibliothequeModel

def ajouter_donnees_test():
    """Ajoute des livres de test dans la base de données"""
    
    # Créer une instance du modèle
    model = BibliothequeModel("bibliotheque.db")
    
    # Liste de livres de test
    livres_test = [
        {
            "titre": "Le Petit Prince",
            "auteur": "Antoine de Saint-Exupéry",
            "annee": 1943,
            "genre": "Fiction"
        },
        {
            "titre": "1984",
            "auteur": "George Orwell",
            "annee": 1949,
            "genre": "Science-Fiction"
        },
        {
            "titre": "L'Étranger",
            "auteur": "Albert Camus",
            "annee": 1942,
            "genre": "Philosophie"
        },
        {
            "titre": "Harry Potter à l'école des sorciers",
            "auteur": "J.K. Rowling",
            "annee": 1997,
            "genre": "Fantasy"
        },
        {
            "titre": "Les Misérables",
            "auteur": "Victor Hugo",
            "annee": 1862,
            "genre": "Roman"
        },
        {
            "titre": "Le Seigneur des Anneaux",
            "auteur": "J.R.R. Tolkien",
            "annee": 1954,
            "genre": "Fantasy"
        },
        {
            "titre": "Crime et Châtiment",
            "auteur": "Fiodor Dostoïevski",
            "annee": 1866,
            "genre": "Roman"
        },
        {
            "titre": "L'Alchimiste",
            "auteur": "Paulo Coelho",
            "annee": 1988,
            "genre": "Fiction"
        },
        {
            "titre": "Sapiens",
            "auteur": "Yuval Noah Harari",
            "annee": 2011,
            "genre": "Histoire"
        },
        {
            "titre": "La Peste",
            "auteur": "Albert Camus",
            "annee": 1947,
            "genre": "Roman"
        },
        {
            "titre": "Le Comte de Monte-Cristo",
            "auteur": "Alexandre Dumas",
            "annee": 1844,
            "genre": "Aventure"
        },
        {
            "titre": "Fondation",
            "auteur": "Isaac Asimov",
            "annee": 1951,
            "genre": "Science-Fiction"
        }
    ]
    
    # Ajouter chaque livre
    compteur_succes = 0
    compteur_echec = 0
    
    print("🔄 Ajout des données de test en cours...")
    print("-" * 60)
    
    for livre in livres_test:
        if model.ajouter_livre(
            livre["titre"],
            livre["auteur"],
            livre["annee"],
            livre["genre"]
        ):
            print(f"✅ Ajouté: {livre['titre']} par {livre['auteur']}")
            compteur_succes += 1
        else:
            print(f"❌ Échec: {livre['titre']}")
            compteur_echec += 1
    
    print("-" * 60)
    print(f"\n📊 Résumé:")
    print(f"   ✅ Livres ajoutés avec succès: {compteur_succes}")
    print(f"   ❌ Échecs: {compteur_echec}")
    print(f"   📚 Total: {len(livres_test)} livres")
    print("\n✨ La base de données est prête!")
    print("💡 Lancez 'python main.py' pour voir vos livres.\n")

if __name__ == "__main__":
    ajouter_donnees_test()
