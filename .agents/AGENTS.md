# Workspace Rules: Premium Web Design & AI-Slop Prevention

Apply these rules during every file edit, code generation, and layout change in this project.

## 1. The 10k-Dollar Site Principles

To make the site look premium, expensive, and professional, always prioritize:
1. **Subject-based Signature Elements**: Design details should derive from the construction/materials world (masonry patterns, brick bonding layout, tactile textures, heavy lines, natural clay/slate color scales).
2. **Typography is UI**: Use high-contrast font weights, proper kerning, and letter-spacing. Avoid default system/AI font stacks (e.g. Arial, Inter). For Russian/Cyrillic websites, ensure that all selected web fonts fully support Cyrillic characters.
3. **Restraint over Clutter**: Luxury websites use whitespace and precise typography to convey quality. Avoid overdecorating or adding dozens of shadows and borders.
4. **State completeness**: Any interactive element (button, link, field, card) must support all 8 interaction states: default, hover, `:focus-visible`, `:active`, disabled, loading, error, success.

## 2. Anti-AI-Slop Visual Controls
- **NO Centering Everything**: AI models tend to center headers, buttons, and paragraphs. Use asymmetrical grids, left-aligned typography, or split-screen structures.
- **NO Purple/Acid Gradients**: Avoid the "generic SaaS" look. Use curated, context-specific color tokens (Oklch preferred). For construction and materials, default to earthy, mineral, clay, or masonry-related tones (e.g., terracottas, charcoal, warm clay whites, slates).
- **NO Numbered Steps (01 / 02 / 03)**: Do not use step numbers unless the content is a strict linear timeline or instruction sequence.
- **NO Emojis in UI**: Emojis cheapen the design. Use pure SVG icons (Lucide or similar clean line style, standardizing stroke-width to 1.5px or 2px).
- **NO Fabricated Metrics**: Never invent stats like "+47% conversion" or "trusted by 50,000+ teams" unless explicitly provided in the data files (e.g., `ДАННЫЕ-КОМПАНИИ.md` or `КАТАЛОГ-ПЛАН.md`). Use empty/dashed placeholders or real values.
- **NO Redrawn Device Frames**: Do not code mock browser windows, Mac title dots, or phone wrappers. Show images cleanly or wrap them in a hairline border.

## 3. Responsive Web Design Safety
- **No Horizontal Scroll**: Ensure `html` and `body` are configured with `overflow-x: clip` or `hidden`. All layout tracks (e.g., grid columns with images) must use `minmax(0, 1fr)` instead of bare `1fr`.
- **Tap Targets**: Mobile interactive elements (buttons, links, form inputs) must have a minimum clickable area of 44px (height/width).
- **Text Wrapping**: Use `overflow-wrap: anywhere` or `min-width: 0` to prevent long headings from clipping or breaking mobile screens.

## 4. MCP Tools Integration Workflows

### 21st.dev Magic component prompt (`@21st-dev/magic`)
- When requested to build interactive elements or complex components, query the `21st-dev` MCP to find premium React, Tailwind, or vanilla HTML components.
- In this static HTML project, write vanilla HTML/CSS counterparts of these components, preserving their high-end animation kinetics.

### Firecrawl competitor audit (`firecrawl`)
- Use Firecrawl to pull competitor code and visual layout structures when building new pages.
- Parse the page's HTML structure to extract its "design DNA" (colors, fonts, structure).

### Better-Design systems (`better-design`)
- Use the repository `/components` or `/registry` under `marvkr/better-design` via GitHub tools to read modern layouts (e.g., Monochrome Industrial, Precision Light) and port their token variables to `tokens.css` or `styles.css`.

## 5. Animation (GSAP & ScrollTrigger)
- Animations should feel fluid, intentional, and performant. Use GSAP timelines for orchestrated reveals rather than random visual transitions.
- Use `ScrollTrigger` for parallax scroll reveals, scroll-driven text fading, or element pinning. Keep transforms hardware-accelerated (`transform: translate3d(...)` or native CSS variables).

## 6. Language & Communication
- All audit findings, reports, UI text, and explanations must be generated in Russian.
