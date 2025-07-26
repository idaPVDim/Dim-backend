from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user.models import ProfilClient, ProfilTechnicien
from faker import Faker
import random

User = get_user_model()

# Listes personnalisées de noms et prénoms burkinabés
BURKINABE_LAST_NAMES = [
    "Badolo", "Ouedraogo", "Kabore", "Sana", "IlBoudou", "Sanfo", "Nacoulma"
]

BURKINABE_FIRST_NAMES = [
    "Ali", "Moussa", "Zenabo", "Kader", "Saydou", "Adama", "Issa", "Boureima",
    "Mahamadou", "Salif", "Mariam", "Fatoumata", "Aminata"
]

# Liste réaliste de villes burkinabés (zone de couverture)
BURKINA_FASO_CITIES = [
    "Ouagadougou", "Bobo-Dioulasso", "Koudougou", "Banfora",
    "Ouahigouya", "Tenkodogo", "Kaya", "Ziniaré", "Dédougou",
    "Fada N'gourma", "Kombissiri", "Gaoua", "Réo",
]

class Command(BaseCommand):
    help = 'Crée 20 utilisateurs avec profils correspondants et rôles variés, noms et prénoms burkinabés.'

    def handle(self, *args, **options):
        fake = Faker('fr_FR')  # toujours utile pour adresse, email, téléphone etc.
        self.stdout.write('Début de la création des utilisateurs...')

        created_emails = set(User.objects.values_list('email', flat=True))
        users_created_count = 0
        roles = ['client', 'technicien', 'admin']

        while users_created_count < 20:
            role = random.choice(roles)

            # Génération email unique simple à base du prénom.nom + un nombre aléa
            first_name = random.choice(BURKINABE_FIRST_NAMES)
            last_name = random.choice(BURKINABE_LAST_NAMES)
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            unique_number = random.randint(1, 9999)
            email = f"{base_email}{unique_number}@example.com"

            if email in created_emails:
                continue  # évite doublon email

            created_emails.add(email)

            user = User.objects.create_user(
                email=email,
                password='Password123!',
                role=role,
                phone_number=fake.phone_number(),
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            if role == 'client':
                ProfilClient.objects.create(
                    user=user,
                    address=fake.address(),
                    consommation_annuelle_moyenne_kwh=round(random.uniform(1000, 5000), 2),
                )
            elif role == 'technicien':
                ProfilTechnicien.objects.create(
                    user=user,
                    certifications='Certification exemple',
                    zone_couverture=random.choice(BURKINA_FASO_CITIES),
                    is_certified=random.choice([True, False]),
                )

            users_created_count += 1
            self.stdout.write(f'Créé utilisateur {email} ({first_name} {last_name}) rôle: {role}')

        self.stdout.write(self.style.SUCCESS(f'{users_created_count} utilisateurs créés avec succès.'))
