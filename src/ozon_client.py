"""Ozon API client for fetching shipping postings."""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)

OZON_API_BASE_URL = "https://api-seller.ozon.ru"


class OzonClient:
    """Client for interacting with Ozon Seller API."""
    
    def __init__(self, client_id: str, api_key: str):
        """
        Initialize Ozon API client.
        
        Args:
            client_id: Ozon client identifier
            api_key: Ozon API key
        """
        # Ensure client_id and api_key are strings
        self.client_id = str(client_id)
        self.api_key = str(api_key)
        self.headers = {
            "Client-Id": str(client_id),
            "Api-Key": str(api_key),
            "Content-Type": "application/json"
        }
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
    
    def get_postings(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        cursor: Optional[str] = None,
        sort_dir: str = "ASC"
    ) -> Dict[str, Any]:
        """
        Fetch postings from Ozon API.
        
        Args:
            filter_dict: Filter parameters (required by API)
            limit: Number of results per page (max 1000)
            cursor: Pagination cursor for next page
            sort_dir: Sort direction (ASC or DESC)
            
        Returns:
            API response with postings data
        """
        url = f"{OZON_API_BASE_URL}/v1/assembly/fbs/posting/list"
        
        # Default filter if none provided
        # API requires BOTH cutoff_from and cutoff_to
        if filter_dict is None:
            # Use a date 30 days ago as cutoff_from to get orders
            # Format: YYYY-MM-DDThh:mm:ss.mcsZ
            cutoff_from = (datetime.utcnow() - timedelta(days=30)).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
            # Set cutoff_to to end of today (23:59:59.999Z) to ensure
            # we capture all orders for today, even if there's a delay
            now = datetime.utcnow()
            cutoff_to = now.replace(
                hour=23, minute=59, second=59, microsecond=999000
            ).strftime("%Y-%m-%dT%H:%M:%S.999Z")
            filter_dict = {
                "cutoff_from": cutoff_from,
                "cutoff_to": cutoff_to
            }
        
        # Ensure filter has required cutoff_from field
        if "cutoff_from" not in filter_dict:
            # Add cutoff_from if missing (30 days ago)
            cutoff_from = (datetime.utcnow() - timedelta(days=30)).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
            filter_dict["cutoff_from"] = cutoff_from
        
        # Ensure filter has required cutoff_to field
        # API requires cutoff_to - set to end of today if not provided
        if "cutoff_to" not in filter_dict:
            # Set cutoff_to to end of today to ensure we capture
            # all orders for today
            now = datetime.utcnow()
            cutoff_to = now.replace(
                hour=23, minute=59, second=59, microsecond=999000
            ).strftime("%Y-%m-%dT%H:%M:%S.999Z")
            filter_dict["cutoff_to"] = cutoff_to
        
        # Ensure limit is within API constraints
        limit = max(1, min(int(limit), 1000))
        
        payload = {
            "filter": filter_dict,
            "limit": limit,
            "sort_dir": sort_dir.upper()
        }
        
        if cursor:
            payload["cursor"] = str(cursor)
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Fetching postings from Ozon API "
                    f"(limit={limit}, attempt={attempt + 1}/{max_retries})"
                )
                logger.info(
                    f"Filter: cutoff_from={filter_dict.get('cutoff_from')}, "
                    f"cutoff_to={filter_dict.get('cutoff_to', 'not set')}"
                )
                logger.debug(f"Request payload: {payload}")
                logger.debug(f"Request headers: {dict(self.headers)}")
                
                # Use tuple for timeout: (connect_timeout, read_timeout)
                # Increased timeouts: 30s connect, 120s read
                response = self.session.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=(30, 120)
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(
                    f"Successfully fetched postings. "
                    f"Got {len(data.get('postings', []))} postings"
                )
                return data
                
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Timeout on attempt {attempt + 1}/{max_retries}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Timeout error after {max_retries} attempts: {e}"
                    )
                    raise requests.exceptions.RequestException(
                        f"Request timeout after {max_retries} attempts. "
                        "Проверьте интернет-соединение или попробуйте позже."
                    ) from e
                    
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if hasattr(e, 'response') and e.response is not None:
                    status = e.response.status_code
                    logger.error(
                        f"HTTP {status} error from Ozon API: {e}"
                    )
                    try:
                        error_body = e.response.text
                        logger.error(f"Response body: {error_body}")
                        # Try to parse JSON error response
                        try:
                            error_json = e.response.json()
                            logger.error(f"Error details: {error_json}")
                        except:
                            pass
                    except Exception as parse_error:
                        logger.error(f"Could not read error response: {parse_error}")
                    
                    # Raise with more context
                    if status == 400:
                        raise requests.exceptions.RequestException(
                            f"Неверный формат запроса (400). "
                            f"Проверьте правильность Client-Id и API-Key. "
                            f"Детали в логах."
                        ) from e
                    elif status == 401:
                        raise requests.exceptions.RequestException(
                            "Ошибка аутентификации (401). "
                            "Проверьте правильность Client-Id и API-Key."
                        ) from e
                    elif status == 403:
                        raise requests.exceptions.RequestException(
                            "Доступ запрещен (403). "
                            "Проверьте права доступа API-ключа."
                        ) from e
                
                raise
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1 and hasattr(e, 'response'):
                    status = getattr(e.response, 'status_code', None)
                    # Retry on server errors
                    if status and status >= 500:
                        wait_time = 2 ** attempt
                        logger.warning(
                            f"Server error {status} on attempt "
                            f"{attempt + 1}/{max_retries}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                        continue
                
                logger.error(f"Error fetching postings from Ozon API: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response status: {e.response.status_code}")
                    try:
                        logger.error(f"Response body: {e.response.text}")
                    except:
                        pass
                raise
    
    def get_all_postings(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        sort_dir: str = "ASC"
    ) -> List[Dict[str, Any]]:
        """
        Fetch all postings using pagination.
        
        Args:
            filter_dict: Filter parameters
            sort_dir: Sort direction (ASC or DESC)
            
        Returns:
            List of all postings
        """
        all_postings = []
        cursor = None
        
        while True:
            response = self.get_postings(
                filter_dict=filter_dict,
                limit=1000,
                cursor=cursor,
                sort_dir=sort_dir
            )
            
            postings = response.get("postings", [])
            all_postings.extend(postings)
            
            cursor = response.get("cursor", "")
            # Stop if cursor is empty or no more postings
            if not cursor or cursor == "" or not postings:
                break
        
        logger.info(f"Fetched {len(all_postings)} total postings across all pages")
        return all_postings
    
    def parse_posting_products(self, posting: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse posting and extract product data for each product.
        
        Args:
            posting: Single posting object from API response
            
        Returns:
            List of product dictionaries with posting context
        """
        posting_number = posting.get("posting_number", "")
        products = posting.get("products", [])
        
        parsed_products = []
        for product in products:
            # Convert SKU to string for consistency
            sku = product.get("sku", "")
            if sku is not None:
                sku = str(sku)
            
            parsed_product = {
                "posting_number": str(posting_number) if posting_number else "",
                "picture_url": str(product.get("picture_url", "")),
                "product_name": str(product.get("product_name", "")),
                "sku": sku,
                "quantity": int(product.get("quantity", 0)),
                "offer_id": str(product.get("offer_id", ""))
            }
            parsed_products.append(parsed_product)
        
        return parsed_products

