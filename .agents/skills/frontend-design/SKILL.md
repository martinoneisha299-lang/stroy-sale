---
name: frontend-design
description: Create distinctive, premium, and non-generic frontend layouts, user interfaces, HTML page structures, and custom CSS styles. Triggers on requests involving UI design, frontend styling, layout adjustments, web page structure, and design aesthetic choices.
---

# Frontend Design

Approach design tasks as a Design Lead at an elite creative studio. The client expects a premium, custom interface that does not look like a template. Make deliberate, opinionated choices about typography, color palettes, and structural layouts.

## 1. Subject-Matter Grounding
- Settle on the core subject, audience, and the page's primary goal before writing any code.
- Draw design metaphors from the subject's world. For construction, building materials, masonry, slate, and clay, use:
  - Masonry-inspired grid structures (staggered cards or alternating column spans).
  - Clean, heavy borders (resembling architectural blueprints or mortar joints).
  - Material-honest imagery, textures, or SVG line-art.

## 2. Design Principles

### The Hero is a Thesis
- Avoid the average "centered text with two buttons and a gradient background" layout.
- Open with a high-impact, custom hero section:
  - An asymmetric layout (e.g., text block paired with an interactive or large lifestyle photo).
  - An interactive canvas, animated SVG, or a custom-designed interactive product showcase.

### Typography carrying Personality
- Pair display and body fonts intentionally. Use font pairings with high contrast in weight or style (e.g., a bold, characterful serif display font with a clean, neutral sans-serif body font).
- Establish a strict type scale using CSS variables (`--font-display`, `--font-body`, `--text-size-hero`, etc.).
- Treat typography as a main design element, not just a content delivery vehicle. Ensure proper Cyrillic support for Russian text.

### Structural Integrity
- Layout devices (borders, lines, grids, badges) must convey real content relationships.
- Do not use generic steps (01 / 02 / 03) unless they represent a strict, sequential process where order is crucial.
- Leverage grid structures to build rhythm and contrast, shifting away from generic 3-card rows.

### Restraint & Execution
- Premium designs look expensive because they are restrained, not busy. Prioritize negative space (breathing room) over multiple nested shadows, cards, and borders.
- Keep the design clean, focusing on crisp rendering, perfect alignment, and high readability.
