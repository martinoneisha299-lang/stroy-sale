---
name: ecommerce-cro-design
description: Design and optimize high-converting e-commerce catalog interfaces, product cards, material calculators, faceted filters, and lead capture funnels. Triggers on requests involving catalog usability, product page conversion, checkout/quotation forms, filters, calculators, and commercial UI ergonomics.
---

# E-Commerce & Conversion Rate Optimization (CRO) Design

This skill provides specialized guidelines for building high-converting, frictionless e-commerce and catalog interfaces for building materials, construction, and high-ticket B2B/B2C products.

## 1. Product Card Architecture ($10k Standard)
- **Visual Clarity**: Clean rectangular product image with natural aspect ratio (4:3 or 1:1), no rounded corners on photos.
- **Secondary Image Hover**: Smooth crossfade to a contextual/lifestyle photo or close-up texture (`.p-alt`) on desktop hover.
- **Hierarchy of Specs**:
  - Category / Brand / Factory tag (subtle, uppercase, `var(--ink-4)`).
  - Product Title: Bold, high-contrast, strictly balanced wrapping (`text-wrap: balance`).
  - Key Technical Metrics: 2–3 key parameters in compact chips or data pairs (e.g. `Формат: 1NF`, `Поверхность: Рустик`, `Морозостойкость: F100`).
  - Pricing Block: Primary unit price in large bold font (`38.50 ₽/шт`) + calculated packaging / square meter rate (`1 848 ₽/м²` or `18 480 ₽/поддон`).
  - Action Element: High-contrast action button ("В заявку" / "Купить") with immediate quantity adjustment (`+` / `-` controls) or direct drawer trigger.

## 2. Faceted Filter & Catalog Navigation
- **Desktop Sidebar**:
  - Sticky sidebar with independent scrolling if filters exceed viewport height.
  - Collapsible filter sections with counter badges indicating active selections.
  - Instant live filtering (dynamic DOM updating without full page reload).
- **Mobile Filter Drawer**:
  - Full-height or 85vh bottom-sheet modal with sticky header (Reset button) and sticky footer (Apply button with live matching product count, e.g. "Показать 48 товаров").
  - Large touch-friendly filter chips and checkboxes (minimum 44px tap zone).
- **Active Filter Pills Bar**:
  - Horizontal scrollable or wrapped chips bar showing all active filters with single-click remove (`×`) and "Очистить все" trigger.

## 3. Commercial Lead Funnels & Quotation Drawer
- **1-Click Quick Order & Quotation Drawer**:
  - Slide-out side drawer displaying selected products, subtotal, pallet/tonnage estimation, and delivery calculator.
  - Minimal friction input fields: Phone number with auto-formatting mask (`+7 (___) ___-__-__`), name, optional delivery location.
  - Zero cognitive overload: Clear shipping notes ("Доставка манипулятором по Краснодару и краю", "Расчет точного объема за 15 минут").
- **Trust Elements (Anti-AI-Slop)**:
  - No fake countdown timers, stock tickers ("Осталось 3 шт"), or fabricated 5-star badges.
  - Authentic trust indicators: Direct factory warranty certificates, physical showroom address with map/directions, direct WhatsApp/Telegram manager links.

## 4. Material Calculators & Estimators
- **Interactive Calculators**:
  - Real-time conversion between units: Pieces (шт) ⇄ Square meters (м²) ⇄ Pallets (поддоны) ⇄ Tons (тонны).
  - Brick calculator: Wall area ($S = L \times H$), masonry thickness (0.5, 1, 1.5, 2 bricks), mortar joint allowance (+5% waste factor).
  - Paving tile calculator: Square meters + curb/border length + base sand/gravel estimation.
  - Roof calculator: Sheet overlap allowance, ridge caps, self-tapping screws count.
- **Immediate State Feedback**:
  - Results update smoothly without lag or page refresh as sliders or inputs change.
  - One-click "Добавить расчет в заявку" button that transfers all calculated quantities directly into the cart/order sheet.
