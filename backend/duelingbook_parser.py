import re
from typing import Dict
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def extract_deck_id(url: str) -> str:
    """Extract deck ID from DuelingBook URL."""
    match = re.search(r'[?&]id=(\d+)', url)
    if not match:
        raise ValueError("Invalid DuelingBook URL. Expected format: https://www.duelingbook.com/deck?id=XXXXXXXX")
    return match.group(1)


def parse_duelingbook_deck(url: str) -> Dict[str, int]:
    """
    Fetch and parse a DuelingBook deck URL to extract main deck cards using Selenium.
    
    Args:
        url: DuelingBook deck URL (e.g., https://www.duelingbook.com/deck?id=19462366)
        
    Returns:
        Dictionary mapping card names to their counts in the main deck
        
    Raises:
        ValueError: If URL is invalid or deck cannot be parsed
        WebDriverException: If browser automation fails
    """
    deck_id = extract_deck_id(url)
    deck_url = f"https://www.duelingbook.com/deck?id={deck_id}"
    
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = None
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Navigate to the deck page
        driver.get(deck_url)
        
        # Wait for the deck cards to load
        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "deck_cards"))
        )
        
        # Give it extra time for all cards to load
        import time
        time.sleep(3)
        
        # Try to get deck text from preview first
        try:
            preview_element = driver.find_element(By.ID, "preview_txt")
            deck_text = preview_element.text
        except:
            deck_text = ""
        
        # If preview is empty, use other methods
        if not deck_text:
            try:
                # User suggestion: Look for span tags with class "name_txt" which contain the card title
                try:
                    deck_cards_container = driver.find_element(By.CSS_SELECTOR, ".deck_bg .deck_cards")
                    
                    # Look for elements with class "name_txt"
                    text_elements = deck_cards_container.find_elements(By.CLASS_NAME, "name_txt")
                    
                    main_deck_cards = []
                    for elem in text_elements:
                        # Get visible text or text content if hidden
                        card_name = elem.text.strip() or elem.get_attribute("textContent").strip() or elem.get_attribute("innerHTML").strip()
                        
                        if card_name:
                            main_deck_cards.append(card_name)
                    
                    if main_deck_cards:
                        card_counts = Counter(main_deck_cards)
                        return dict(card_counts)
                        
                except Exception:
                    pass

                # Fallback: Get all card elements in the main deck
                deck_cards_container = driver.find_element(By.CSS_SELECTOR, ".deck_bg .deck_cards")
                card_elements = deck_cards_container.find_elements(By.CLASS_NAME, "cardfront")
                
                # Extract card names from various attributes
                main_deck_cards = []
                for card_elem in card_elements:
                    # Try to get the background image URL which often contains the card name
                    card_style = card_elem.get_attribute("style")
                    if 'background-image' in (card_style or ''):
                        # Extract card name from background URL
                        # URL format usually: .../cards/Card_Name.jpg
                        match = re.search(r'cards/([^/]+)\.jpg', card_style)
                        if match:
                            # Decode URL: 'Card_Name' -> 'Card Name'
                            # Also handle URL encoding if present
                            raw_name = match.group(1)
                            import urllib.parse
                            card_name = urllib.parse.unquote(raw_name).replace('_', ' ')
                            main_deck_cards.append(card_name)
                            continue

                    # Attempt to find the name_txt span relative to this card if it exists
                    try:
                        text_span = card_elem.find_element(By.CLASS_NAME, "name_txt")
                        card_name = text_span.text.strip() or text_span.get_attribute("textContent").strip()
                        if card_name:
                            main_deck_cards.append(card_name)
                            continue
                    except:
                        pass
                
                if not main_deck_cards:
                     raise ValueError(f"Could not extract cards from deck elements. Found {len(card_elements)} card elements but no names.")
                
                # Count occurrences
                card_counts = Counter(main_deck_cards)
                return dict(card_counts)
                
            except Exception as e:
                print(f"DEBUG: Exception: {e}")
                import traceback
                traceback.print_exc()
                raise ValueError(f"Could not parse deck: {str(e)}")
        
        # Parse the deck text from preview
        lines = deck_text.split('\n')
        main_deck_cards = []
        in_main_deck = False
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if 'Main Deck' in line or 'Deck (' in line:
                in_main_deck = True
                continue
            elif 'Side Deck' in line or 'Extra Deck' in line:
                in_main_deck = False
                continue
            
            # Parse card lines in main deck section
            if in_main_deck and line:
                # Match patterns like "3x Card Name" or "Card Name x3"
                match = re.match(r'(\d+)x?\s+(.+)', line)
                if match:
                    count = int(match.group(1))
                    card_name = match.group(2).strip()
                    main_deck_cards.extend([card_name] * count)
        
        if not main_deck_cards:
            raise ValueError("Could not parse any cards from the deck. The page format may have changed.")
        
        # Count occurrences
        card_counts = Counter(main_deck_cards)
        
        return dict(card_counts)
        
    except TimeoutException:
        raise ValueError("Timeout while loading DuelingBook page. The page took too long to load.")
    except WebDriverException as e:
        raise ValueError(f"Browser automation error: {str(e)}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    # Test with example URL
    test_url = "https://www.duelingbook.com/deck?id=19462366"
    try:
        result = parse_duelingbook_deck(test_url)
        print("Parsed deck:")
        for card, count in sorted(result.items()):
            print(f"  {count}x {card}")
        print(f"\nTotal cards: {sum(result.values())}")
    except Exception as e:
        print(f"Error: {e}")
