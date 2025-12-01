# Deployment Instructions

## GitHub Repository Setup

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Repository name: `Ozon_bot_for_supplies`
   - Description: "Telegram bot for managing Ozon supplies orders"
   - Set to Private (recommended for credentials)
   - Do NOT initialize with README, .gitignore, or license

2. After creating the repository, run these commands:

```bash
cd /Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies
   git remote add origin https://github.com/KachalichMaxim/For_ozon_bot.git
   git branch -M main
   git push -u origin main
```

**Note:** Repository is already set up and pushed to: https://github.com/KachalichMaxim/For_ozon_bot.git

## VM Deployment

1. Connect to your VM:
```bash
cd /Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' USER@HOST
```

2. On the VM, clone the repository:
```bash
git clone https://github.com/KachalichMaxim/For_ozon_bot.git
cd For_ozon_bot
```

3. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Create `.env` file with your credentials:
```bash
nano .env
```

Add the following (update with your values):
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
GOOGLE_SHEETS_ID=1ngNLaD2s9fb8LtfRQ7Maw6guPpGVrwsOwmJkmsI815Y
GOOGLE_SERVICE_ACCOUNT_JSON=tonal-concord-464913-u3-2024741e839c.json
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

5. Upload the Google Service Account JSON file:
```bash
# Use scp from your local machine:
scp -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  /Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies/tonal-concord-464913-u3-2024741e839c.json \
  USER@HOST:~/Ozon_bot_for_supplies/
```

6. Run the bot:
```bash
python3 main.py
```

7. To run in background (using screen or tmux):
```bash
# Using screen:
screen -S ozon_bot
python3 main.py
# Press Ctrl+A then D to detach

# To reattach:
screen -r ozon_bot

# Using tmux:
tmux new -s ozon_bot
python3 main.py
# Press Ctrl+B then D to detach

# To reattach:
tmux attach -t ozon_bot
```

## Important Notes

- The `.env` file and `tonal-concord-464913-u3-2024741e839c.json` are NOT in git (for security)
- Make sure to upload the JSON file manually to the VM
- Keep your `.env` file secure and never commit it to git

