"""Google Sheets integration for reading warehouse configs."""
import logging
from typing import List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from .config import Config


logger = logging.getLogger(__name__)


class SheetsManager:
    """Manages Google Sheets operations."""
    
    def __init__(self):
        """Initialize Google Sheets client."""
        self.sheet_id = Config.GOOGLE_SHEETS_ID
        self.client = None
        self.spreadsheet = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Google Sheets client with service account credentials."""
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds_path = Config.get_service_account_path()
            credentials = Credentials.from_service_account_file(
                str(creds_path),
                scopes=scopes
            )
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            logger.info("Google Sheets client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    def get_warehouses(self) -> List[Dict[str, str]]:
        """
        Read warehouse configurations from "Ozon" sheet.
        
        Returns:
            List of dictionaries with keys: Город, Название склада, Client_id, API_KEY
        """
        try:
            worksheet = self.spreadsheet.worksheet("Ozon")
            records = worksheet.get_all_records()
            
            # Log available columns for debugging
            if records:
                logger.debug(f"Available columns in Ozon sheet: {list(records[0].keys())}")
            
            warehouses = []
            for record in records:
                # Convert to string to ensure proper type
                client_id = str(record.get("Client_id", "")).strip()
                api_key = str(record.get("API_KEY", "")).strip()
                warehouse = {
                    "city": str(record.get("Город", "")).strip(),
                    "warehouse_name": str(record.get("Название склада", "")).strip(),
                    "client_id": client_id,
                    "api_key": api_key
                }
                # Only include warehouses with required fields
                if warehouse["warehouse_name"] and warehouse["client_id"] and warehouse["api_key"]:
                    warehouses.append(warehouse)
                else:
                    logger.debug(
                        f"Skipped warehouse record - missing fields: "
                        f"name={bool(warehouse['warehouse_name'])}, "
                        f"client_id={bool(warehouse['client_id'])}, "
                        f"api_key={bool(warehouse['api_key'])}"
                    )
            
            logger.info(f"Retrieved {len(warehouses)} warehouses from Ozon sheet")
            return warehouses
        except Exception as e:
            logger.error(f"Error reading warehouses: {e}", exc_info=True)
            return []
    
    def get_warehouse_chat_ids(self) -> Dict[str, List[str]]:
        """
        Read warehouse access mappings from "Access" sheet.
        Supports multiple Chat_id per warehouse.
        
        Returns:
            Dictionary mapping warehouse_name to list of chat_ids
        """
        try:
            worksheet = self.spreadsheet.worksheet("Access")
            records = worksheet.get_all_records()
            
            # Dictionary: warehouse_name -> list of chat_ids
            warehouse_access = {}
            for record in records:
                warehouse_name = record.get("Название склада", "")
                chat_id = record.get("Chat_id", "")
                if warehouse_name and chat_id:
                    chat_id_str = str(chat_id).strip()
                    if warehouse_name not in warehouse_access:
                        warehouse_access[warehouse_name] = []
                    # Add chat_id if not already in list (avoid duplicates)
                    if chat_id_str not in warehouse_access[warehouse_name]:
                        warehouse_access[warehouse_name].append(chat_id_str)
            
            total_mappings = sum(len(ids) for ids in warehouse_access.values())
            logger.info(
                f"Retrieved access mappings: {len(warehouse_access)} warehouses, "
                f"{total_mappings} total user access entries"
            )
            return warehouse_access
        except Exception as e:
            logger.error(f"Error reading access mappings: {e}")
            return {}
    
    def check_user_access(self, chat_id: str, warehouse_name: str) -> bool:
        """
        Check if user (chat_id) has access to a warehouse.
        Supports multiple users per warehouse.
        
        Args:
            chat_id: Telegram chat ID
            warehouse_name: Name of the warehouse
            
        Returns:
            True if user has access, False otherwise
        """
        warehouse_access = self.get_warehouse_chat_ids()
        allowed_chat_ids = warehouse_access.get(warehouse_name, [])
        return str(chat_id).strip() in allowed_chat_ids
    
    def add_to_tasks(self, posting_data: List[Dict[str, Any]], warehouse_name: str) -> bool:
        """
        Add posting products to "Tasks" sheet using batch update.
        
        Args:
            posting_data: List of dictionaries with posting/product data
            warehouse_name: Name of the warehouse
            
        Returns:
            True if successful, False otherwise
        """
        try:
            worksheet = self.spreadsheet.worksheet("Tasks")
            
            # Prepare rows to add with offer_id column
            rows_to_add = []
            for item in posting_data:
                row = [
                    item.get("posting_number", ""),  # Номер отправления
                    item.get("picture_url", ""),     # Фото
                    item.get("offer_id", ""),        # Offer ID
                    item.get("product_name", ""),    # Наименование
                    item.get("sku", ""),             # Артикул
                    item.get("quantity", ""),        # Кол-во
                    ""                               # Этикетка (empty initially)
                ]
                rows_to_add.append(row)
            
            # Use batch update for better performance
            if rows_to_add:
                # Get current number of rows to find where to insert
                existing_rows = len(worksheet.get_all_values())
                start_row = existing_rows + 1
                
                # Prepare range for batch update (columns A-G)
                end_row = start_row + len(rows_to_add) - 1
                range_name = f"A{start_row}:G{end_row}"
                
                # Batch update values using gspread's update method
                worksheet.update(range_name, rows_to_add, value_input_option='USER_ENTERED')
                
                logger.info(
                    f"Added {len(rows_to_add)} rows to Tasks sheet "
                    f"for warehouse {warehouse_name} using batch update"
                )
            
            return True
        except Exception as e:
            logger.error(f"Error adding to Tasks sheet: {e}", exc_info=True)
            return False
    
    def log_processed_order(self, posting_number: str, warehouse_name: str) -> bool:
        """
        Log processed order to "ProcessedOrders" sheet.
        
        Args:
            posting_number: Order posting number
            warehouse_name: Name of the warehouse
            
        Returns:
            True if successful, False otherwise
        """
        try:
            worksheet = self.spreadsheet.worksheet("ProcessedOrders")
            
            # Add row: posting_number, warehouse_name, timestamp
            from datetime import datetime
            row = [
                posting_number,
                warehouse_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            worksheet.append_row(row)
            
            logger.info(f"Logged processed order {posting_number} for warehouse {warehouse_name}")
            return True
        except Exception as e:
            logger.error(f"Error logging processed order: {e}")
            return False
    
    def ensure_sheet_exists(self, sheet_name: str) -> None:
        """
        Ensure a sheet exists in the spreadsheet. Create if it doesn't.
        
        Args:
            sheet_name: Name of the sheet to check/create
        """
        try:
            try:
                self.spreadsheet.worksheet(sheet_name)
                logger.debug(f"Sheet '{sheet_name}' already exists")
            except gspread.exceptions.WorksheetNotFound:
                # Create sheet if it doesn't exist
                self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                logger.info(f"Created sheet '{sheet_name}'")
                
                # Set headers based on sheet name
                worksheet = self.spreadsheet.worksheet(sheet_name)
                if sheet_name == "Tasks":
                    headers = [
                        "Номер отправления",
                        "Фото",
                        "Offer ID",
                        "Наименование",
                        "Артикул",
                        "Кол-во",
                        "Этикетка"
                    ]
                    worksheet.append_row(headers)
                elif sheet_name == "ProcessedOrders":
                    headers = ["Номер отправления", "Название склада", "Дата обработки"]
                    worksheet.append_row(headers)
        except Exception as e:
            logger.warning(f"Could not ensure sheet '{sheet_name}' exists: {e}")

