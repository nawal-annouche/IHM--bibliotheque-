"""
Controller.py - Contrôleur de l'application
Responsabilité : Logique applicative, lien entre modèle et vue
"""

from model import BibliothequeModel
from view import BibliothequeView

class BibliothequeController:
    """Contrôleur pour gérer les interactions entre modèle et vue"""
   
    def __init__(self, model: BibliothequeModel, view: BibliothequeView):
        """Initialise le contrôleur"""
        self.model = model
        self.view = view
       
        # Liaison des événements
        self._bind_events()
       
        # Afficher tous les livres au démarrage
        self.afficher_tous()
   
    def _bind_events(self):
        """Lie tous les événements de la vue aux méthodes du contrôleur"""
        self.view.bind_add_button(self.ajouter_livre)
        self.view.bind_modify_button(self.modifier_livre)
        self.view.bind_delete_button(self.supprimer_livre)
        self.view.bind_show_all_button(self.afficher_tous_avec_message)
        self.view.bind_search_button(self.rechercher_livre)
        self.view.bind_clear_button(self.vider_formulaire)
        self.view.bind_quit_button(self.quitter_application)
        self.view.bind_tree_selection(self.on_livre_selectionne)
   
    def ajouter_livre(self):
        """Ajoute un nouveau livre"""
        # Récupérer les données du formulaire
        titre, auteur, annee, genre = self.view.get_inputs()
       
        # Validation des données
        if not self._valider_donnees(titre, auteur, annee, genre):
            return
       
        # Conversion de l'année en entier
        try:
            annee_int = int(annee)
        except ValueError:
            self.view.show_error("Erreur", "L'année doit être un nombre valide")
            return
       
        # Ajouter le livre au modèle
        if self.model.ajouter_livre(titre, auteur, annee_int, genre):
            self.view.show_info("Succès", f"Le livre '{titre}' a été ajouté avec succès!")
            self.view.clear_inputs()
            self.afficher_tous()
        else:
            self.view.show_error("Erreur", "Impossible d'ajouter le livre")
   
    def modifier_livre(self):
        """Modifie le livre sélectionné"""
        # Vérifier qu'un livre est sélectionné
        id_livre = self.view.get_selected_book()
        if not id_livre:
            self.view.show_error("Erreur", "Veuillez sélectionner un livre à modifier")
            return
       
        # Récupérer les nouvelles données
        titre, auteur, annee, genre = self.view.get_inputs()
       
        # Validation des données
        if not self._valider_donnees(titre, auteur, annee, genre):
            return
       
        # Conversion de l'année
        try:
            annee_int = int(annee)
        except ValueError:
            self.view.show_error("Erreur", "L'année doit être un nombre valide")
            return
       
        # Modifier le livre
        if self.model.modifier(id_livre, titre, auteur, annee_int, genre):
            self.view.show_info("Succès", f"Le livre '{titre}' a été modifié avec succès!")
            self.view.clear_inputs()
            self.afficher_tous()
        else:
            self.view.show_error("Erreur", "Impossible de modifier le livre")
   
    def supprimer_livre(self):
        """Supprime le livre sélectionné"""
        # Vérifier qu'un livre est sélectionné
        id_livre = self.view.get_selected_book()
        if not id_livre:
            self.view.show_error("Erreur", "Veuillez sélectionner un livre à supprimer")
            return
       
        # Récupérer les informations du livre pour la confirmation
        livre = self.model.get_livre_by_id(id_livre)
        if not livre:
            self.view.show_error("Erreur", "Livre introuvable")
            return
       
        titre = livre[1]
       
        # Demander confirmation
        if self.view.ask_confirmation("Confirmation",
                                     f"Voulez-vous vraiment supprimer le livre '{titre}' ?"):
            if self.model.supprimer(id_livre):
                self.view.show_info("Succès", f"Le livre '{titre}' a été supprimé")
                self.view.clear_inputs()
                self.afficher_tous()
            else:
                self.view.show_error("Erreur", "Impossible de supprimer le livre")
   
    def afficher_tous(self):
        """Affiche tous les livres de la bibliothèque"""
        livres = self.model.tout_afficher()
        self.view.afficher_liste(livres)
        
    def afficher_tous_avec_message(self):
        """Affiche tous les livres et montre le nombre"""
        livres = self.model.tout_afficher()
        self.view.afficher_liste(livres)

        nombre = len(livres)
        self.view.show_info("Bibliothèque", f"Il y a {nombre} livre(s) dans la bibliothèque.")
   
    def rechercher_livre(self):
        """Recherche des livres selon le texte saisi"""
        texte_recherche = self.view.get_search_text()
       
        if not texte_recherche:
            self.view.show_error("Erreur", "Veuillez saisir un terme de recherche")
            return
       
        # Recherche dans tous les champs
        resultats = []
       
        # Recherche par titre
        resultats.extend(self.model.rechercher("titre", texte_recherche))
       
        # Recherche par auteur
        for livre in self.model.rechercher("auteur", texte_recherche):
            if livre not in resultats:
                resultats.append(livre)
       
        # Recherche par genre
        for livre in self.model.rechercher("genre", texte_recherche):
            if livre not in resultats:
                resultats.append(livre)
       
        # Recherche par année (si c'est un nombre)
        try:
            annee = int(texte_recherche)
            for livre in self.model.rechercher("annee", str(annee)):
                if livre not in resultats:
                    resultats.append(livre)
        except ValueError:
            pass  # Pas un nombre, on ignore la recherche par année
       
        # Afficher les résultats
        if resultats:
            self.view.afficher_liste(resultats)
            self.view.show_info("Résultats", f"{len(resultats)} livre(s) trouvé(s)")
        else:
            self.view.show_info("Résultats", "Aucun livre trouvé")
            self.afficher_tous()
   
    def on_livre_selectionne(self):
        """Gère l'événement de sélection d'un livre dans la liste"""
        id_livre = self.view.get_selected_book()
        if not id_livre:
            return
       
        # Récupérer les informations du livre
        livre = self.model.get_livre_by_id(id_livre)
        if livre:
            _, titre, auteur, annee, genre = livre
            self.view.set_inputs(titre, auteur, str(annee), genre)
            
            entries = [self.view.titre_entry, self.view.auteur_entry, self.view.annee_entry]
            for e in entries:
                e.config(fg="#111827")  # noir
    def vider_formulaire(self):
        """Vide le formulaire de saisie"""
        self.view.clear_inputs()
        self.view.clear_selection()
   
    def quitter_application(self):
        """Quitte l'application"""
        if self.view.ask_confirmation("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.view.root.destroy()
   
    def _valider_donnees(self, titre: str, auteur: str, annee: str, genre: str) -> bool:
        """
        Valide les données saisies
        Retourne True si valide, False sinon
        """
        if not titre:
            self.view.show_error("Erreur", "Le titre est obligatoire")
            return False
       
        if not auteur:
            self.view.show_error("Erreur", "L'auteur est obligatoire")
            return False
       
        if not annee:
            self.view.show_error("Erreur", "L'année est obligatoire")
            return False
       
        if not genre:
            self.view.show_error("Erreur", "Le genre est obligatoire")
            return False
       
        # Vérifier que l'année est un nombre
        try:
            annee_int = int(annee)
            if annee_int < 1000 or annee_int > 2100:
                self.view.show_error("Erreur", "L'année doit être entre 1000 et 2100")
                return False
        except ValueError:
            self.view.show_error("Erreur", "L'année doit être un nombre valide")
            return False
       
        return True