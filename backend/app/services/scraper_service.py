import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from decimal import Decimal
import json
import logging
import time

logger = logging.getLogger(__name__)

class ScraperService:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    CURRENCY_SYMBOLS = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR',
        'Rs': 'INR',
        'USD': 'USD',
        'EUR': 'EUR',
        'GBP': 'GBP',
        'INR': 'INR',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.current_user_agent_index = 0
    
    def _get_user_agent(self) -> str:
        agent = self.USER_AGENTS[self.current_user_agent_index]
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.USER_AGENTS)
        return agent
    
    def _detect_currency(self, text: str, price: Decimal) -> str:
        for symbol, currency in self.CURRENCY_SYMBOLS.items():
            if symbol in text:
                return currency
        return 'USD'
    
    def _extract_price_from_text(self, text: str) -> Optional[tuple]:
        price_patterns = [
            r'[₹Rs\.]*\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'[\$€£¥]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|EUR|GBP|INR|Rs)',
            r'Price[:\s]*[₹\$€£¥Rs\.]*\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = Decimal(price_str)
                    if price > 0:
                        currency = self._detect_currency(text, price)
                        return (price, currency)
                except:
                    continue
        return None
    
    def _extract_price_from_meta(self, soup: BeautifulSoup) -> Optional[tuple]:
        meta_tags = [
            ('property', 'og:price:amount'),
            ('property', 'product:price:amount'),
            ('property', 'og:price'),
            ('name', 'price'),
            ('itemprop', 'price'),
        ]
        
        price = None
        currency = 'USD'
        
        for attr_type, attr_value in meta_tags:
            tag = soup.find('meta', {attr_type: attr_value})
            if tag and tag.get('content'):
                try:
                    price = Decimal(tag.get('content'))
                    break
                except:
                    continue
        
        if price:
            currency_tag = soup.find('meta', {'property': 'og:price:currency'}) or \
                          soup.find('meta', {'property': 'product:price:currency'})
            if currency_tag and currency_tag.get('content'):
                currency = currency_tag.get('content').upper()
            return (price, currency)
        
        return None
    
    def _extract_price_from_json_ld(self, soup: BeautifulSoup) -> Optional[tuple]:
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                if isinstance(data, list):
                    for item in data:
                        result = self._extract_price_from_json_data(item)
                        if result:
                            return result
                else:
                    result = self._extract_price_from_json_data(data)
                    if result:
                        return result
            except:
                continue
        return None
    
    def _extract_price_from_json_data(self, data: dict) -> Optional[tuple]:
        if not isinstance(data, dict):
            return None
            
        if data.get('@type') == 'Product' and 'offers' in data:
            offers = data['offers']
            if isinstance(offers, dict):
                price = offers.get('price') or offers.get('lowPrice')
                currency = offers.get('priceCurrency', 'USD')
                if price:
                    try:
                        return (Decimal(str(price)), currency)
                    except:
                        pass
            elif isinstance(offers, list) and offers:
                for offer in offers:
                    price = offer.get('price') or offer.get('lowPrice')
                    currency = offer.get('priceCurrency', 'USD')
                    if price:
                        try:
                            return (Decimal(str(price)), currency)
                        except:
                            continue
        return None
    
    def _extract_price_from_selectors(self, soup: BeautifulSoup) -> Optional[tuple]:
        price_selectors = [
            {'class': re.compile(r'price', re.I)},
            {'class': re.compile(r'cost', re.I)},
            {'class': re.compile(r'amount', re.I)},
            {'class': re.compile(r'product-price', re.I)},
            {'class': re.compile(r'price-current', re.I)},
            {'id': re.compile(r'price', re.I)},
            {'itemprop': 'price'},
            {'data-price': True},
        ]
        
        for selector in price_selectors:
            elements = soup.find_all(attrs=selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                
                data_price = elem.get('data-price')
                if data_price:
                    try:
                        price = Decimal(data_price)
                        currency = self._detect_currency(text, price)
                        return (price, currency)
                    except:
                        pass
                
                result = self._extract_price_from_text(text)
                if result:
                    return result
        
        return None
    
    def _extract_price_from_scripts(self, soup: BeautifulSoup) -> Optional[tuple]:
        scripts = soup.find_all('script')
        for script in scripts:
            if not script.string:
                continue
            
            price_patterns = [
                r'"price"\s*:\s*"?(\d+\.?\d*)"?',
                r'"price"\s*:\s*(\d+\.?\d*)',
                r'price:\s*"?(\d+\.?\d*)"?',
                r'"currentPrice"\s*:\s*"?(\d+\.?\d*)"?',
                r'"salePrice"\s*:\s*"?(\d+\.?\d*)"?',
            ]
            
            currency_patterns = [
                r'"currency"\s*:\s*"([A-Z]{3})"',
                r'"priceCurrency"\s*:\s*"([A-Z]{3})"',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, script.string)
                if match:
                    try:
                        price = Decimal(match.group(1))
                        currency = 'USD'
                        
                        for curr_pattern in currency_patterns:
                            curr_match = re.search(curr_pattern, script.string)
                            if curr_match:
                                currency = curr_match.group(1)
                                break
                        
                        if price > 0:
                            return (price, currency)
                    except:
                        continue
        
        return None
    
    def _extract_product_name(self, soup: BeautifulSoup) -> Optional[str]:
        name_sources = [
            soup.find('meta', {'property': 'og:title'}),
            soup.find('meta', {'name': 'twitter:title'}),
            soup.find('h1', {'class': re.compile(r'product', re.I)}),
            soup.find('h1'),
            soup.find('title'),
        ]
        
        for source in name_sources:
            if source:
                if source.name == 'meta':
                    name = source.get('content', '').strip()
                else:
                    name = source.get_text(strip=True)
                if name:
                    return name[:500]
        return None
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        image_sources = [
            soup.find('meta', {'property': 'og:image'}),
            soup.find('meta', {'name': 'twitter:image'}),
            soup.find('img', {'class': re.compile(r'product', re.I)}),
            soup.find('img', {'id': re.compile(r'product', re.I)}),
            soup.find('img', {'itemprop': 'image'}),
        ]
        
        for source in image_sources:
            if source:
                url = source.get('content') or source.get('src') or source.get('data-src')
                if url:
                    if url.startswith('http'):
                        return url
                    elif url.startswith('//'):
                        return 'https:' + url
                    elif url.startswith('/'):
                        from urllib.parse import urljoin
                        return urljoin(base_url, url)
        return None
    
    def _try_playwright_scraping(self, url: str) -> Optional[Dict]:
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=self._get_user_agent()
                )
                
                page.goto(url, wait_until='domcontentloaded', timeout=15000)
                time.sleep(2)
                
                content = page.content()
                browser.close()
                
                soup = BeautifulSoup(content, 'lxml')
                return self._extract_from_soup(soup, url)
        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {str(e)}")
            return None
    
    def _extract_from_soup(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        price_result = (
            self._extract_price_from_meta(soup) or
            self._extract_price_from_json_ld(soup) or
            self._extract_price_from_scripts(soup) or
            self._extract_price_from_selectors(soup)
        )
        
        if price_result:
            price, currency = price_result
            name = self._extract_product_name(soup)
            image_url = self._extract_image_url(soup, url)
            
            return {
                'price': price,
                'name': name,
                'image_url': image_url,
                'currency': currency
            }
        
        return None
    
    def scrape_product(self, url: str) -> Dict:
        try:
            headers = {
                'User-Agent': self._get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            result = self._extract_from_soup(soup, url)
            
            if result:
                return result
            
            logger.info(f"Basic scraping failed for {url}, trying Playwright...")
            result = self._try_playwright_scraping(url)
            
            if result:
                return result
            
            raise ValueError("Could not extract price from the page. The site may require manual price entry or uses advanced anti-scraping measures.")
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise Exception(f"Failed to scrape product: {str(e)}")

scraper_service = ScraperService()
