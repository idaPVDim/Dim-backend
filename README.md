Voici une explication des APIs développées actuellement pour les modules Installation et Maintenance, et leur rôle :

***

## Module Installation - API

### InstallationViewSet
- Point d’entrée principal pour gérer les projets d’installation photovoltaïque.
- CRUD complet (`GET`, `POST`, `PUT`, `DELETE`) sur les installations.
- Intègre les relations avec client, technicien, équipements proposés.
- Permet au client de créer une installation et au technicien de la suivre et la modifier.

### InstallationEquipementViewSet
- Gère la relation entre installations et équipements (quantité, détails).
- Permet d’ajouter, modifier ou supprimer les équipements liés à un projet.

### SchemaInstallationViewSet
- Gère les schémas techniques d’installation (fichiers PDF, images).
- Permet upload et récupération sécurisée des documents.

### DevisViewSet
- API sur le devis associé à chaque installation.
- Manipule les informations de coût (achat, installation, maintenance).
- Supporte l’upload de document PDF du devis.

### ComparaisonEconomiqueViewSet
- Gère la comparaison économique pour un devis.
- Offre les données chiffrées (coût traditionnel, économies, retour investissement).

***

## Module Maintenance - API

### IncidentViewSet
- Gestion des incidents signalés sur une installation.
- Permet au client de signaler un problème, et au technicien de suivre son avancée.

### MaintenanceViewSet
- Gère les interventions de maintenance liées à des incidents.
- Saisie des solutions, coût et dates prévues/réelles d’intervention.
- Upload des rapports PDF de maintenance.

### QuestionMaintenanceViewSet
- Questions prédéfinies servant au diagnostic des incidents.
- Utilisées par le technicien pour guider le diagnostic.

### ReponseMaintenanceViewSet
- Enregistre les réponses aux questions de diagnostic associées à un incident.
- Différencie réponses données par client et technicien.
- Permet un échange structuré et historisé.

***

## Résumé de la couverture fonctionnelle API

- Ces APIs fournissent **toutes les opérations nécessaires** sur les projets d’installation photovoltaïque, depuis la demande initiale jusqu’à la maintenance.
- Elles supportent la gestion des documents, devis, caractéristiques techniques, et le dialogue entre client et technicien.
- Les accès sont sécurisés via authentification et permissions.
- Les relations complexes (ex : équipements liés à une installation) sont bien prises en compte.

***

