from typing import List


def parse_ydk_deck(ydk_content: bytes) -> List[str]:
    """
    Parse a YDK deck file to extract card passcodes from the main deck.
    
    YDK file format:
        #created by ...
        #main
        89631139
        89631139
        14558127
        #extra
        63767246
        !side
        12345678
    
    Args:
        ydk_content: Raw bytes of the YDK file
        
    Returns:
        List of card passcodes (as strings) from the main deck section.
        Duplicates are preserved (each line = one card copy).
        
    Raises:
        ValueError: If YDK file is malformed or has no main deck section
    """
    try:
        # Decode bytes to string
        content = ydk_content.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Invalid YDK file encoding. File must be UTF-8 text.")
    
    lines = content.splitlines()
    passcodes = []
    in_main_section = False
    found_main_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check for section markers
        if line.lower() == '#main':
            in_main_section = True
            found_main_section = True
            continue
        elif line.startswith('#') or line.startswith('!'):
            # Entering a different section (extra or side)
            in_main_section = False
            continue
        
        # Extract passcodes from main section
        if in_main_section:
            # Passcodes should be numeric (typically 8 digits)
            if line.isdigit():
                passcodes.append(line)
            else:
                # Skip non-numeric lines (could be comments)
                continue
    
    if not found_main_section:
        raise ValueError("YDK file must contain a #main section")
    
    if not passcodes:
        raise ValueError("No cards found in main deck section")
    
    return passcodes


if __name__ == "__main__":
    # Test with example YDK
    example_ydk = """#created by ...
#main
89631139
89631139
89631139
14558127
14558127
14558127
#extra
63767246
63767246
!side
12345678
"""
    
    try:
        result = parse_ydk_deck(example_ydk.encode('utf-8'))
        print("Parsed passcodes:")
        for passcode in result:
            print(f"  {passcode}")
        print(f"\nTotal cards: {len(result)}")
    except Exception as e:
        print(f"Error: {e}")
