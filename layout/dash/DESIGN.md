# Design System Document: Editorial Intelligence

## 1. Overview & Creative North Star: "The Digital Atelier"
This design system is not a template; it is a high-end educational environment. The Creative North Star is **"The Digital Atelier"**—a space that feels like a curated, architectural studio rather than a standard learning management system. 

To achieve this, we move away from traditional "boxed" layouts. We embrace **Intentional Asymmetry** and **Tonal Depth**. By breaking the rigid 12-column grid with overlapping elements and shifting background densities, we create a signature experience that feels bespoke, authoritative, and premium. The goal is to make the student feel they are entering a private masterclass, not just a website.

---

## 2. Colors: Depth Through Density
We utilize a monochromatic base punctuated by "Illuminant Accents." The palette is designed to recede and advance based on importance, using Material-style surface tiers to define hierarchy without visual clutter.

### The "No-Line" Rule
**Standard 1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined solely through background shifts. For example, a `surface-container-low` section should sit directly against a `surface` background. This creates a "soft edge" that feels more sophisticated than a hard stroke.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—stacked sheets of obsidian glass.
- **Base Layer:** `surface` (#131313)
- **Primary Containers:** `surface-container-low` (#1C1B1B)
- **Interactive/Nested Cards:** `surface-container-high` (#2A2A2A)
- **Floating Modals:** `surface-container-highest` (#353534)

### The "Glass & Gradient" Rule
To add "soul" to the interface, use Glassmorphism for floating navigation and overlays. Use `surface` colors at 70% opacity with a `24px` backdrop-blur. 
- **Signature CTA Texture:** Use a subtle linear gradient (45°) from `primary` (#CEBDFF) to `primary-container` (#A78BFA). This prevents the "flat-and-dead" look of standard buttons.

---

## 3. Typography: The Geist Aesthetic
We use **Geist** (and its Inter-inspired scales) to convey precision and modernity. Typography is our primary tool for authority.

*   **Display (Large/Medium):** Used for hero headers. Tracking should be set to `-0.02em` to create a tight, editorial feel. 
*   **Headline (Small) & Title (Large):** Used for course titles and section headers. These are the anchors of the page.
*   **Body (Medium):** The workhorse for educational content. Set at `1rem` with a generous line-height (`1.6`) to ensure long-form readability.
*   **Labels:** Always uppercase with `0.05em` letter spacing to denote "meta-information" like categories or durations.

**Hierarchy Strategy:** Contrast is king. Pair a `display-md` headline with a `label-md` category tag to create a high-fashion, high-intellect visual tension.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too "web 2.0." We use **Tonal Layering** to convey lift.

*   **The Layering Principle:** Depth is achieved by "stacking" tiers. Place a `surface-container-lowest` card on a `surface-container-low` background to create a "recessed" look. Place a `surface-bright` element on a `surface` background to create "lift."
*   **Ambient Shadows:** If a floating effect is required (e.g., a dropdown), use a "Tinted Shadow": `0px 20px 40px rgba(0, 0, 0, 0.4)`. Never use pure black shadows; they feel muddy.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility, use the `outline-variant` token at **15% opacity**. It should be felt, not seen.
*   **Backdrop Blur:** Any element floating over content (headers/modals) must use `backdrop-filter: blur(12px)`.

---

## 5. Components: Architectural Primitives

### Buttons: The Interaction Signature
*   **Primary:** Gradient of `primary` to `primary-container`. `radius-md` (0.375rem). No border.
*   **Secondary:** Ghost style. `outline` token at 20% opacity. Text color `secondary` (#5DE6FF).
*   **Tertiary:** Text only, `on-surface-variant`. On hover, shift to `primary` with a 2px underline.

### Cards & Lists: No Dividers
*   **Forbid the use of divider lines.** Use `1.5rem` (6) or `2rem` (8) of vertical white space to separate items.
*   **Interactive Cards:** Use `surface-container-high`. On hover, transition the background to `surface-container-highest` and apply a `primary` ghost-border at 10% opacity.

### Input Fields: Minimalist Precision
*   **Default:** `surface-container-low` background. No border.
*   **Focus State:** A 1px bottom-border of `secondary` (#5DE6FF). This draws focus without boxing the user in.

### Educational-Specific Components
*   **Progress Indicators:** Use a thin (2px) line using the `secondary` token. Avoid chunky bars.
*   **Course Badges:** Small capsules with `primary` text on a `primary-container` background (at 20% opacity).

---

## 6. Do's and Don'ts

### Do:
*   **Do** use asymmetrical layouts where the text block is offset from the imagery.
*   **Do** use the `secondary` color (#22D3EE) for technical highlights, code snippets, or "aha!" moments.
*   **Do** prioritize "negative space." If it feels empty, add more space, not more elements.

### Don't:
*   **Don't** use 100% white (#FFFFFF). Use `on-background` (#E5E2E1) for a softer, premium reading experience.
*   **Don't** use "Drop Shadows" on cards. Use background-color shifts to indicate depth.
*   **Don't** use rounded corners larger than `xl` (0.75rem) unless it's a pill-shape button. We want the system to feel architectural, not "bubbly."
*   **Don't** ever use a solid 1px divider between list items. The spacing scale is your divider.