#!/bin/bash

# Script de démarrage pour Celery Worker et Beat

echo "🔄 Démarrage de Celery pour les tâches asynchrones"
echo "=================================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si Redis est en cours d'exécution
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis n'est pas en cours d'exécution!${NC}"
    echo ""
    echo "Pour installer et démarrer Redis:"
    echo ""
    echo "Sur macOS:"
    echo "  brew install redis"
    echo "  brew services start redis"
    echo ""
    echo "Sur Ubuntu/Debian:"
    echo "  sudo apt-get install redis-server"
    echo "  sudo systemctl start redis"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Redis est en cours d'exécution${NC}"
echo ""

# Demander quel mode démarrer
echo "Choisissez le mode de démarrage:"
echo "1) Worker seulement"
echo "2) Beat seulement (planificateur)"
echo "3) Worker + Beat (recommandé)"
echo ""
read -p "Votre choix (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}Démarrage du Celery Worker...${NC}"
        celery -A config worker -l info
        ;;
    2)
        echo -e "${GREEN}Démarrage du Celery Beat...${NC}"
        celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    3)
        echo -e "${GREEN}Démarrage du Celery Worker + Beat...${NC}"
        celery -A config worker -B -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    *)
        echo -e "${RED}Choix invalide!${NC}"
        exit 1
        ;;
esac
