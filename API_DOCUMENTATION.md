# Documentation API - Backend d'Automatisation de Génération d'Images

## Base URL
```
http://localhost:8000/api
```

## Authentification

Toutes les requêtes (sauf register et login) nécessitent un token JWT dans le header:
```
Authorization: Bearer <access_token>
```

---

## 🔐 Authentication Endpoints

### 1. Inscription
**POST** `/auth/register/`

**Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Utilisateur créé avec succès"
}
```

### 2. Connexion
**POST** `/auth/login/`

**Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 3. Rafraîchir le Token
**POST** `/auth/token/refresh/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Utilisateur Actuel
**GET** `/auth/me/`

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-15T10:30:00Z"
}
```

### 5. Profil Utilisateur
**GET** `/auth/profile/`

**Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "bio": "Créateur de contenu passionné",
  "avatar": "http://localhost:8000/media/avatars/john.jpg",
  "phone": "+33612345678",
  "instagram_username": "john_insta",
  "facebook_page_id": "123456789",
  "twitter_username": "john_twitter",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**PATCH** `/auth/profile/`

**Body:**
```json
{
  "bio": "Nouvelle bio",
  "instagram_username": "new_username"
}
```

### 6. Changer le Mot de Passe
**POST** `/auth/change-password/`

**Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password2": "NewPass123!"
}
```

---

## 🎨 Images Endpoints

### 1. Générer une Image
**POST** `/images/generate/`

**Body:**
```json
{
  "prompt": "Un coucher de soleil sur une plage tropicale avec des palmiers",
  "style": "realistic",
  "width": 1024,
  "height": 1024,
  "quality": "hd",
  "tags": ["nature", "plage", "coucher de soleil"]
}
```

**Paramètres:**
- `prompt` (required): Description de l'image
- `style` (optional): "realistic", "artistic", "anime", "digital_art" (default: "realistic")
- `width` (optional): 256, 512, 1024 (default: 1024)
- `height` (optional): 256, 512, 1024 (default: 1024)
- `quality` (optional): "standard", "hd" (default: "standard")
- `tags` (optional): Liste de tags

**Response (202):**
```json
{
  "id": 1,
  "status": "pending",
  "message": "Génération d'image en cours...",
  "task_id": "abc123-def456-ghi789"
}
```

### 2. Liste des Images
**GET** `/images/`

**Query Parameters:**
- `status`: pending, generated, validated, rejected, failed
- `search`: Recherche dans le prompt
- `tags`: Filtrer par tags (séparés par des virgules)
- `ordering`: created_at, -created_at, prompt

**Response (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/images/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "prompt": "Un coucher de soleil...",
      "image_url": "https://...",
      "image_file": "http://localhost:8000/media/images/...",
      "status": "validated",
      "style": "realistic",
      "width": 1024,
      "height": 1024,
      "quality": "hd",
      "tags": ["nature", "plage"],
      "created_at": "2024-01-15T10:30:00Z",
      "generation_time": 5.2
    }
  ]
}
```

### 3. Détails d'une Image
**GET** `/images/{id}/`

**Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "prompt": "Un coucher de soleil sur une plage tropicale",
  "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
  "image_file": "http://localhost:8000/media/images/image_1.png",
  "status": "validated",
  "style": "realistic",
  "width": 1024,
  "height": 1024,
  "quality": "hd",
  "validation_notes": "Image parfaite pour Instagram",
  "tags": ["nature", "plage", "coucher de soleil"],
  "metadata": {
    "model": "blackbox-ai",
    "steps": 30,
    "guidance_scale": 7.5
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "generation_time": 5.2
}
```

### 4. Valider/Rejeter une Image
**PATCH** `/images/{id}/validate/`

**Body:**
```json
{
  "action": "validate",
  "validation_notes": "Parfait pour le post de demain!"
}
```

**Paramètres:**
- `action` (required): "validate" ou "reject"
- `validation_notes` (optional): Notes de validation

**Response (200):**
```json
{
  "id": 1,
  "status": "validated",
  "validation_notes": "Parfait pour le post de demain!",
  "message": "Image validée avec succès"
}
```

### 5. Supprimer une Image
**DELETE** `/images/{id}/`

**Response (204):** No Content

### 6. Statistiques
**GET** `/images/statistics/`

**Response (200):**
```json
{
  "total_images": 150,
  "by_status": {
    "pending": 5,
    "generated": 20,
    "validated": 100,
    "rejected": 20,
    "failed": 5
  },
  "by_style": {
    "realistic": 80,
    "artistic": 40,
    "anime": 20,
    "digital_art": 10
  },
  "average_generation_time": 4.8,
  "total_generation_time": 720.0
}
```

### 7. Historique de Génération
**GET** `/images/history/`

**Response (200):**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "image": 1,
      "prompt": "Un coucher de soleil...",
      "parameters": {
        "style": "realistic",
        "width": 1024,
        "height": 1024
      },
      "status": "completed",
      "generation_time": 5.2,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 8. Liste des Tags
**GET** `/images/tags/`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "nature",
    "usage_count": 45
  },
  {
    "id": 2,
    "name": "plage",
    "usage_count": 30
  }
]
```

---

## 📅 Scheduler Endpoints

### 1. Planifier un Post
**POST** `/scheduler/schedule/`

**Body:**
```json
{
  "image": 1,
  "scheduled_time": "2024-12-25T10:00:00Z",
  "platform": "instagram",
  "caption": "Joyeux Noël! 🎄✨",
  "hashtags": "#christmas #holiday #celebration #joy"
}
```

**Paramètres:**
- `image` (required): ID de l'image
- `scheduled_time` (required): Date/heure de publication (ISO 8601)
- `platform` (required): "instagram", "facebook", "twitter"
- `caption` (required): Légende du post
- `hashtags` (optional): Hashtags

**Response (201):**
```json
{
  "id": 1,
  "image": {
    "id": 1,
    "image_url": "http://..."
  },
  "scheduled_time": "2024-12-25T10:00:00Z",
  "platform": "instagram",
  "caption": "Joyeux Noël! 🎄✨",
  "hashtags": "#christmas #holiday",
  "status": "scheduled",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Liste des Posts Planifiés
**GET** `/scheduler/posts/`

**Query Parameters:**
- `status`: scheduled, posted, failed, cancelled
- `platform`: instagram, facebook, twitter
- `scheduled_time_after`: Date ISO 8601
- `scheduled_time_before`: Date ISO 8601

**Response (200):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "image": {
        "id": 1,
        "image_url": "http://..."
      },
      "scheduled_time": "2024-12-25T10:00:00Z",
      "platform": "instagram",
      "caption": "Joyeux Noël!",
      "status": "scheduled",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Détails d'un Post
**GET** `/scheduler/posts/{id}/`

**Response (200):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "image": {
    "id": 1,
    "prompt": "Un coucher de soleil...",
    "image_url": "http://..."
  },
  "scheduled_time": "2024-12-25T10:00:00Z",
  "platform": "instagram",
  "caption": "Joyeux Noël! 🎄✨",
  "hashtags": "#christmas #holiday",
  "status": "posted",
  "posted_at": "2024-12-25T10:00:15Z",
  "platform_post_id": "123456789",
  "platform_post_url": "https://instagram.com/p/...",
  "metadata": {},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-12-25T10:00:15Z"
}
```

### 4. Modifier un Post
**PATCH** `/scheduler/posts/{id}/`

**Body:**
```json
{
  "scheduled_time": "2024-12-26T10:00:00Z",
  "caption": "Nouvelle légende"
}
```

### 5. Annuler un Post
**POST** `/scheduler/posts/{id}/cancel/`

**Response (200):**
```json
{
  "id": 1,
  "status": "cancelled",
  "message": "Post annulé avec succès"
}
```

### 6. Publier Immédiatement
**POST** `/scheduler/posts/{id}/publish-now/`

**Response (200):**
```json
{
  "id": 1,
  "status": "posted",
  "posted_at": "2024-01-15T10:35:00Z",
  "platform_post_url": "https://instagram.com/p/...",
  "message": "Post publié avec succès"
}
```

### 7. Analytics d'un Post
**GET** `/scheduler/posts/{id}/analytics/`

**Response (200):**
```json
{
  "id": 1,
  "scheduled_post": 1,
  "likes": 245,
  "comments": 18,
  "shares": 12,
  "views": 1520,
  "reach": 1200,
  "impressions": 1800,
  "engagement_rate": 18.13,
  "last_synced_at": "2024-01-16T10:00:00Z",
  "raw_data": {}
}
```

### 8. Synchroniser les Analytics
**POST** `/scheduler/posts/{id}/sync-analytics/`

**Response (200):**
```json
{
  "message": "Analytics synchronisées avec succès",
  "analytics": {
    "likes": 250,
    "comments": 20,
    "engagement_rate": 18.5
  }
}
```

### 9. Statistiques du Scheduler
**GET** `/scheduler/statistics/`

**Response (200):**
```json
{
  "total_posts": 50,
  "by_status": {
    "scheduled": 10,
    "posted": 35,
    "failed": 3,
    "cancelled": 2
  },
  "by_platform": {
    "instagram": 25,
    "facebook": 15,
    "twitter": 10
  },
  "upcoming_posts": 10,
  "posts_this_week": 7,
  "posts_this_month": 28
}
```

### 10. Plannings Récurrents
**GET** `/scheduler/schedules/`

**Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Posts quotidiens Instagram",
      "frequency": "daily",
      "time_of_day": "10:00:00",
      "platforms": ["instagram"],
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**POST** `/scheduler/schedules/`

**Body:**
```json
{
  "name": "Posts quotidiens Instagram",
  "frequency": "daily",
  "time_of_day": "10:00:00",
  "platforms": ["instagram"],
  "is_active": true
}
```

---

## 📊 Codes de Statut HTTP

- `200 OK`: Requête réussie
- `201 Created`: Ressource créée
- `202 Accepted`: Requête acceptée (traitement asynchrone)
- `204 No Content`: Suppression réussie
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Ressource non trouvée
- `500 Internal Server Error`: Erreur serveur

---

## 🔒 Gestion des Erreurs

Format standard des erreurs:
```json
{
  "error": "Message d'erreur",
  "details": {
    "field": ["Message d'erreur spécifique"]
  }
}
```

Exemple:
```json
{
  "error": "Données invalides",
  "details": {
    "prompt": ["Ce champ est requis."],
    "width": ["Valeur invalide. Choisissez parmi: 256, 512, 1024"]
  }
}
```

---

## 💡 Exemples avec cURL

### Inscription
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### Générer une Image
```bash
curl -X POST http://localhost:8000/api/images/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Un coucher de soleil sur une plage",
    "style": "realistic",
    "quality": "hd"
  }'
```

### Planifier un Post
```bash
curl -X POST http://localhost:8000/api/scheduler/schedule/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": 1,
    "scheduled_time": "2024-12-25T10:00:00Z",
    "platform": "instagram",
    "caption": "Joyeux Noël! 🎄"
  }'
```

---

## 🚀 Webhooks (À venir)

Les webhooks permettront de recevoir des notifications en temps réel pour:
- Génération d'image terminée
- Post publié avec succès
- Erreur de publication
- Nouvelles analytics disponibles

---

Pour plus d'informations, consultez le README.md principal.
