/** Types for `tokens.js`, which is CommonJS so `tailwind.config.js` can read
 *  the same file the renderer does. See that file for why. */

export type AssistantHue = 'idle' | 'listening' | 'thinking' | 'speaking' | 'acting'

export declare const COLORS: Record<string, string>
export declare const HUES: Record<AssistantHue, string>
export declare const RGB: Record<AssistantHue, [number, number, number]>
export declare function hexToRgb(hex: string): [number, number, number]
