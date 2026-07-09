---
name: gsap-animations
description: Create rich, modern interactive animations using GSAP, ScrollTrigger, and Timeline libraries. Triggers on requests for smooth scroll, parallax effects, interactive hover transitions, and landing page load animations.
---

# GSAP & ScrollTrigger Animations

Orchestrate motion to enhance content readability and user engagement. Avoid random animations that slow down the page or feel gimmicky.

## 1. Setup & Registration
- Always import GSAP core and its plugins cleanly.
- Register plugins immediately after loading:
  ```javascript
  gsap.registerPlugin(ScrollTrigger);
  ```
- Use `gsap.timeline()` for sequences instead of chaining delays manually.

## 2. Animation Patterns

### Parallax Scrolls
- Animate elements on scroll using `scrub: true` or numeric values (e.g., `scrub: 1` for smoother catch-up kinetics).
- Keep motion ranges subtle. Avoid moving elements by more than `100px` to prevent layout breaks.

### Orchestrated Reveals
- Use `stagger` to animate groups of elements (like grids of product cards or feature rows) sequentially.
- Trigger reveals as elements enter the viewport:
  ```javascript
  gsap.from(".card", {
    y: 30,
    opacity: 0,
    stagger: 0.1,
    duration: 0.6,
    scrollTrigger: {
      trigger: ".card-grid",
      start: "top 85%"
    }
  });
  ```

## 3. Performance & Mobile Rules
- **Disable Heavy Scrolls on Mobile**: Use `ScrollTrigger.matchMedia()` to scale down or disable scrolling animations for viewports smaller than `768px` to ensure smooth rendering on touch devices.
- **Hardware Acceleration**: Always animate transform properties (`x`, `y`, `scale`, `rotation`) and opacity. Never animate layout-triggering properties (`width`, `height`, `margin`, `top`, `left`).
- **Will-Change Hint**: Add `will-change: transform` or `will-change: opacity` in CSS to elements that undergo complex scroll-linked animations.
