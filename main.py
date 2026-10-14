import tkinter as tk

from model import BibliothequeModel

from view import BibliothequeView

from controller import BibliothequeController


def main():
    """Fonction principale pour lancer l'application"""
   
    # Créer la fenêtre principale
    root = tk.Tk()
   
    # Créer le modèle
    model = BibliothequeModel("bibliotheque.db")
   
    # Créer la vue
    view = BibliothequeView(root)
   
    # Créer le contrôleur
    controller = BibliothequeController(model, view)
   
      # fermer via la croix (X)
    root.protocol("WM_DELETE_WINDOW", controller.quitter_application)
   
    # Lancer la boucle principale
    root.mainloop()

if __name__ == "__main__":
    main()