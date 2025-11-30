"""Telegram bot handler for Ozon supplies management."""
import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from .config import Config
from .sheets_manager import SheetsManager
from .ozon_client import OzonClient


logger = logging.getLogger(__name__)


class OzonBot:
    """Main bot class for handling Telegram interactions."""
    
    def __init__(self):
        """Initialize the bot with dependencies."""
        self.sheets_manager = SheetsManager()
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up command and callback handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("check_orders", self.check_orders_command))
        self.application.add_handler(CallbackQueryHandler(self.warehouse_callback, pattern="^warehouse_"))
        self.application.add_handler(CallbackQueryHandler(self.navigation_callback, pattern="^(refresh_|back_to_warehouses)"))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - show warehouse selection menu."""
        chat_id = str(update.effective_chat.id)
        
        try:
            # Get available warehouses
            warehouses = self.sheets_manager.get_warehouses()
            
            if not warehouses:
                await update.message.reply_text(
                    "❌ Не найдено доступных складов. Проверьте настройки."
                )
                return
            
            # Filter warehouses by user access (supports multiple users per warehouse)
            warehouse_access = self.sheets_manager.get_warehouse_chat_ids()
            available_warehouses = [
                w for w in warehouses
                if str(chat_id).strip() in warehouse_access.get(w["warehouse_name"], [])
            ]
            
            if not available_warehouses:
                await update.message.reply_text(
                    "❌ У вас нет доступа ни к одному складу. "
                    "Обратитесь к администратору."
                )
                logger.warning(f"User {chat_id} has no warehouse access")
                return
            
            # Show warehouse selection menu
            await self._show_warehouse_menu(update, available_warehouses)
            logger.info(f"User {chat_id} started the bot")
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при получении списка складов."
            )
    
    async def _show_warehouse_menu(
        self,
        update: Update,
        warehouses: list,
        message_text: str = "Выберите склад для получения отправлений:"
    ) -> None:
        """Show warehouse selection menu with inline keyboard."""
        keyboard = []
        for warehouse in warehouses:
            warehouse_name = warehouse["warehouse_name"]
            city = warehouse.get("city", "")
            button_text = f"{warehouse_name}"
            if city:
                button_text = f"{city} - {warehouse_name}"
            
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"warehouse_{warehouse_name}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                message_text,
                reply_markup=reply_markup
            )
    
    async def check_orders_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /check_orders command - show warehouse selection."""
        chat_id = str(update.effective_chat.id)
        
        try:
            # Get available warehouses
            warehouses = self.sheets_manager.get_warehouses()
            
            if not warehouses:
                await update.message.reply_text(
                    "❌ Не найдено доступных складов. Проверьте настройки."
                )
                return
            
            # Filter warehouses by user access (supports multiple users per warehouse)
            warehouse_access = self.sheets_manager.get_warehouse_chat_ids()
            available_warehouses = [
                w for w in warehouses
                if str(chat_id).strip() in warehouse_access.get(w["warehouse_name"], [])
            ]
            
            if not available_warehouses:
                await update.message.reply_text(
                    "❌ У вас нет доступа ни к одному складу. "
                    "Обратитесь к администратору."
                )
                logger.warning(f"User {chat_id} has no warehouse access")
                return
            
            # Show warehouse selection menu using common function
            await self._show_warehouse_menu(update, available_warehouses)
            logger.info(f"User {chat_id} requested warehouse selection")
            
        except Exception as e:
            logger.error(f"Error in check_orders_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при получении списка складов."
            )
    
    async def warehouse_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle warehouse selection callback."""
        query = update.callback_query
        await query.answer()
        
        chat_id = str(update.effective_chat.id)
        warehouse_name = query.data.replace("warehouse_", "")
        
        try:
            # Verify user has access to this warehouse
            if not self.sheets_manager.check_user_access(chat_id, warehouse_name):
                await query.edit_message_text(
                    "❌ У вас нет доступа к этому складу."
                )
                return
            
            # Get warehouse details
            warehouses = self.sheets_manager.get_warehouses()
            warehouse = next(
                (w for w in warehouses if w["warehouse_name"] == warehouse_name),
                None
            )
            
            if not warehouse:
                await query.edit_message_text(
                    "❌ Склад не найден."
                )
                return
            
            # Notify user that fetching has started
            await query.edit_message_text(
                f"⏳ Загружаю отправления для склада: {warehouse_name}..."
            )
            
            # Fetch orders from Ozon API
            await self._process_warehouse_orders(update, context, warehouse)
            
        except Exception as e:
            logger.error(f"Error in warehouse_callback: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ Произошла ошибка при обработке склада {warehouse_name}."
            )
    
    async def _process_warehouse_orders(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        warehouse: Dict[str, str]
    ) -> None:
        """Process orders for selected warehouse."""
        warehouse_name = warehouse["warehouse_name"]
        chat_id = update.effective_chat.id
        
        try:
            # Initialize Ozon client
            ozon_client = OzonClient(
                client_id=warehouse["client_id"],
                api_key=warehouse["api_key"]
            )
            
            # Fetch all postings
            postings = ozon_client.get_all_postings()
            
            if not postings:
                # Show message with navigation menu
                message_text = f"ℹ️ Для склада {warehouse_name} нет новых отправлений."
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔄 Получить отправления",
                            callback_data=f"refresh_{warehouse_name}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад к складам",
                            callback_data="back_to_warehouses"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    reply_markup=reply_markup
                )
                return
            
            # Process each posting
            all_products = []
            processed_postings = set()
            
            for posting in postings:
                posting_number = posting.get("posting_number", "")
                
                # Parse products from posting
                products = ozon_client.parse_posting_products(posting)
                all_products.extend(products)
                
                # Store unique posting numbers for logging
                if posting_number:
                    processed_postings.add(posting_number)
            
            if not all_products:
                # Show message with navigation menu
                message_text = f"ℹ️ Для склада {warehouse_name} нет товаров в отправлениях."
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔄 Получить отправления",
                            callback_data=f"refresh_{warehouse_name}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад к складам",
                            callback_data="back_to_warehouses"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    reply_markup=reply_markup
                )
                return
            
            # Sort products by offer_id alphabetically
            all_products.sort(key=lambda x: str(x.get("offer_id", "")).lower())
            
            # Save to Tasks sheet
            success = self.sheets_manager.add_to_tasks(all_products, warehouse_name)
            
            if not success:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔄 Получить отправления",
                            callback_data=f"refresh_{warehouse_name}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Назад к складам",
                            callback_data="back_to_warehouses"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Ошибка при сохранении данных в таблицу.",
                    reply_markup=reply_markup
                )
                return
            
            # Log processed orders
            for posting_number in processed_postings:
                self.sheets_manager.log_processed_order(posting_number, warehouse_name)
            
            # Send individual messages with photos for each product
            messages_sent = 0
            for product in all_products:
                try:
                    await self._send_product_message(context, chat_id, product, warehouse_name)
                    messages_sent += 1
                except Exception as e:
                    logger.error(f"Error sending product message: {e}", exc_info=True)
                    # Continue with next product even if one fails
            
            # Send summary message with navigation menu
            summary_text = (
                f"✅ Обработка завершена для склада: {warehouse_name}\n\n"
                f"📦 Отправлений: {len(processed_postings)}\n"
                f"🛍️ Товаров: {len(all_products)}\n"
                f"💬 Сообщений отправлено: {messages_sent}"
            )
            
            # Create navigation menu
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔄 Получить отправления",
                        callback_data=f"refresh_{warehouse_name}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Назад к складам",
                        callback_data="back_to_warehouses"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=summary_text,
                reply_markup=reply_markup
            )
            
            logger.info(
                f"Successfully processed {len(processed_postings)} postings "
                f"with {len(all_products)} products for warehouse {warehouse_name}"
            )
            
        except Exception as e:
            logger.error(f"Error processing warehouse orders: {e}", exc_info=True)
            
            # Provide user-friendly error message
            error_msg = "❌ Ошибка при получении данных от Ozon API."
            
            error_str = str(e).lower()
            if "timeout" in error_str or "timed out" in error_str:
                error_msg += (
                    "\n\n⏱️ Превышено время ожидания ответа от сервера Ozon. "
                    "Возможные причины:\n"
                    "• Медленное интернет-соединение\n"
                    "• Перегрузка серверов Ozon\n"
                    "• Слишком много отправлений для загрузки\n\n"
                    "Попробуйте повторить запрос через несколько минут."
                )
            elif "connection" in error_str or "network" in error_str:
                error_msg += (
                    "\n\n🌐 Проблема с сетевым соединением. "
                    "Проверьте ваше интернет-соединение и попробуйте снова."
                )
            else:
                error_msg += f"\n\nДетали: {str(e)}"
            
            # Add navigation menu to error message
            keyboard = [
                [
                    InlineKeyboardButton(
                        "⬅️ Назад к складам",
                        callback_data="back_to_warehouses"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_msg,
                reply_markup=reply_markup
            )
    
    async def navigation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle navigation callbacks (refresh warehouse or back to warehouses)."""
        query = update.callback_query
        await query.answer()
        
        chat_id = str(update.effective_chat.id)
        callback_data = query.data
        
        try:
            if callback_data == "back_to_warehouses":
                # Show warehouse selection menu
                warehouses = self.sheets_manager.get_warehouses()
                warehouse_access = self.sheets_manager.get_warehouse_chat_ids()
                available_warehouses = [
                    w for w in warehouses
                    if str(chat_id).strip() in warehouse_access.get(w["warehouse_name"], [])
                ]
                
                if available_warehouses:
                    await self._show_warehouse_menu(
                        update,
                        available_warehouses,
                        "Выберите склад для получения отправлений:"
                    )
                else:
                    await query.edit_message_text(
                        "❌ У вас нет доступа ни к одному складу."
                    )
                    
            elif callback_data.startswith("refresh_"):
                # Refresh orders for selected warehouse
                warehouse_name = callback_data.replace("refresh_", "")
                
                # Verify user has access
                if not self.sheets_manager.check_user_access(chat_id, warehouse_name):
                    await query.edit_message_text(
                        "❌ У вас нет доступа к этому складу."
                    )
                    return
                
                # Get warehouse details
                warehouses = self.sheets_manager.get_warehouses()
                warehouse = next(
                    (w for w in warehouses if w["warehouse_name"] == warehouse_name),
                    None
                )
                
                if not warehouse:
                    await query.edit_message_text(
                        "❌ Склад не найден."
                    )
                    return
                
                # Notify user that fetching has started
                await query.edit_message_text(
                    f"⏳ Загружаю отправления для склада: {warehouse_name}..."
                )
                
                # Fetch orders from Ozon API
                await self._process_warehouse_orders(update, context, warehouse)
                
        except Exception as e:
            logger.error(f"Error in navigation_callback: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ Произошла ошибка. Попробуйте еще раз."
            )
    
    async def _send_product_message(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        product: Dict[str, Any],
        warehouse_name: str
    ) -> None:
        """Send a message with product photo and details."""
        
        picture_url = product.get("picture_url", "")
        posting_number = product.get("posting_number", "")
        offer_id = product.get("offer_id", "")
        product_name = product.get("product_name", "")
        sku = product.get("sku", "")
        quantity = product.get("quantity", 0)
        
        # Format detailed info
        details = (
            f"📦 <b>Номер отправления:</b> {posting_number}\n"
            f"🏷️ <b>Offer ID:</b> {offer_id}\n"
            f"📋 <b>Наименование:</b> {product_name}\n"
            f"🔢 <b>Артикул:</b> {sku}\n"
            f"📊 <b>Кол-во:</b> {quantity}\n"
            f"🏢 <b>Склад:</b> {warehouse_name}"
        )
        
        # Send photo with caption if available
        if picture_url:
            try:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=picture_url,
                    caption=details,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Could not send photo from URL {picture_url}: {e}")
                # Fallback to text only
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📷 [Фото недоступно]\n\n{details}",
                    parse_mode="HTML"
                )
        else:
            # Send text message if no photo
            await context.bot.send_message(
                chat_id=chat_id,
                text=details,
                parse_mode="HTML"
            )
    
    def run(self) -> None:
        """Start the bot."""
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

