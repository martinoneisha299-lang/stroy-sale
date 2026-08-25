---
name: mobile-first-pro
description: Enforce mobile-first UX excellence, touch ergonomics, 375px viewport safety, iOS Safari compatibility, and thumb-zone optimization. Triggers on requests involving mobile design, touch interfaces, mobile navigation, responsive auditing, and smartphone layout debugging.
---

# Mobile-First UX & Touch Ergonomics

This skill ensures that mobile users receive a best-in-class, app-like experience with zero glitches, layout shifts, or awkward touch targets.

## 1. 375px Viewport & Safe Area Rules
- **Base Testing Width**: Always validate on `375px` (iPhone SE / standard compact smartphone) and `430px` (iPhone Pro Max).
- **Zero Horizontal Scroll**:
  - `html, body { overflow-x: clip; width: 100%; }`
  - Long headlines must use `text-wrap: balance` and `overflow-wrap: anywhere`.
- **Dynamic Viewport Height**:
  - Use `100dvh` or `100svh` instead of standard `100vh` for full-height drawers and hero screens to avoid being covered by mobile browser address bars.
- **iOS Safe Areas**:
  - Sticky bottom action bars and mobile tab-bars must include `padding-bottom: max(12px, env(safe-area-inset-bottom))`.

## 2. Thumb-Zone Ergonomics & Touch Targets
- **Minimum 44px Tap Zone**:
  - Every interactive button, filter chip, link, search icon, quantity stepper, and menu item must have at least `44px × 44px` clickable area.
- **Bottom Navigation Priority**:
  - Place primary mobile actions (Catalog trigger, Filter toggle, Cart/Quotation button, Call/WhatsApp direct line) in a sticky bottom navigation bar or bottom sheet within natural thumb reach.

## 3. iOS Safari Form & Input Ergonomics
- **No Unwanted Auto-Zoom**:
  - All `<input>`, `<select>`, and `<textarea>` elements must have a minimum `font-size: 16px` on mobile screens to prevent iOS Safari from forcefully zooming in on focus.
- **Input Keyboards**:
  - Use proper `inputmode` and `type` attributes (`inputmode="tel"` for phone numbers, `inputmode="numeric"` for quantities, `type="email"` for email fields).

## 4. Mobile First-Screen (Above-the-Fold) Budget
- The first screen on mobile (`~640px` height) must deliver maximum information density without clutter:
  - Header: Logo + Phone CTA + Cart trigger (< 56px height).
  - Compact Hero: Headline + 1-sentence value proposition + Category quick chips.
  - Peek of the Catalog: The top edge of the first catalog items or promo cards MUST peek into the first viewport (at 550–600px) so the user instinctively knows to scroll down.
