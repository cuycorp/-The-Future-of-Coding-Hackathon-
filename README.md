# Application d'Automatisation de Génération d'Images - Backend

Backend Django pour une application d'automatisation de génération d'images avec planification de posts sur les réseaux sociaux.

## 🚀 Fonctionnalités

### 1. **Authentification** (`apps/authentication`)
- ✅ Inscription et connexion utilisateur
- ✅ Authentification JWT (JSON Web Tokens)
- ✅ Gestion de profil utilisateur
- ✅ Changement de mot de passe
- ✅ Profils étendus avec informations réseaux sociaux

### 2. **Génération d'Images** (`apps/images`)
- ✅ Génération d'images via Blackbox AI
- ✅ Gestion asynchrone avec Celery
- ✅ Paramètres personnalisables (style, taille, qualité)
- ✅ Système de tags pour organiser les images
- ✅ Historique de génération
- ✅ Statistiques de génération

### 3. **Validation d'Images** (`apps/images`)
- ✅ Validation/rejet d'images par l'utilisateur
- ✅ Notes de validation
- ✅ Statuts multiples (pending, generated, validated, rejected, failed)
- ✅ Filtrage par statut

### 4. **Planification de Posts** (`apps/scheduler`)
- ✅ Planification de posts sur Instagram, Facebook, Twitter
- ✅ Gestion de légendes et hashtags
- ✅ Publication automatique via Celery Beat
- ✅ Plannings récurrents (quotidien, hebdomadaire, mensuel)
- ✅ Analytics des posts publiés
- ✅ Annulation et republication

## 📋 Prérequis

- Python 3.11+
- Redis (pour Celery)
- PostgreSQL (optionnel, SQLite par défaut)
- Clé API Blackbox AI ([Obtenir une clé](https://www.blackbox.ai))

## 🛠️ Installation

### 1. Cloner le projet
```bash
git clone <repository-url>
cd -The-Future-of-Coding-Hackathon-
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

**Variables importantes:**
- `BLACKBOX_API_KEY`: Votre clé API Blackbox AI (obligatoire pour la génération d'images)
- `SECRET_KEY`: Clé secrète Django (générer une nouvelle en production)
- `REDIS_URL`: URL de connexion Redis

### 5. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement
```bash
python manage.py runserver
```

Le serveur sera accessible sur `http://localhost:8000`

## 🔄 Celery (Tâches Asynchrones)

### Démarrer Celery Worker
```bash
celery -A config worker -l info
```

### Démarrer Celery Beat (Planificateur)
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Ou les deux ensemble
```bash
celery -A config worker -B -l info
```

## 📡 API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `POST /api/auth/token/refresh/` - Rafraîchir le token
- `GET /api/auth/me/` - Utilisateur actuel
- `GET/PATCH /api/auth/profile/` - Profil utilisateur
- `POST /api/auth/change-password/` - Changer le mot de passe

### Images (`/api/images/`)
- `POST /api/images/generate/` - Générer une image
- `GET /api/images/` - Liste des images
- `GET /api/images/{id}/` - Détails d'une image
- `PATCH /api/images/{id}/` - Modifier une image
- `DELETE /api/images/{id}/` - Supprimer une image
- `PATCH /api/images/{id}/validate/` - Valider/rejeter une image
- `GET /api/images/statistics/` - Statistiques
- `GET /api/images/history/` - Historique
- `GET /api/images/tags/` - Liste des tags

### Scheduler (`/api/scheduler/`)
- `POST /api/scheduler/schedule/` - Planifier un post
- `GET /api/scheduler/posts/` - Liste des posts planifiés
- `GET /api/scheduler/posts/{id}/` - Détails d'un post
- `PATCH /api/scheduler/posts/{id}/` - Modifier un post
- `DELETE /api/scheduler/posts/{id}/` - Supprimer un post
- `POST /api/scheduler/posts/{id}/cancel/` - Annuler un post
- `POST /api/scheduler/posts/{id}/publish-now/` - Publier immédiatement
- `GET /api/scheduler/posts/{id}/analytics/` - Analytics d'un post
- `POST /api/scheduler/posts/{id}/sync-analytics/` - Synchroniser les analytics
- `GET /api/scheduler/statistics/` - Statistiques du scheduler
- `GET /api/scheduler/schedules/` - Plannings récurrents
- `POST /api/scheduler/schedules/` - Créer un planning

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### Obtenir un token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Utiliser le token
```bash
curl -X GET http://localhost:8000/api/images/ \
  -H "Authorization: Bearer <access_token>"
```

## 📊 Structure du Projet

```
.
├── config/                 # Configuration Django
│   ├── settings.py        # Paramètres principaux
│   ├── urls.py           # URLs principales
│   ├── celery.py         # Configuration Celery
│   └── wsgi.py
├── apps/
│   ├── authentication/    # App d'authentification
│   │   ├── models.py     # UserProfile
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── images/           # App de génération d'images
│   │   ├── models.py     # GeneratedImage, ImageTag, etc.
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py      # Tâches Celery
│   │   ├── admin.py
│   │   └── services/
│   │       └── image_generator.py
│   └── scheduler/        # App de planification
│       ├── models.py     # ScheduledPost, PostingSchedule, etc.
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── tasks.py      # Tâches Celery
│       ├── admin.py
│       └── services/
│           └── platform_integrations.py
├── media/                # Fichiers uploadés
├── requirements.txt      # Dépendances Python
├── manage.py
└── README.md
```

## 🎨 Exemple d'Utilisation

### 1. S'inscrire
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Générer une image
```bash
curl -X POST http://localhost:8000/api/images/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Un coucher de soleil sur une plage tropicale",
    "style": "realistic",
    "width": 1024,
    "height": 1024,
    "quality": "hd"
  }'
```

### 3. Valider l'image
```bash
curl -X PATCH http://localhost:8000/api/images/1/validate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "validate",
    "validation_notes": "Image parfaite!"
  }'
```

### 4. Planifier un post
```bash
curl -X POST http://localhost:8000/api/scheduler/schedule/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "image": 1,
    "scheduled_time": "2024-12-25T10:00:00Z",
    "platform": "instagram",
    "caption": "Joyeux Noël! 🎄",
    "hashtags": "#christmas #holiday #celebration"
  }'
```

## 🔧 Configuration Avancée

### PostgreSQL (Production)
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=image_automation_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Redis
```bash
# Installation sur macOS
brew install redis
brew services start redis

# Installation sur Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

## 📝 Administration

Accédez à l'interface d'administration Django sur `http://localhost:8000/admin/`

## 🧪 Tests

```bash
python manage.py test
```

## 📦 Déploiement

### Collecte des fichiers statiques
```bash
python manage.py collectstatic
```

### Variables d'environnement en production
- Définir `DEBUG=False`
- Générer une nouvelle `SECRET_KEY`
- Configurer `ALLOWED_HOSTS`
- Utiliser PostgreSQL au lieu de SQLite
- Configurer un serveur de fichiers pour `MEDIA_ROOT`

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

## 🆘 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

## 🔮 Roadmap

- [ ] Support de plus de plateformes (LinkedIn, TikTok)
- [ ] Génération d'images avec Stable Diffusion
- [ ] Édition d'images (recadrage, filtres)
- [ ] Templates de posts
- [ ] Analytics avancées
- [ ] Notifications par email
- [ ] API webhooks
- [ ] Export de données

---

Développé avec ❤️ pour The Future of Coding Hackathon
