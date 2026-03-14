/**
 * Simple YDK parser for the frontend.
 * Extracts card passcodes from the #main section.
 */
export function parseYDK(content: string): string[] {
    const lines = content.split(/\r?\n/);
    const passcodes: string[] = [];
    let inMainSection = false;
    
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        
        if (line.toLowerCase() === '#main') {
            inMainSection = true;
            continue;
        } else if (line.startsWith('#') || line.startsWith('!')) {
            inMainSection = false;
            continue;
        }
        
        if (inMainSection) {
            // Check if it's a numeric passcode (typically 8 digits)
            if (/^\d+$/.test(line)) {
                passcodes.push(line.padStart(8, '0'));
            }
        }
    }
    
    return passcodes;
}
