Voici un exemple de README qui décrit clairement les APIs développées pour les apps Installation et Maintenance, ainsi que les actions attendues des Clients et Techniciens via ces APIs :

***

# Documentation API - Modules Installation & Maintenance

Ce document présente l’ensemble des endpoints API REST disponibles dans les applications **Installation** et **Maintenance**, et explique le rôle des **clients** et des **techniciens** dans l’utilisation de ces APIs.

***

## Module Installation

### Principaux Endpoints

- `GET /api/installation/installations/` : Liste des installations (projets photovoltaïques)
- `POST /api/installation/installations/` : Création d’une nouvelle installation (client)
- `GET /api/installation/installations/{id}/` : Détails d’une installation spécifique
- `PUT/PATCH /api/installation/installations/{id}/` : Mise à jour d’une installation (technicien / client en fonction du rôle)
- Gestion des équipements liés, schémas, devis, comparaisons via `/installation-equipements/`, `/schemas/`, `/devis/`, `/comparaisons-economiques/`.

### Que fait le Client ?

- Crée une demande d’installation en saisissant ses besoins (consommation, surface, budget, contraintes).
- Peut consulter le statut et l’avancement de son projet.
- Visualise les équipements proposés, schéma d’installation, et devis envoyé par le technicien.
- Valide ou rejette le devis.
- Signale un incident dans la phase maintenance via le module dédié.

### Que fait le Technicien ?

- Consulte et traite les demandes d’installation des clients.
- Peut utiliser les données initiales fournies par le client ou saisir ses propres calculs (sélecteur `source_donnees`).
- Sélectionne les équipements, crée ou modifie la liste avec indication d’origine (`source`).
- Génère et uploade schéma d’installation et devis.
- Change le statut de l’installation au fur et à mesure de son avancement (ex: de « en attente » à « installée »).
- Surveille et gère les incidents liés à l’installation.

***

## Module Maintenance

### Principaux Endpoints

- `GET /api/maintenance/incidents/` : Liste des incidents signalés sur installations
- `POST /api/maintenance/incidents/` : Signalement d’un nouvel incident (client)
- `PATCH /api/maintenance/incidents/{id}/` : Mise à jour du statut de l’incident (technicien)
- Gestion des interventions, questions et réponses diagnostiques via `/maintenances/`, `/questions-maintenance/`, `/reponses-maintenance/`.

### Que fait le Client ?

- Signale un problème via la création d’un incident lié à une installation.
- Peut répondre aux questions de diagnostic posées par le technicien.

### Que fait le Technicien ?

- Analyse et diagnostique les incidents signalés.
- Propose des solutions, planifie et réalise les interventions de maintenance.
- Complète les rapports d’intervention.
- Utilise les questions et réponses de diagnostic pour guider l’analyse.

***

## Authentification et Sécurité

- Les endpoints sont protégés par authentification (JWT, session, etc. selon configuration).
- Les accès en lecture ou modification sont soumis à des permissions basées sur le rôle (client, technicien, admin).

***

## Format des données

- Les données sont échangées en JSON.
- Les fichiers (devis, rapports, schéma) sont uploadés via multipart/form-data sur des endpoints dédiés.

***

## Bonnes pratiques d’utilisation

- Le client doit toujours fournir ses données initiales via l’API d’installation.
- Le technicien peut consulter et modifier les données en fonction du workflow, en gardant toujours trace des modifications (ex: différences entre données client et technicien).
- Les communications incident/maintenance sont à privilégier via les endpoints dédiés pour assurer un historique structuré.

***

Cette documentation simplifiée permet une compréhension rapide des APIs disponibles et des responsabilités de chaque utilisateur. Pour toute question technique ou détail d’implémentation, référez-vous au code source et à la documentation technique associée.

***

