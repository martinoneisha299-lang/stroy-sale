---
name: modern-css-architecture
description: Write robust, modern, high-performance CSS architecture, design tokens, fluid typography, responsive layout grids, and zero-CLS styling. Triggers on requests involving CSS styling, tokens, layout refactoring, CSS Grid/Flexbox architecture, responsive breakpoints, and performance styling.
---

# Modern CSS Architecture & Performance Styling

This skill enforces strict, scalable, and modern CSS3 standards for production-grade web applications.

## 1. Design Token Integrity
- **Single Source of Truth**: All core properties (colors, typography, spacing, elevations, radii, transitions) are managed in `tokens.css`.
- **Systematic Color Scale**:
  - Surfaces: `--paper`, `--tile`, `--field` (clean neutral slate/sand undertones).
  - Borders: `--rule`, `--rule-strong` (crisp 1px hairline separation).
  - Typography: `--ink`, `--ink-2`, `--ink-3`, `--ink-4` (accessible contrast ratios >= 4.5:1).
  - Accents: `--accent` (reserved strictly for primary conversion CTAs and active states, <= 5% screen area).
- **Zero Hardcoded Magic Numbers**: Never use raw hex codes or random pixel offsets in component files. Reference design tokens (`var(--...)`).

## 2. Fluid Layout & Responsive Typographic Scales
- **Fluid Typography**:
  - Use `clamp()` for smooth scaling between mobile and desktop without sudden jarring jumps:
    `font-size: clamp(1.75rem, 4vw + 1rem, 2.75rem);`
- **Modern Grid Systems**:
  - Always use `minmax(0, 1fr)` for dynamic grid columns to prevent layout blowout from wide images or preformatted code:
    `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));`
  - Leverage `subgrid` for aligning card headers, prices, and CTA buttons across varying row heights.

## 3. High Performance & Zero Cumulative Layout Shift (CLS = 0)
- **Aspect Ratio Locking**:
  - Explicitly declare `aspect-ratio: 4 / 3` or `width` + `height` attributes on all image containers.
  - Use lightweight skeleton loaders or subtle placeholder backgrounds (`--field`) during image load.
- **Hardware-Accelerated Interactions**:
  - Transitions and animations must target GPU-friendly properties only (`transform`, `opacity`, `filter`).
  - Avoid animating layout-triggering properties (`width`, `height`, `margin`, `top`, `left`).
- **Isolation & Containment**:
  - Use `contain: content` or `contain: layout style` on high-frequency catalog items to optimize browser paint performance.

## 4. Modern Interactive States (8 Interaction States)
Every interactive element (button, link, field, chip, dropdown) must have distinct styles for:
1. `default`
2. `:hover`
3. `:focus-visible` (crisp 2px outline with outline-offset)
4. `:active` (subtle translate/scale press effect)
5. `:disabled` (`opacity: 0.5`, `cursor: not-allowed`)
6. `loading` (spinner or skeleton overlay)
7. `error` (`--err` accent border + hint)
8. `success` (`--ok` feedback state)
