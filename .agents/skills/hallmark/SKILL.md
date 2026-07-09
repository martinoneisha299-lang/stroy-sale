---
name: hallmark
description: Perform visual audits, quality checks, anti-slop inspections, design extraction, and site redesign. Triggers on commands such as 'hallmark audit', 'hallmark redesign', 'hallmark study', or queries about whether a page looks AI-generated, generic, or needs visual upgrading.
---

# Hallmark: Anti-AI-Slop Quality Control

Use Hallmark to audit, redesign, or extract design DNA from existing layout structures and templates.

## 1. Verbs and Invocations

### `hallmark audit <target>`
- Scan the target HTML/CSS files against the list of 65+ visual AI-slop tells.
- Score the page on 6 design axes (Philosophy, Hierarchy, Execution, Specificity, Restraint, Variety) from 1 to 5.
- Output a ranked punch list of changes required to make the site look premium and unique. Do not modify the files directly during the audit command.

### `hallmark redesign <target>`
- Rebuild the visual layout and style definitions while preserving the underlying data, routes, file dependencies, and search engine optimization parameters.
- Reorganize section spacing, header fonts, component visual layouts, and color tokens.
- Keep modifications clean and localized to separate component style blocks or templates.

### `hallmark study <screenshot | URL>`
- Parse the live URL or read the reference image.
- Extract the "Design DNA": typography stack, color palettes, spacing rhythm, and layout patterns.
- Produce a markdown diagnosis (`design.md`) outlining how the user's project can adapt this DNA for its own content.

## 2. Integrity and Pre-emit Critique
- Before finalizing any UI work, perform a critique against these principles:
  - **Philosophy**: Does this layout make sense for the subject matter?
  - **Hierarchy**: Is there a single, clear dominant visual element?
  - **Restraint**: Have we removed excessive borders, multiple font variations, and neon gradients?
  - **Variety**: Does this page layout avoid repeating the exact hero -> features -> CTA template rhythm of previous sections?
- Print the critique scores at the top of modified CSS or HTML files:
  `/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */`
