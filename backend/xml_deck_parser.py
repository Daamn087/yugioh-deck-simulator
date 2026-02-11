import xml.etree.ElementTree as ET
from typing import Dict
from collections import Counter
import html


def parse_xml_deck(xml_content: bytes) -> Dict[str, int]:
    """
    Parse an XML deck file to extract main deck cards.
    
    Args:
        xml_content: Raw bytes of the XML file
        
    Returns:
        Dictionary mapping card names to their counts in the main deck
        
    Raises:
        ValueError: If XML is malformed or missing required structure
    """
    try:
        # Parse XML from bytes
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    
    # Find the <main> section
    main_section = root.find('main')
    if main_section is None:
        raise ValueError("XML deck file must contain a <main> section")
    
    # Extract all card elements from main deck
    card_elements = main_section.findall('card')
    
    if not card_elements:
        raise ValueError("No cards found in main deck section")
    
    # Extract card names and count occurrences
    card_names = []
    for card_elem in card_elements:
        card_name = card_elem.text
        if card_name:
            # Decode HTML entities (e.g., &amp; -> &)
            card_name = html.unescape(card_name.strip())
            card_names.append(card_name)
    
    if not card_names:
        raise ValueError("Could not extract any card names from the deck")
    
    # Count occurrences
    card_counts = Counter(card_names)
    
    return dict(card_counts)


if __name__ == "__main__":
    # Test with example XML
    example_xml = """<?xml version="1.0" encoding="utf-8" ?>
<deck name="Test Deck">
 <main>
  <card id="16582" passcode="08379983">Lunalight Gold Leo</card>
  <card id="16582" passcode="08379983">Lunalight Gold Leo</card>
  <card id="16582" passcode="08379983">Lunalight Gold Leo</card>
  <card id="8504" passcode="14558127">Ash Blossom &amp; Joyous Spring</card>
  <card id="8504" passcode="14558127">Ash Blossom &amp; Joyous Spring</card>
 </main>
 <side>
  <card id="1233" passcode="75652080">Double Cyclone</card>
 </side>
</deck>"""
    
    try:
        result = parse_xml_deck(example_xml.encode('utf-8'))
        print("Parsed deck:")
        for card, count in sorted(result.items()):
            print(f"  {count}x {card}")
        print(f"\nTotal cards: {sum(result.values())}")
    except Exception as e:
        print(f"Error: {e}")
