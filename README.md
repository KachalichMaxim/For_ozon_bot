# Telegram Ozon Supplies Bot

Telegram bot for managing Ozon supplies orders. The bot fetches shipping postings from Ozon API, allows warehouse selection, and stores order data in Google Sheets.

## Features

- Fetch orders from Ozon API via manual command
- Select warehouse from available options
- Store order products in Google Sheets "Tasks" sheet
- Log processed orders in "ProcessedOrders" sheet
- Send individual messages with product photos and details

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in your `TELEGRAM_BOT_TOKEN` (get from @BotFather)
- Verify `GOOGLE_SHEETS_ID` matches your Google Sheet
- Ensure `GOOGLE_SERVICE_ACCOUNT_JSON` path is correct

**Note:** The Google Service Account JSON file (`tonal-concord-464913-u3-2024741e839c.json`) is not included in the repository for security reasons. You need to place it in the project directory manually.

3. Set up Google Sheets:
- Share your Google Sheet with the service account email from the JSON file
- Ensure sheets "Ozon", "Access", "Tasks", and "ProcessedOrders" exist
- "Ozon" sheet structure: Город, Название склада, Client_id, API_KEY
- "Access" sheet structure: Название склада, Chat_id

4. Run the bot:
```bash
python main.py
```

## Usage

- `/start` - Show welcome message and available commands
- `/check_orders` - Fetch and display orders (select warehouse when prompted)

## Project Structure

```
├── main.py                          # Application entry point
├── src/
│   ├── bot.py                       # Telegram bot implementation
│   ├── ozon_client.py               # Ozon API client
│   ├── sheets_manager.py            # Google Sheets integration
│   ├── config.py                    # Configuration management
│   └── utils.py                     # Helper functions
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (not in git)
├── .env.example                     # Environment variables template
└── README.md                        # This file

```

