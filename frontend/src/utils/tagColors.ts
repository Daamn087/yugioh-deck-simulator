/**
 * Utility functions for generating consistent, deterministic colors for tags
 */

/**
 * Simple hash function to convert a string to a number
 * Uses the DJB2 algorithm for consistent hashing
 */
function hashString(str: string): number {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) + hash) + str.charCodeAt(i); // hash * 33 + c
    }
    return Math.abs(hash);
}

/**
 * Generate a consistent gradient color for a tag name
 * Uses HSL color space to ensure vibrant, harmonious colors
 * 
 * @param tagName - The name of the tag
 * @returns CSS gradient string
 */
export function getTagColor(tagName: string): string {
    const hash = hashString(tagName);

    // Generate hue from hash (0-360 degrees)
    const hue = hash % 360;

    // Create a second hue for the gradient (offset by 20-40 degrees)
    const hueOffset = 20 + (hash % 20);
    const hue2 = (hue + hueOffset) % 360;

    // Keep saturation and lightness consistent for visual harmony
    // Saturation: 70% for vibrant colors
    // Lightness: 60% for first color, 50% for second (slightly darker)
    const color1 = `hsl(${hue}, 70%, 60%)`;
    const color2 = `hsl(${hue2}, 70%, 50%)`;

    return `linear-gradient(135deg, ${color1}, ${color2})`;
}

/**
 * Generate a consistent background color for tag badges (lighter version)
 * Used for tag badges in card effects editor
 * 
 * @param tagName - The name of the tag
 * @returns Object with background and color CSS values
 */
export function getTagBadgeColors(tagName: string): { background: string; color: string; border: string } {
    const hash = hashString(tagName);
    const hue = hash % 360;

    // Lighter background with lower saturation and higher lightness
    const background = `hsla(${hue}, 60%, 25%, 0.3)`;
    const color = `hsl(${hue}, 70%, 65%)`;
    const border = `hsla(${hue}, 60%, 50%, 0.4)`;

    return { background, color, border };
}
