# 📁 Structure du Projet

```
-The-Future-of-Coding-Hackathon-/
│
├── 📄 manage.py                          # Script de gestion Django
├── 📄 requirements.txt                   # Dépendances Python
├── 📄 .env                              # Variables d'environnement (non versionné)
├── 📄 .env.example                      # Template des variables d'environnement
├── 📄 .gitignore                        # Fichiers à ignorer par Git
│
├── 📄 README.md                         # Documentation principale
├── 📄 API_DOCUMENTATION.md              # Documentation API complète
├── 📄 QUICK_START.md                    # Guide de démarrage rapide
├── 📄 TODO.md                           # Liste des tâches et fonctionnalités
├── 📄 PROJECT_STRUCTURE.md              # Ce fichier
│
├── 🔧 start.sh                          # Script de démarrage du serveur
├── 🔧 start_celery.sh                   # Script de démarrage de Celery
│
├── 📂 config/                           # Configuration Django
│   ├── __init__.py                      # Import Celery
│   ├── settings.py                      # Paramètres Django
│   ├── urls.py                          # URLs principales
│   ├── wsgi.py                          # Configuration WSGI
│   ├── asgi.py                          # Configuration ASGI
│   └── celery.py                        # Configuration Celery
│
├── 📂 apps/                             # Applications Django
│   │
│   ├── 📂 authentication/               # App d'authentification
│   │   ├── __init__.py
│   │   ├── apps.py                      # Configuration de l'app
│   │   ├── models.py                    # UserProfile
│   │   ├── serializers.py               # Serializers DRF
│   │   ├── views.py                     # Vues API
│   │   ├── urls.py                      # Routes API
│   │   ├── admin.py                     # Configuration admin
│   │   ├── tests.py                     # Tests unitaires
│   │   └── migrations/                  # Migrations de base de données
│   │       └── 0001_initial.py
│   │
│   ├── 📂 images/                       # App de génération d'images
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # GeneratedImage, ImageTag, etc.
│   │   ├── serializers.py               # Serializers DRF
│   │   ├── views.py                     # Vues API
│   │   ├── urls.py                      # Routes API
│   │   ├── admin.py                     # Configuration admin
│   │   ├── tasks.py                     # Tâches Celery
│   │   ├── tests.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   └── services/                    # Services métier
│   │       ├── __init__.py
│   │       └── image_generator.py       # Service Blackbox AI
│   │
│   └── 📂 scheduler/                    # App de planification
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                    # ScheduledPost, PostingSchedule, etc.
│       ├── serializers.py               # Serializers DRF
│       ├── views.py                     # Vues API
│       ├── urls.py                      # Routes API
│       ├── admin.py                     # Configuration admin
│       ├── tasks.py                     # Tâches Celery
│       ├── tests.py
│       ├── migrations/
│       │   └── 0001_initial.py
│       └── services/                    # Services métier
│           ├── __init__.py
│           └── platform_integrations.py # Intégrations réseaux sociaux
│
├── 📂 media/                            # Fichiers uploadés (non versionné)
│   ├── images/                          # Images générées
│   └── avatars/                         # Avatars utilisateurs
│
├── 📂 staticfiles/                      # Fichiers statiques collectés (non versionné)
│
├── 📂 venv/                             # Environnement virtuel Python (non versionné)
│
└── 📄 db.sqlite3                        # Base de données SQLite (non versionné)
```

---

## 📋 Description des Composants

### 🔧 Configuration (`config/`)

**settings.py**
- Configuration Django principale
- Apps installées
- Middleware
- Base de données
- Configuration REST Framework
- Configuration JWT
- Configuration Celery
- Configuration CORS
- Variables d'environnement

**urls.py**
- Routes principales de l'API
- Inclusion des URLs des apps
- Configuration des fichiers media

**celery.py**
- Configuration Celery
- Tâches périodiques (Beat)
- Configuration Redis

---

### 🔐 Authentication (`apps/authentication/`)

**Modèles:**
- `UserProfile`: Profil utilisateur étendu avec informations réseaux sociaux

**Endpoints:**
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `POST /api/auth/token/refresh/` - Rafraîchir token
- `GET /api/auth/me/` - Utilisateur actuel
- `GET/PATCH /api/auth/profile/` - Profil utilisateur
- `POST /api/auth/change-password/` - Changer mot de passe

**Fonctionnalités:**
- Authentification JWT
- Gestion de profil
- Intégration réseaux sociaux

---

### 🎨 Images (`apps/images/`)

**Modèles:**
- `GeneratedImage`: Images générées par IA
- `ImageTag`: Tags pour organiser les images
- `ImageTagRelation`: Relation many-to-many
- `ImageGenerationHistory`: Historique de génération

**Endpoints:**
- `POST /api/images/generate/` - Générer une image
- `GET /api/images/` - Liste des images
- `GET /api/images/{id}/` - Détails d'une image
- `PATCH /api/images/{id}/` - Modifier une image
- `DELETE /api/images/{id}/` - Supprimer une image
- `PATCH /api/images/{id}/validate/` - Valider/rejeter
- `GET /api/images/statistics/` - Statistiques
- `GET /api/images/history/` - Historique
- `GET /api/images/tags/` - Liste des tags

**Services:**
- `ImageGeneratorService`: Intégration Blackbox AI

**Tâches Celery:**
- `generate_image_task`: Génération asynchrone
- `cleanup_old_images_task`: Nettoyage automatique

**Fonctionnalités:**
- Génération d'images avec Blackbox AI
- Styles personnalisables
- Système de tags
- Validation d'images
- Statistiques détaillées

---

### 📅 Scheduler (`apps/scheduler/`)

**Modèles:**
- `ScheduledPost`: Posts planifiés
- `PostingSchedule`: Plannings récurrents
- `PostAnalytics`: Analytics des posts

**Endpoints:**
- `POST /api/scheduler/schedule/` - Planifier un post
- `GET /api/scheduler/posts/` - Liste des posts
- `GET /api/scheduler/posts/{id}/` - Détails d'un post
- `PATCH /api/scheduler/posts/{id}/` - Modifier un post
- `DELETE /api/scheduler/posts/{id}/` - Supprimer un post
- `POST /api/scheduler/posts/{id}/cancel/` - Annuler
- `POST /api/scheduler/posts/{id}/publish-now/` - Publier maintenant
- `GET /api/scheduler/posts/{id}/analytics/` - Analytics
- `POST /api/scheduler/posts/{id}/sync-analytics/` - Sync analytics
- `GET /api/scheduler/statistics/` - Statistiques
- `GET/POST /api/scheduler/schedules/` - Plannings récurrents

**Services:**
- `InstagramPublisher`: Publication sur Instagram
- `FacebookPublisher`: Publication sur Facebook
- `TwitterPublisher`: Publication sur Twitter

**Tâches Celery:**
- `publish_scheduled_posts_task`: Publication automatique
- `sync_post_analytics_task`: Synchronisation analytics
- `check_scheduled_posts_task`: Vérification périodique

**Fonctionnalités:**
- Planification de posts
- Publication multi-plateformes
- Plannings récurrents
- Analytics en temps réel
- Gestion d'erreurs

---

## 🗄️ Base de Données

### Tables Principales

**authentication_userprofile**
- Profils utilisateurs étendus
- Informations réseaux sociaux

**images_generatedimage**
- Images générées
- Métadonnées de génération
- Statuts de validation

**images_imagetag**
- Tags pour organiser les images

**images_imagetagrelation**
- Relations images-tags

**images_imagegenerationhistory**
- Historique de génération

**scheduler_scheduledpost**
- Posts planifiés
- Informations de publication

**scheduler_postingschedule**
- Plannings récurrents

**scheduler_postanalytics**
- Analytics des posts

**django_celery_beat_***
- Tables Celery Beat pour la planification

---

## 🔄 Flux de Données

### Génération d'Image
```
1. Utilisateur → POST /api/images/generate/
2. API → Crée GeneratedImage (status: pending)
3. API → Lance generate_image_task (Celery)
4. Celery → Appelle Blackbox AI API
5. Celery → Télécharge l'image
6. Celery → Met à jour GeneratedImage (status: generated)
7. Utilisateur → Reçoit notification
```

### Publication de Post
```
1. Utilisateur → POST /api/scheduler/schedule/
2. API → Crée ScheduledPost (status: scheduled)
3. Celery Beat → Vérifie les posts à publier
4. Celery → Lance publish_scheduled_posts_task
5. Service → Publie sur la plateforme
6. Celery → Met à jour ScheduledPost (status: posted)
7. Celery → Sync analytics périodiquement
```

---

## 🔐 Sécurité

- **Authentification**: JWT avec access/refresh tokens
- **Permissions**: IsAuthenticated pour toutes les routes protégées
- **CORS**: Configuré pour le frontend
- **Variables sensibles**: Stockées dans .env
- **Validation**: Serializers DRF pour toutes les entrées

---

## 📊 Monitoring

- **Admin Django**: Interface d'administration complète
- **Celery Flower**: Monitoring des tâches (à installer)
- **Logs**: Configuration dans settings.py
- **Sentry**: À configurer pour la production

---

## 🚀 Déploiement

### Développement
- SQLite
- Django Development Server
- Celery local

### Production
- PostgreSQL
- Gunicorn/uWSGI
- Nginx
- Redis
- Celery Workers
- Supervisor/Systemd

---

## 📝 Notes Importantes

1. **Media Files**: Les images sont stockées dans `media/images/`
2. **Static Files**: Collectés dans `staticfiles/` avec `collectstatic`
3. **Migrations**: Toujours créer et appliquer les migrations
4. **Tests**: À développer dans chaque app
5. **Documentation**: Maintenir à jour avec les changements

---

Dernière mise à jour: 21 Octobre 2025
