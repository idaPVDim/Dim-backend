import random
from django.core.management.base import BaseCommand
from user.models import ProfilClient, ProfilTechnicien
from installation.models import Installation, Province, InstallationEquipement
from product.models import Equipement
from decimal import Decimal

class Command(BaseCommand):
    help = "Créer 20 installations aléatoires avec clients, techniciens, équipements et provinces"

    def handle(self, *args, **kwargs):
        clients = list(ProfilClient.objects.all())
        techniciens = list(ProfilTechnicien.objects.all())
        provinces = list(Province.objects.all())
        equipements = list(Equipement.objects.all())

        if not clients or not techniciens or not provinces or not equipements:
            self.stdout.write(self.style.ERROR("Base de données insuffisante : clients, techniciens, provinces ou équipements manquants"))
            return

        for i in range(20):
            client = random.choice(clients)
            technicien = random.choice(techniciens)
            province = random.choice(provinces)

            installation = Installation.objects.create(
                client=client,
                technicien=technicien,
                source_donnees=random.choice(['client', 'technicien']),
                province=province,
                budget_client=Decimal(random.randint(500000, 2000000)),
                surface_disponible_m2=Decimal(random.uniform(10.0, 100.0)).quantize(Decimal('0.01')),
                contraintes_specifiques="Exemple de contraintes spécifiques",
                status='pending',
            )
            # Ajout de 1 à 3 équipements au hasard, moitié client moitié technicien
            for _ in range(random.randint(1, 3)):
                eq = random.choice(equipements)
                source = random.choice(['client', 'technicien'])
                quantite = random.randint(1, 5)

                InstallationEquipement.objects.create(
                    installation=installation,
                    equipement=eq,
                    quantite=quantite,
                    source=source
                )

            self.stdout.write(f"Installation {installation.id} créée - Client: {client.user.email}, Technicien: {technicien.user.email}, Province: {province.nom}")

        self.stdout.write(self.style.SUCCESS("20 installations créées avec succès."))
