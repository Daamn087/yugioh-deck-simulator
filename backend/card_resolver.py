import httpx
from typing import List, Dict
from collections import Counter


# YGOProDeck API endpoint
YGOPRODECK_API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


async def resolve_card_data(passcodes: List[str]) -> tuple[List[str], Dict[str, str]]:
    """
    Resolve card passcodes to card names and image URLs using YGOProDeck API.
    
    Args:
        passcodes: List of card passcodes (with duplicates preserved)
        
    Returns:
        Tuple of (list of card names in original order, mapping of card name to image URL)
        
    Raises:
        ValueError: If API call fails or passcodes are invalid
    """
    if not passcodes:
        return [], {}
    
    # Normalize passcodes to 8-digit strings (zero-padded)
    normalized_passcodes = [str(p).zfill(8) for p in passcodes]
    
    # Get unique passcodes for API call
    unique_passcodes = list(set(normalized_passcodes))
    
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
    
    # Parse response - API returns {"data": [{"id": ..., "name": ..., "card_images": [...]}, ...]}
    if "data" not in data:
        raise ValueError("Invalid response from YGOProDeck API")
    
    # Build mappings
    passcode_to_name = {}
    name_to_image = {}
    
    for card in data["data"]:
        card_name = card.get("name", "")
        if not card_name:
            continue
            
        # Extract small image URL
        images = card.get("card_images", [])
        if images:
            # Prefer image_url_small for UI previews
            name_to_image[card_name] = images[0].get("image_url_small") or images[0].get("image_url")
            
        # Map the primary ID
        primary_id = str(card.get("id", "")).zfill(8)
        passcode_to_name[primary_id] = card_name
        
        # Map all associated image IDs (alternative artworks/passcodes)
        for img in images:
            img_id = str(img.get("id", "")).zfill(8)
            if img_id:
                passcode_to_name[img_id] = card_name
    
    # Map normalized passcodes to names, preserving order and duplicates
    card_names = []
    unresolved = []
    
    for passcode in normalized_passcodes:
        if passcode in passcode_to_name:
            card_names.append(passcode_to_name[passcode])
        else:
            unresolved.append(passcode)
    
    # Report unresolved passcodes
    if unresolved:
        raise ValueError(
            f"Could not resolve the following passcodes: {', '.join(sorted(set(unresolved)))}"
        )
    
    return card_names, name_to_image


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
            names, images = await resolve_card_data(test_passcodes)
            print("Resolved card names:")
            for name in names:
                print(f"  {name} (Image: {images.get(name, 'N/A')})")
            
            counts = count_cards(names)
            print("\nCard counts:")
            for name, count in counts.items():
                print(f"  {count}x {name}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())
