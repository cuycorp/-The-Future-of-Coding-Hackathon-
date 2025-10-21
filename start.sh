#!/bin/bash

# Script de démarrage rapide pour le backend Django

echo "🚀 Démarrage du Backend d'Automatisation de Génération d'Images"
echo "================================================================"

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Environnement virtuel non trouvé!${NC}"
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installation des dépendances...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dépendances installées${NC}"
fi

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé!${NC}"
    echo "Copie de .env.example vers .env..."
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
    echo -e "${YELLOW}⚠️  N'oubliez pas de configurer vos clés API dans .env${NC}"
fi

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate

# Vérifier si un superutilisateur existe
echo ""
echo -e "${YELLOW}Voulez-vous créer un superutilisateur? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Démarrer le serveur
echo ""
echo -e "${GREEN}✅ Démarrage du serveur Django sur http://127.0.0.1:8001${NC}"
echo -e "${GREEN}✅ Admin disponible sur http://127.0.0.1:8001/admin${NC}"
echo -e "${GREEN}✅ API disponible sur http://127.0.0.1:8001/api${NC}"
echo ""
echo -e "${YELLOW}📝 Pour démarrer Celery, ouvrez un nouveau terminal et exécutez:${NC}"
echo -e "${YELLOW}   ./start_celery.sh${NC}"
echo ""
echo "Appuyez sur CTRL+C pour arrêter le serveur"
echo ""

python manage.py runserver 8001
