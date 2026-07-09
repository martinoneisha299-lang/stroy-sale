---
name: design-taste-frontend
description: Enforce top-tier, $10k-level visual aesthetics, layout rhythm, whitespace, and high-end editorial and minimalist looks. Triggers on requests to make a site look premium, expensive, polished, professional, and unique.
---

# Design Taste Frontend

This skill enforces distinct visual styles (aesthetics) and layout arrangements, avoiding average visual distributions.

## 1. Curated Visual Directions

### A. Industrial Brutalist (Highly recommended for Construction & Materials)
- **Macrostructure**: Solid structural lines, explicit layout grids, dense monospace tags, and asymmetric layouts.
- **Color System**: Earthy mineral colors (masonry reds, charcoal slate, sand beige, deep industrial black, cement whites).
- **Typography**: Bold, heavy sans-serif headers paired with monospace accents (`JetBrains Mono`, `Roboto Mono`) for technical specs.
- **Details**: `1px` or `2px` crisp border lines (`var(--color-border)`), sharp corners (`border-radius: 0`), and flat, high-contrast button styling.

### B. Warm Editorial
- **Macrostructure**: High-end magazine style with generous margins, asymmetric column spans, and elegant photography.
- **Color System**: Soft cream backgrounds (`#fbfaf7`), dark charcoal ink text, and earthy warm accent points (terracotta, clay red).
- **Typography**: Large, high-contrast serif displays (`Playfair Display`, `Lora`) paired with clean geometric sans-serif body copy.
- **Details**: Elegant, fine borders, soft gradients, and subtle, smooth transitions.

### C. Modern Minimalist (The Apple/Stripe Aesthetic)
- **Macrostructure**: Strict geometry, massive breathing room, and left-aligned components.
- **Color System**: Clean monochrome scale with a single, highly refined colored anchor point.
- **Typography**: Inter/Geist-like typography with precise tracking and letter-spacing modifications.
- **Details**: Sub-pixel lines, soft elevations (`box-shadow`), and rounded button shapes (`border-radius: 8px`).

## 2. General Aesthetic Rules
- Avoid standard 3-column rows that repeat across multiple sections. Alternating grids (e.g. 5fr/7fr in one section, 3-column masonry in the next) provide visual texture.
- Real content should drive the layouts. If products have images, grid tracks must size dynamically based on the aspect ratios of the images.
- Use CSS transitions for interactive states to make the site feel responsive and premium.
