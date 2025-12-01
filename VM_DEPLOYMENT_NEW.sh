#!/bin/bash
# Deployment script for Ozon Bot on NEW VM (45.159.248.211)

SSH_USER='root'
SSH_HOST='45.159.248.211'
SSH_PASS='LDne17ikUS34'
REPO_URL='https://github.com/KachalichMaxim/For_ozon_bot.git'
PROJECT_DIR='~/For_ozon_bot'
LOCAL_PROJECT_DIR='/Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies'

echo "🚀 Starting deployment to NEW VM (${SSH_HOST})..."

# Check if sshpass is installed (needed for password authentication)
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew not found. Please install sshpass manually or use: brew install hudochenkov/sshpass/sshpass"
            exit 1
        else
            brew install hudochenkov/sshpass/sshpass
        fi
    else
        echo "Please install sshpass: sudo apt-get install sshpass (Linux) or brew install hudochenkov/sshpass/sshpass (macOS)"
        exit 1
    fi
fi

# Step 1: Connect to VM and clone/update repository
echo "📦 Cloning/updating repository on VM..."
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} "
    if [ -d ${PROJECT_DIR} ]; then
        echo 'Repository exists, updating...'
        cd ${PROJECT_DIR}
        git pull origin main
    else
        echo 'Repository does not exist, cloning...'
        cd ~
        git clone ${REPO_URL} For_ozon_bot
        cd ${PROJECT_DIR}
    fi
"

# Step 2: Upload .env file (if it exists locally)
if [ -f "${LOCAL_PROJECT_DIR}/.env" ]; then
    echo "📤 Uploading .env file..."
    sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no \
        "${LOCAL_PROJECT_DIR}/.env" \
        ${SSH_USER}@${SSH_HOST}:${PROJECT_DIR}/.env
else
    echo "⚠️  .env file not found locally. Please create it on VM manually."
fi

# Step 3: Upload Google Service Account JSON file
if [ -f "${LOCAL_PROJECT_DIR}/tonal-concord-464913-u3-2024741e839c.json" ]; then
    echo "📤 Uploading Google Service Account JSON..."
    sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no \
        "${LOCAL_PROJECT_DIR}/tonal-concord-464913-u3-2024741e839c.json" \
        ${SSH_USER}@${SSH_HOST}:${PROJECT_DIR}/
else
    echo "⚠️  JSON file not found. Please upload it manually."
fi

# Step 4: Install dependencies and setup on VM
echo "⚙️  Setting up environment on VM..."
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} "
    cd ${PROJECT_DIR}
    
    # Create virtual environment if it doesn't exist
    if [ ! -d venv ]; then
        echo 'Creating virtual environment...'
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo '✅ Setup completed!'
"

echo "✅ Deployment preparation completed!"
echo ""
echo "To start the bot, run:"
echo "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} 'cd ${PROJECT_DIR} && source venv/bin/activate && python3 main.py'"
echo ""
echo "Or to run in background with screen:"
echo "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} 'cd ${PROJECT_DIR} && screen -dmS ozon_bot bash -c \"source venv/bin/activate && python3 main.py\"'"

