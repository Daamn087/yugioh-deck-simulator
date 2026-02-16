import httpx
from typing import List, Dict
from collections import Counter


# YGOProDeck API endpoint
YGOPRODECK_API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


async def resolve_card_names(passcodes: List[str]) -> List[str]:
    """
    Resolve card passcodes to card names using YGOProDeck API.
    
    Args:
        passcodes: List of card passcodes (with duplicates preserved)
        
    Returns:
        List of card names in the same order as passcodes
        
    Raises:
        ValueError: If API call fails or passcodes are invalid
    """
    if not passcodes:
        return []
    
    # Get unique passcodes for API call
    unique_passcodes = list(set(passcodes))
    
    # Build batch API request (comma-separated IDs)
    passcode_param = ",".join(unique_passcodes)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                YGOPRODECK_API,
                params={"id": passcode_param}
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise ValueError("One or more card passcodes are invalid or not found in the database")
        raise ValueError(f"Failed to fetch card data from YGOProDeck API: {e}")
    except httpx.RequestError as e:
        raise ValueError(f"Network error while fetching card data: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error resolving card names: {e}")
    
    # Parse response - API returns {"data": [{"id": ..., "name": ...}, ...]}
    if "data" not in data:
        raise ValueError("Invalid response from YGOProDeck API")
    
    # Build passcode -> name mapping
    passcode_to_name = {}
    for card in data["data"]:
        card_id = str(card.get("id", ""))
        card_name = card.get("name", "")
        if card_id and card_name:
            passcode_to_name[card_id] = card_name
    
    # Map passcodes to names, preserving order and duplicates
    card_names = []
    unresolved = []
    
    for passcode in passcodes:
        if passcode in passcode_to_name:
            card_names.append(passcode_to_name[passcode])
        else:
            unresolved.append(passcode)
    
    # Report unresolved passcodes
    if unresolved:
        raise ValueError(
            f"Could not resolve the following passcodes: {', '.join(set(unresolved))}"
        )
    
    return card_names


def count_cards(card_names: List[str]) -> Dict[str, int]:
    """
    Count occurrences of each card name.
    
    Args:
        card_names: List of card names (with duplicates)
        
    Returns:
        Dictionary mapping card names to their counts
    """
    return dict(Counter(card_names))


if __name__ == "__main__":
    import asyncio
    
    # Test with example passcodes
    test_passcodes = [
        "89631139",  # Blue-Eyes White Dragon
        "89631139",
        "89631139",
        "14558127",  # Ash Blossom & Joyous Spring
        "14558127",
        "14558127"
    ]
    
    async def test():
        try:
            names = await resolve_card_names(test_passcodes)
            print("Resolved card names:")
            for name in names:
                print(f"  {name}")
            
            counts = count_cards(names)
            print("\nCard counts:")
            for name, count in counts.items():
                print(f"  {count}x {name}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())
