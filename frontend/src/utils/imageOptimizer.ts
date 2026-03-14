import { PROXY_URL } from '../api';

/**
 * Image optimizer service for client-side image processing.
 * Used to convert original card images to optimized WebP format to save space in IndexedDB.
 */

export async function optimizeImage(imageUrl: string, quality = 0.8): Promise<Blob> {
    // Route through our backend proxy to bypass CORS
    const proxiedUrl = `${PROXY_URL}?url=${encodeURIComponent(imageUrl)}`;
    
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous'; // Still needed even with proxy to play safe
        
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                reject(new Error('Failed to get canvas context'));
                return;
            }
            
            ctx.drawImage(img, 0, 0);
            
            // Convert to WebP
            canvas.toBlob(
                (blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Canvas toBlob failed'));
                    }
                },
                'image/webp',
                quality
            );
        };
        
        img.onerror = () => {
            reject(new Error(`Failed to load image via proxy: ${proxiedUrl}`));
        };
        
        img.src = proxiedUrl;
    });
}

/**
 * Utility to convert a Blob to DataURL for display in <img> tags.
 */
export function blobToDataURL(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}
