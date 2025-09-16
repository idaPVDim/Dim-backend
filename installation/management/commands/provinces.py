from django.core.management.base import BaseCommand
from installation.models import Province

class Command(BaseCommand):
    help = 'Créer la liste des provinces avec irradiations'

    def handle(self, *args, **kwargs):
        provinces_data = [
            {'nom': 'BALE', 'irradiation': 5.0},
            {'nom': 'BAM', 'irradiation': 5.2},
            {'nom': 'BANWA', 'irradiation': 5.0},
            {'nom': 'BAZEGA', 'irradiation': 5.0},
            {'nom': 'BOUGOURIBA', 'irradiation': 4.9},
            {'nom': 'BOULGOU', 'irradiation': 5.0},
            {'nom': 'BOUKIEMDE', 'irradiation': 5.0},
            {'nom': 'COMOE', 'irradiation': 4.9},
            {'nom': 'GANZOURGOU', 'irradiation': 5.1},
            {'nom': 'GNAGNA', 'irradiation': 5.2},
            {'nom': 'GOURMA', 'irradiation': 5.0},
            {'nom': 'HOUET', 'irradiation': 5.0},
            {'nom': 'IOBA', 'irradiation': 4.9},
            {'nom': 'KADIOGO', 'irradiation': 5.1},
            {'nom': 'KENEDOUGOU', 'irradiation': 4.9},
            {'nom': 'KOMANDJARI', 'irradiation': 5.1},
            {'nom': 'KOMPIENGA', 'irradiation': 4.8},
            {'nom': 'KOSSI', 'irradiation': 5.1},
            {'nom': 'KOULPELOGO', 'irradiation': 4.9},
            {'nom': 'KOURITENGA', 'irradiation': 5.1},
            {'nom': 'KOURWEOGO', 'irradiation': 5.2},
            {'nom': 'LERABA', 'irradiation': 4.9},
            {'nom': 'LOROUM', 'irradiation': 5.3},
            {'nom': 'MOUHOUN', 'irradiation': 5.0},
            {'nom': 'NAHOURI', 'irradiation': 4.9},
            {'nom': 'NAMENTENGA', 'irradiation': 5.1},
            {'nom': 'NAYALA', 'irradiation': 5.1},
            {'nom': 'NOUMBIEL', 'irradiation': 4.9},
            {'nom': 'OUBRITENGA', 'irradiation': 5.1},
            {'nom': 'OUDALAN', 'irradiation': 5.4},
            {'nom': 'PASSORE', 'irradiation': 5.2},
            {'nom': 'PONI', 'irradiation': 4.9},
            {'nom': 'SANGUIE', 'irradiation': 5.0},
            {'nom': 'SANMATENGA', 'irradiation': 5.2},
            {'nom': 'SENO', 'irradiation': 5.3},
            {'nom': 'SISSILI', 'irradiation': 4.9},
            {'nom': 'SOUM', 'irradiation': 5.4},
            {'nom': 'SOUROU', 'irradiation': 5.1},
            {'nom': 'TAPOA', 'irradiation': 4.9},
            {'nom': 'TUY', 'irradiation': 4.9},
            {'nom': 'YAGHA', 'irradiation': 5.2},
            {'nom': 'YATENGA', 'irradiation': 5.2},
            {'nom': 'ZIRO', 'irradiation': 4.9},
            {'nom': 'ZONDOMA', 'irradiation': 5.2},
            {'nom': 'ZOUNDWEOGO', 'irradiation': 5.0},
        ]

        for province_data in provinces_data:
            province, created = Province.objects.update_or_create(
                nom=province_data['nom'], defaults={'irradiation': province_data['irradiation']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Province {province.nom} créée"))
            else:
                self.stdout.write(f"Province {province.nom} mise à jour")

        self.stdout.write(self.style.SUCCESS("Import des provinces terminé"))
