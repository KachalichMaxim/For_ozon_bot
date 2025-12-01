"""Main entry point for the Telegram Ozon Supplies Bot."""
import sys
import signal
from src.config import Config
from src.utils import setup_logging
from src.bot import OzonBot


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Shutting down bot...")
    sys.exit(0)


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging(Config.LOG_LEVEL, Config.LOG_FILE)
    
    # Validate configuration
    if not Config.validate():
        print("❌ Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize and run bot
    try:
        bot = OzonBot()
        print("✅ Bot initialized successfully. Starting...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


