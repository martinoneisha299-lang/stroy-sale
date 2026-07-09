---
name: ui-ux-pro-max
description: Select and configure design systems, color palettes, fonts, typographic scales, responsive grids, and UX interaction guidelines. Triggers on requests for color scheme setup, design tokens, typography choices, responsive design, form UX, and mobile-first auditing.
---

# UI/UX Pro Max

Enforce rigorous UX standards and design token structures. Every interface must balance aesthetics, accessibility, and high performance.

## 1. Design Token System
- All color, typography, and spacing variables must be defined as central custom CSS properties (in `tokens.css` or `:root` of `styles.css`).
- **Color Space**: Prefer `oklch()` or `hsl()` for fluid adjustments. Keep color tokens clean and contextual:
  - `--color-bg`: Page background.
  - `--color-surface`: Card/panel backgrounds.
  - `--color-accent`: Main brand color.
  - `--color-text`: Primary text.
  - `--color-text-muted`: Secondary/muted text.
- **Spacing Scale**: Implement a strict 4-point or 8-point scale using variables (e.g., `--space-xs: 4px`, `--space-sm: 8px`, `--space-md: 16px`, `--space-lg: 24px`, `--space-xl: 32px`, `--space-2xl: 48px`, `--space-3xl: 64px`). Never use arbitrary pixel margins or paddings.

## 2. Interactive States & Touch Targets
Every interactive component (buttons, inputs, selectable cards, chips) must explicitly implement styles for **all 8 interactive states**:
1. **Default**: Normal, unfocused state.
2. **Hover**: Desktop hover style (smooth color change or minor scale transform, transitions under 150ms).
3. **Focus (`:focus-visible`)**: Keyboard navigation focus ring with high visibility.
4. **Active (`:active`)**: Press down style (slight scale decrease or darker background to mimic physical feedback).
5. **Disabled**: Visually muted, non-interactive state (`opacity: 0.5; pointer-events: none`).
6. **Loading**: Spinning indicator or text replacement to prevent multiple form submissions.
7. **Error**: Red/invalid borders with descriptive helper text.
8. **Success**: Green/valid indicator (e.g., checkmarks or green success borders).

- **Touch Size**: Ensure all interactive mobile elements have a minimum target size of 44px by 44px.

## 3. Responsive Safety
- Verify layouts at 320px, 375px (standard mobile), 768px (tablet), and 1280px (desktop).
- Never allow horizontal overflow scroll. Set `html, body { overflow-x: clip; }`.
- When styling images within grids, use `minmax(0, 1fr)` columns to prevent layout breakages.
