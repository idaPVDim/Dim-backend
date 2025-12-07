from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rating

@receiver(post_save, sender=Rating)
def update_rating_stats(sender, instance, created, **kwargs):
    if not created:
        return

    # mise à jour technicien
    if instance.technicien:
        tech = instance.technicien
        qs = tech.ratings_recus.all()
        tech.nombre_avis = qs.count()
        tech.note_moyenne = qs.aggregate(Avg('note'))['note__avg'] or 0
        tech.save()

    # mise à jour marchand
    if instance.marchand:
        march = instance.marchand
        qs = march.ratings_recus.all()
        march.nombre_avis = qs.count()
        march.note_moyenne = qs.aggregate(Avg('note'))['note__avg'] or 0
        march.save()

    # mise à jour client
    if instance.client:
        cli = instance.client
        qs = cli.ratings_recus.all()
        cli.nombre_avis = qs.count()
        cli.note_moyenne = qs.aggregate(Avg('note'))['note__avg'] or 0
        cli.save()
