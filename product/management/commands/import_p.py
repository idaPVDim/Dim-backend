import json
from django.core.management.base import BaseCommand
from product.models import Categorie, Marque, Equipement

# Données fournies (vous pouvez aussi charger depuis un fichier JSON)
DATA = [
    {
      "id": 1,
      "categorie": "Electroménager",
      "sous_categorie": "Réfrigérateur",
      "nom": "Réfrigérateur simple porte 180L",
      "puissance_W": 120,
      "tension_V": 220,
      "frequence_Hz": 50,
      "marque": "LG",
      "taille": "180L",
      "mode": "AC"
    },
    {
      "id": 2,
      "categorie": "Electroménager",
      "sous_categorie": "Téléviseur",
      "nom": "Téléviseur LED 32''",
      "puissance_W": 60,
      "tension_V": 220,
      "frequence_Hz": 50,
      "marque": "Nasco",
      "taille": "32 pouces",
      "mode": "AC"
    },
    {
      "id": 3,
      "categorie": "Electroménager",
      "sous_categorie": "Ventilateur",
      "nom": "Ventilateur sur pied",
      "puissance_W": 70,
      "tension_V": 220,
      "marque": "Binatone",
      "mode": "AC"
    },
    {
      "id": 4,
      "categorie": "Electroménager",
      "sous_categorie": "Climatiseur",
      "nom": "Climatiseur Split 1.5CV",
      "puissance_W": 1200,
      "tension_V": 220,
      "marque": "Midea",
      "taille": "1.5CV",
      "mode": "AC"
    },
    {
      "id": 5,
      "categorie": "Solaire",
      "sous_categorie": "Panneau Solaire",
      "nom": "Panneau monocristallin 330W",
      "puissance_W": 330,
      "tension_V": 24,
      "marque": "Jinko Solar",
      "mode": "DC"
    },
    {
      "id": 6,
      "categorie": "Solaire",
      "sous_categorie": "Batterie",
      "nom": "Batterie Gel 12V 200Ah",
      "capacite_Ah": 200,
      "tension_V": 12,
      "type_equipement": "Gel",
      "marque": "Narada",
      "mode": "DC"
    },
    {
      "id": 7,
      "categorie": "Solaire",
      "sous_categorie": "Onduleur",
      "nom": "Onduleur hybride 3kVA 24V",
      "puissance_VA": 3000,
      "tension_entree_V": 24,
      "tension_sortie_V": 220,
      "type_equipement": "Hybride",
      "marque": "Must Solar",
      "mode": "DC/AC"
    },
    {
      "id": 8,
      "categorie": "Solaire",
      "sous_categorie": "Contrôleur de charge",
      "nom": "Contrôleur MPPT 60A 12/24/48V",
      "courant_A": 60,
      "tension_max_V": 100,
      "type_equipement": "MPPT",
      "marque": "Epever",
      "mode": "DC"
    },
    {
      "id": 9,
      "categorie": "Electroménager",
      "sous_categorie": "Lumière",
      "nom": "Ampoule LED 9W",
      "puissance_W": 9,
      "tension_V": 220,
      "marque": "Philips",
      "mode": "AC"
    },
    {
      "id": 10,
      "categorie": "Electroménager",
      "sous_categorie": "Congélateur",
      "nom": "Congélateur horizontal 250L",
      "puissance_W": 150,
      "tension_V": 220,
      "marque": "Hisense",
      "taille": "250L",
      "mode": "AC"
    }
]

class Command(BaseCommand):
    help = 'Importe les équipements depuis une source JSON statique'

    def handle(self, *args, **options):
        self.stdout.write("Début de l'import des équipements...")

        for item in DATA:
            # Gestion des catégories (catégorie + sous_catégorie)
            # On crée ou récupère la catégorie racine
            root_cat, _ = Categorie.objects.get_or_create(nom=item['categorie'], parent=None)

            # Si une sous_categorie est présente, on la crée ou récupère en lien avec la racine
            if 'sous_categorie' in item and item['sous_categorie']:
                sub_cat, _ = Categorie.objects.get_or_create(nom=item['sous_categorie'], parent=root_cat)
            else:
                sub_cat = root_cat

            # Gestion de la marque (on crée si nécessaire)
            marque_name = item.get('marque')
            marque_obj = None
            if marque_name:
                marque_obj, _ = Marque.objects.get_or_create(nom=marque_name)

            # Préparation des champs Equipement
            equip_data = {
                'categorie': sub_cat,
                'marque': marque_obj,
                'nom': item.get('nom'),
                'description': item.get('description', ''),
                'puissance_W': item.get('puissance_W'),
                'tension_V': item.get('tension_V'),
                'frequence_Hz': item.get('frequence_Hz'),
                'capacite_Ah': item.get('capacite_Ah'),
                'taille': item.get('taille'),
                'type_equipement': item.get('type_equipement') or item.get('type'),
                'mode': item.get('mode'),
            }

            # Pour certains champs spécifiques non dans votre modèle, on ignore (ex: puissance_VA, tension_entree_V...)
            # Vous pouvez étendre la logique si besoin

            # Création / mise à jour (unique par nom + catégorie + marque)
            equip, created = Equipement.objects.update_or_create(
                nom=equip_data['nom'],
                categorie=equip_data['categorie'],
                marque=equip_data['marque'],
                defaults=equip_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Créé équipement: {equip.nom}"))
            else:
                self.stdout.write(f"Mis à jour équipement: {equip.nom}")

        self.stdout.write(self.style.SUCCESS("Import terminé avec succès !"))
