# 🤖 Configuration Blackbox AI pour la Génération d'Images

## Changement Important

Le backend utilise maintenant **Blackbox AI** au lieu d'OpenAI DALL-E pour la génération d'images.

## 📝 Configuration Requise

### 1. Obtenir une Clé API Blackbox

1. Visitez [https://www.blackbox.ai](https://www.blackbox.ai)
2. Créez un compte ou connectez-vous
3. Accédez à la section API
4. Générez une nouvelle clé API

### 2. Configurer les Variables d'Environnement

Modifiez votre fichier `.env` et remplacez:

```env
# Ancienne configuration (OpenAI)
OPENAI_API_KEY=your-openai-api-key-here
```

Par:

```env
# Nouvelle configuration (Blackbox AI)
BLACKBOX_API_KEY=your-blackbox-api-key-here
```

### 3. Fichier `.env` Complet

Voici un exemple de fichier `.env` mis à jour:

```env
# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-y3widb()k&ck(m9_k%9%&sjrq7@mc@2r+_y+rofw%&@_@$f#l@
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (SQLite for development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Blackbox AI API (NOUVEAU!)
BLACKBOX_API_KEY=your-blackbox-api-key-here

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Media Files
MEDIA_ROOT=media/
MEDIA_URL=/media/

# Social Media API Keys (Optional)
INSTAGRAM_ACCESS_TOKEN=
FACEBOOK_ACCESS_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
```

## 🎨 Paramètres de Génération d'Images

### Styles Disponibles

Le service supporte maintenant plus de styles:

- `realistic` - Photorealistic, haute qualité, détaillé, 8k
- `artistic` - Artistique, créatif, expressif, chef-d'œuvre
- `cartoon` - Style cartoon, animé, coloré, vibrant
- `abstract` - Art abstrait, moderne, conceptuel
- `vintage` - Style vintage, rétro, classique
- `minimalist` - Minimaliste, simple, design épuré
- `anime` - Style anime, manga, animation japonaise
- `digital_art` - Art digital, concept art, trending on artstation

### Paramètres Supportés

```json
{
  "prompt": "Description de l'image",
  "negative_prompt": "Éléments à éviter",
  "style": "realistic",
  "width": 1024,
  "height": 1024,
  "quality": "hd"
}
```

**Paramètres techniques:**
- `steps`: 30 (standard) ou 50 (hd)
- `guidance_scale`: 7.5 (par défaut)
- Résolutions supportées: 256x256 à 2048x2048

## 📡 Endpoint API Blackbox

L'API utilise l'endpoint:
```
POST https://api.blackbox.ai/v1/image
```

**Headers requis:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## 🔄 Différences avec OpenAI DALL-E

| Fonctionnalité | OpenAI DALL-E | Blackbox AI |
|----------------|---------------|-------------|
| Negative Prompts | ❌ Non supporté | ✅ Supporté nativement |
| Résolutions | Limitées (1024x1024, 1024x1792, 1792x1024) | ✅ Flexibles (256-2048) |
| Steps | Non configurable | ✅ Configurable (30-50) |
| Guidance Scale | Non configurable | ✅ Configurable |
| Styles | Limités | ✅ 8+ styles |
| Prix | Plus élevé | Plus économique |

## 🚀 Exemple d'Utilisation

### Via l'API REST

```bash
curl -X POST http://localhost:8002/api/images/generate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Un magnifique coucher de soleil sur une plage tropicale",
    "negative_prompt": "personnes, bâtiments, pollution",
    "style": "realistic",
    "width": 1024,
    "height": 1024,
    "quality": "hd"
  }'
```

### Réponse Attendue

```json
{
  "id": 1,
  "status": "pending",
  "message": "Génération d'image en cours...",
  "task_id": "abc123-def456-ghi789"
}
```

Après quelques secondes, l'image sera générée et accessible via:

```bash
curl -X GET http://localhost:8002/api/images/1/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Dépannage

### Erreur: "No API key provided"

**Solution:** Vérifiez que `BLACKBOX_API_KEY` est bien défini dans votre fichier `.env`

### Erreur: "API Request Error"

**Solutions possibles:**
1. Vérifiez votre connexion internet
2. Vérifiez que votre clé API est valide
3. Vérifiez que vous avez des crédits API disponibles

### Erreur: "No image URL in response"

**Solution:** La structure de réponse de l'API Blackbox peut varier. Le code essaie plusieurs champs possibles:
- `image_url`
- `url`
- `data.url`

Si l'erreur persiste, contactez le support Blackbox AI pour connaître la structure exacte de leur réponse.

## 📚 Documentation Officielle

Pour plus d'informations, consultez:
- [Documentation Blackbox AI](https://docs.blackbox.ai/api-reference/image)
- [Exemples d'utilisation](https://docs.blackbox.ai/examples)

## 🆘 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs du serveur Django
2. Vérifiez les logs Celery (si génération asynchrone)
3. Consultez la documentation Blackbox AI
4. Ouvrez une issue sur GitHub

---

**Note:** N'oubliez pas de redémarrer le serveur Django après avoir modifié le fichier `.env`:

```bash
# Arrêtez le serveur (CTRL+C)
# Puis relancez:
python manage.py runserver 8002
