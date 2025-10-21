# 🚀 Guide de Démarrage Rapide

Ce guide vous aidera à démarrer rapidement avec le backend d'automatisation de génération d'images.

## ⚡ Démarrage en 5 Minutes

### 1. Prérequis
- Python 3.11+ installé
- Git installé
- (Optionnel) Redis pour Celery

### 2. Installation Rapide

```bash
# Cloner le projet (si ce n'est pas déjà fait)
cd -The-Future-of-Coding-Hackathon-

# Utiliser le script de démarrage automatique
./start.sh
```

Le script `start.sh` va automatiquement:
- ✅ Créer l'environnement virtuel
- ✅ Installer les dépendances
- ✅ Créer le fichier .env
- ✅ Appliquer les migrations
- ✅ Proposer de créer un superutilisateur
- ✅ Démarrer le serveur Django

### 3. Configuration de Base

Éditez le fichier `.env` et ajoutez votre clé API Blackbox AI:

```env
BLACKBOX_API_KEY=your-blackbox-api-key-here
```

**Obtenir une clé API Blackbox:**
1. Visitez https://www.blackbox.ai
2. Créez un compte ou connectez-vous
3. Accédez à la section API
4. Générez une nouvelle clé API

### 4. Accéder à l'Application

- **API**: http://127.0.0.1:8001/api/
- **Admin**: http://127.0.0.1:8001/admin/
- **Documentation API**: Voir `API_DOCUMENTATION.md`

---

## 📋 Étapes Détaillées

### Installation Manuelle

Si vous préférez installer manuellement:

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement virtuel
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier le fichier d'environnement
cp .env.example .env

# 5. Éditer .env avec vos configurations
nano .env  # ou votre éditeur préféré

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Démarrer le serveur
python manage.py runserver 8001
```

---

## 🔄 Démarrer Celery (Optionnel mais Recommandé)

Celery est nécessaire pour:
- Génération d'images asynchrone
- Publication automatique de posts planifiés
- Synchronisation des analytics

### Installation de Redis

**Sur macOS:**
```bash
brew install redis
brew services start redis
```

**Sur Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Démarrer Celery

```bash
# Dans un nouveau terminal
./start_celery.sh
```

Ou manuellement:

```bash
# Worker + Beat ensemble
celery -A config worker -B -l info

# Ou séparément:
# Worker seulement
celery -A config worker -l info

# Beat seulement
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 🧪 Tester l'API

### 1. S'inscrire

```bash
curl -X POST http://127.0.0.1:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Se connecter

```bash
curl -X POST http://127.0.0.1:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

Copiez le token `access` de la réponse.

### 3. Générer une Image

```bash
curl -X POST http://127.0.0.1:8001/api/images/generate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Un magnifique coucher de soleil sur une plage tropicale",
    "style": "realistic",
    "quality": "hd"
  }'
```

### 4. Lister les Images

```bash
curl -X GET http://127.0.0.1:8001/api/images/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 Prochaines Étapes

1. **Configurer les Clés API des Réseaux Sociaux**
   - Instagram Access Token
   - Facebook Access Token
   - Twitter API Keys

2. **Explorer l'Interface Admin**
   - Accédez à http://127.0.0.1:8001/admin/
   - Connectez-vous avec votre superutilisateur
   - Explorez les modèles et données

3. **Lire la Documentation**
   - `README.md` - Documentation complète
   - `API_DOCUMENTATION.md` - Documentation API détaillée
   - `TODO.md` - Fonctionnalités à venir

4. **Développer le Frontend**
   - Utilisez React pour créer l'interface utilisateur
   - Connectez-vous à l'API REST
   - Consultez la documentation API pour les endpoints

---

## 🐛 Résolution de Problèmes

### Le port 8001 est déjà utilisé
```bash
# Utilisez un autre port
python manage.py runserver 8002
```

### Erreur "No module named 'django'"
```bash
# Assurez-vous que l'environnement virtuel est activé
source venv/bin/activate
pip install -r requirements.txt
```

### Erreur de connexion Redis
```bash
# Vérifiez que Redis est en cours d'exécution
redis-cli ping
# Devrait retourner: PONG

# Si non, démarrez Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Erreur Blackbox AI API
```bash
# Vérifiez que votre clé API est correcte dans .env
cat .env | grep BLACKBOX_API_KEY

# Testez votre clé API avec curl
curl -X POST https://api.blackbox.ai/v1/image \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

---

## 📚 Ressources Utiles

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Celery Documentation**: https://docs.celeryproject.org/

- **Blackbox AI API**: https://docs.blackbox.ai/api-reference/image

---

## 💡 Conseils

1. **Développement**: Utilisez SQLite (par défaut)
2. **Production**: Passez à PostgreSQL
3. **Sécurité**: Changez `SECRET_KEY` et `DEBUG=False` en production
4. **Performance**: Activez le caching avec Redis
5. **Monitoring**: Configurez Sentry pour le suivi des erreurs

---

## 🆘 Besoin d'Aide?

- Consultez `README.md` pour plus de détails
- Lisez `API_DOCUMENTATION.md` pour les endpoints
- Vérifiez `TODO.md` pour les fonctionnalités planifiées
- Ouvrez une issue sur GitHub

---

**Bon développement! 🚀**
