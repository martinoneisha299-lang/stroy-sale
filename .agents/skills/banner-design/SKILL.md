---
name: banner-design
description: Design premium promotional banners, advertising creatives, discount cards, and seasonal marketing components. Triggers on building hero banners, discount alerts, promotional sliders, and countdown timers.
---

# Banner & Promo Design

Promotional elements must feel integrated and premium, avoiding cheap, blinky "sticker" looks.

## 1. Visual Layout Rules
- **Margins & Padding**: Give text elements ample breathing room. Use at least `32px` of internal padding for banners.
- **Typography Scale**: Ensure a clear visual hierarchy. Use a large, bold display font for the offer headline, paired with a small, uppercase, widely tracked label (eyebrow text) to introduce the promotion.
- **Unified Palette**: Banner colors should match the site's primary tokens (`tokens.css`). Accent bands should use soft tinted backgrounds (`--color-tint`) or solid dark panels (`--color-ink`) with high contrast text.

## 2. Dynamic Expiry and Control
- All temporary promotional banners must use standard data attributes to manage lifecycle programmatically.
- **Auto-Hide Attribute**: Specify the date after which the banner should automatically hide using `data-until="YYYY-MM-DD"`.
- Make sure the global scripts parse these attributes and add `display: none` or a hidden class once the date has passed.
