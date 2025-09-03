#!/bin/bash
# 🚀 VirtualDisplayPy Launcher
# Date: 03/09/2025
# Description: Launcher script for VirtualDisplayPy

echo "🖥️ VirtualDisplayPy - Émulateur d'Afficheur MostaGare"
echo "====================================================="

# Navigate to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "   Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "   Installation des dépendances..."
    source venv/bin/activate
    pip install -e .
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Environnement virtuel activé"

# Parse arguments
case "${1:-gui}" in
    "gui")
        echo "🖥️ Lancement de l'interface graphique..."
        python3 main_gui_simple.py
        ;;
    "console")
        echo "💻 Lancement de l'interface console..."
        python3 main_simple.py
        ;;
    "test")
        echo "🧪 Lancement des tests..."
        python3 -m cli.test_runner_cli run
        ;;
    "test-create")
        echo "📝 Création des scénarios de test..."
        python3 -m cli.test_runner_cli create-scenarios
        ;;
    "test-list")
        echo "📋 Liste des scénarios de test..."
        python3 -m cli.test_runner_cli list-scenarios
        ;;
    "external")
        echo "📡 Test d'envoi de messages externes..."
        python3 external_sender.py
        ;;
    "external-serial")
        echo "📟 Test de communication série externe..."
        python3 external_serial_app.py
        ;;
    "test-external")
        echo "🧪 Test simple de messages externes..."
        python3 test_external_messages.py
        ;;
    "send-gui")
        echo "📡 Envoi de message vers GUI..."
        python3 send_message_to_gui.py
        ;;
    "send")
        echo "📤 Envoi de message vers afficheurs..."
        if [ -z "$2" ]; then
            python3 send_to_display.py "Message test $(date '+%H:%M:%S')"
        else
            python3 send_to_display.py "$2"
        fi
        ;;
    "help"|"-h"|"--help")
        echo ""
        echo "Usage: $0 [gui|console|test|test-create|test-list|external|external-serial|test-external|send-gui|send|help]"
        echo ""
        echo "Options:"
        echo "  gui            Lancer l'interface graphique (défaut)"
        echo "  console        Lancer l'interface console"
        echo "  test           Exécuter les tests automatisés"
        echo "  test-create    Créer les scénarios de test par défaut"
        echo "  test-list      Lister les scénarios de test disponibles"
        echo "  external       Tester l'envoi de messages depuis une app externe"
        echo "  external-serial Tester la communication série externe (pyserial)"
        echo "  test-external  Test simple de messages externes (recommandé)"
        echo "  send-gui       Envoyer message vers GUI (message visible)"
        echo "  send [message] Envoyer message vers displays GUI (RECOMMANDÉ)"
        echo "  help           Afficher cette aide"
        echo ""
        ;;
    *)
        echo "❌ Option inconnue: $1"
        echo "   Utilisez '$0 help' pour voir les options disponibles"
        exit 1
        ;;
esac