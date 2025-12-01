# VM Deployment Commands

## Quick Commands Reference

### SSH Connection Details
- **SSH Key**: `/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227`
- **User**: `bookntrack`
- **Host**: `89.169.173.221`
- **Repository**: `https://github.com/KachalichMaxim/For_ozon_bot.git`

---

## Deployment Steps

### 1. Clone Repository on VM

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~ && git clone https://github.com/KachalichMaxim/For_ozon_bot.git && cd For_ozon_bot && echo "✅ Repository cloned"'
```

### 2. Update Repository (if already exists)

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && git pull origin main && echo "✅ Repository updated"'
```

### 3. Upload .env File

```bash
scp -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  /Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies/.env \
  bookntrack@89.169.173.221:~/For_ozon_bot/.env
```

### 4. Upload Google Service Account JSON

```bash
scp -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  /Users/kachalichmaxim/Desktop/Ozon_bot_for_supplies/tonal-concord-464913-u3-2024741e839c.json \
  bookntrack@89.169.173.221:~/For_ozon_bot/
```

### 5. Setup Environment and Install Dependencies

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && echo "✅ Dependencies installed"'
```

### 6. Start Bot (Interactive)

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && source venv/bin/activate && python3 main.py'
```

### 7. Start Bot in Background (Screen)

```bash
# Start in screen session
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && screen -dmS ozon_bot bash -c "source venv/bin/activate && python3 main.py"'

# Check if running
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'screen -list'

# Attach to screen session
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'screen -r ozon_bot'
```

### 8. Start Bot in Background (Tmux)

```bash
# Start in tmux session
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && tmux new -d -s ozon_bot "source venv/bin/activate && python3 main.py"'

# Check if running
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'tmux list-sessions'

# Attach to tmux session
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'tmux attach -t ozon_bot'
```

---

## All-in-One Deployment Command

### Full Setup (Clone + Setup + Start in Screen)

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~ && if [ -d For_ozon_bot ]; then cd For_ozon_bot && git pull origin main; else git clone https://github.com/KachalichMaxim/For_ozon_bot.git && cd For_ozon_bot; fi && \
  python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && \
  screen -dmS ozon_bot bash -c "cd ~/For_ozon_bot && source venv/bin/activate && python3 main.py" && \
  sleep 2 && echo "✅ Bot deployed and started in background"'
```

### Update and Restart Bot

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && git pull origin main && \
  screen -S ozon_bot -X quit 2>/dev/null; \
  sleep 1 && \
  screen -dmS ozon_bot bash -c "cd ~/For_ozon_bot && source venv/bin/activate && python3 main.py" && \
  sleep 2 && echo "✅ Bot updated and restarted"'
```

---

## Useful Commands

### Check Bot Status

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'ps aux | grep "python3 main.py" | grep -v grep'
```

### View Bot Logs

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'cd ~/For_ozon_bot && tail -f bot.log'
```

### Stop Bot

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'screen -S ozon_bot -X quit && echo "✅ Bot stopped"'
```

### Check Screen Sessions

```bash
ssh -o StrictHostKeyChecking=no -i '/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227' \
  bookntrack@89.169.173.221 \
  'screen -list'
```

---

## Quick Reference Variables

For easy copy-paste, save these:

```bash
export SSH_KEY='/Users/kachalichmaxim/Desktop/Счета по ЦТС/ssh-key-1760689301227 2/ssh-key-1760689301227'
export SSH_USER='bookntrack'
export SSH_HOST='89.169.173.221'
```

Then use:
```bash
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ${SSH_USER}@${SSH_HOST} 'command'
```


