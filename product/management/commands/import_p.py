import json
import os
import re
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models


def as_decimal(value):
    """Convertit en Decimal si possible, sinon retourne None."""
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(value)
        except InvalidOperation:
            return None
    if isinstance(value, str):
        match = re.search(r'[\d.]+', value)
        if match:
            try:
                return Decimal(match.group())
            except InvalidOperation:
                return None
        return None
    return None


class Command(BaseCommand):
    help = "Importe les équipements depuis fichiers JSON dans le répertoire de la commande"

    def handle(self, *args, **options):
        self.stdout.write("Début d'import des produits JSON...")

        base_dir = os.path.dirname(os.path.abspath(__file__))

        fichiers = [
            "produits_solaire.json",
            "produits_appareils.json",
        ]

        Equipement = apps.get_model('product', 'Equipement')
        Categorie = apps.get_model('product', 'Categorie')
        Marque = apps.get_model('product', 'Marque')

        model_fields = [
            f.name for f in Equipement._meta.get_fields()
            if f.concrete and not f.auto_created and f.name != 'id'
        ]

        def importer_fichier(nom_fichier):
            chemin = os.path.join(base_dir, nom_fichier)
            self.stdout.write(f"Import depuis {nom_fichier}...")

            with open(chemin, encoding='utf-8') as f:
                data = json.load(f)

            count_created = 0
            count_updated = 0

            for item in data:
                if 'titre' in item:
                    continue

                root_cat, _ = Categorie.objects.get_or_create(nom=item.get('categorie', 'Inconnue'), parent=None)
                sub_cat_nom = item.get('sous_categorie') or item.get('type')
                if sub_cat_nom:
                    sub_cat, _ = Categorie.objects.get_or_create(nom=sub_cat_nom, parent=root_cat)
                else:
                    sub_cat = root_cat

                marque_nom = item.get('marque') or item.get('modele_marque')
                marque_obj = None
                if marque_nom:
                    marque_obj, _ = Marque.objects.get_or_create(nom=marque_nom)

                equip_data = {
                    'categorie': sub_cat,
                    'marque': marque_obj,
                }

                for field in model_fields:
                    if field in ['categorie', 'marque']:
                        continue
                    val = item.get(field)
                    if val is not None:
                        db_field = Equipement._meta.get_field(field)
                        if isinstance(db_field, (models.DecimalField, models.FloatField)):
                            val = as_decimal(val)
                        equip_data[field] = val

                json_fields = set(item.keys()) - {'titre'}
                unmapped_fields = json_fields - set(equip_data.keys()) - {'categorie', 'marque', 'sous_categorie', 'type', 'modele_marque'}
                if unmapped_fields:
                    self.stdout.write(self.style.WARNING(
                        f"Champs JSON non importés pour '{equip_data.get('nom', 'Sans nom')}': {', '.join(unmapped_fields)}"
                    ))

                if 'nom' not in equip_data or not equip_data['nom']:
                    self.stdout.write(self.style.ERROR(f"Équipement sans 'nom' ignoré dans {nom_fichier}"))
                    continue

                equip, created = Equipement.objects.update_or_create(
                    nom=equip_data['nom'],
                    categorie=equip_data['categorie'],
                    marque=equip_data.get('marque'),
                    defaults=equip_data
                )

                if created:
                    count_created += 1
                    self.stdout.write(self.style.SUCCESS(f"Créé équipement: {equip.nom}"))
                else:
                    count_updated += 1
                    self.stdout.write(f"Mis à jour équipement: {equip.nom}")

            return count_created, count_updated

        total_created = 0
        total_updated = 0

        for f in fichiers:
            c, u = importer_fichier(f)
            total_created += c
            total_updated += u

        self.stdout.write(self.style.SUCCESS(
            f"Import terminé. Équipements créés: {total_created}, mis à jour: {total_updated}."
        ))
