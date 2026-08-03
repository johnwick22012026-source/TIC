# Global Dark-Theme CSS Audit

**File:** `src/styles/global.css`

This document maps the global dark-theme styling rules in the primary stylesheet and highlights the reusable tokens that will form the foundation for the upcoming light-theme work.

---

## 1. :root – Global Color Tokens & Base Settings

These CSS custom properties serve as the core color palette and base settings for both dark and future light themes.

```css
:root {
  color-scheme: dark;
  font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
  --bg-color: #060914;
  --panel-color: #0f172a;
  --card-color: #111b2b;
  --border-color: #1e293b;
  --accent-color: #38bdf8;
  --muted-color: #94a3b8;
  --board-shell-color: #0e1b3a;
  --board-cell-color: rgba(15, 23, 42, 0.85);
  --board-cell-border: rgba(148, 163, 184, 0.35);
  --x-mark-color: #f87171;
  --o-mark-color: #5eead4;
}
```

**Tokens to preserve for light-theme foundation:** all `--*` variables above.

---

## 2. Base Selectors – Reset & Global Typography

These selectors set up fundamental box-sizing, reset margins, global background, and text defaults.

```css
* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  min-height: 100vh;
  background: radial-gradient(circle at top, #14213d 0%, #060914 45%);
  color: #f8fafc;
  font-size: 16px;
  line-height: 1.6;
}

body {
  font-weight: 400;
}
```

---

## 3. App-Level Surface Rules

These classes establish the overall page layout and container surfaces.

```css
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.game-shell {
  width: min(1100px, 100%);
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 1.5rem;
  padding: clamp(2rem, 3vw, 3rem);
  display: flex;
  flex-direction: column;
  gap: 2rem;
  box-shadow: 0 25px 55px rgba(2, 6, 23, 0.85);
}

.status-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  background: var(--card-color);
  padding: 1rem 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  font-size: 1rem;
}
```

---

## 4. Typography Defaults

Global typography styles for headings, subtitles, and state labels.

```css
.title-area {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.eyebrow {
  letter-spacing: 0.35em;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--muted-color);
  margin: 0;
}

.title-area h1 {
  margin: 0;
  font-size: clamp(2.25rem, 4vw, 3.2rem);
}

.subtitle {
  margin: 0;
  color: var(--muted-color);
  font-size: 0.95rem;
  line-height: 1.5;
}

.board-panel h2 {
  margin: 0;
  font-size: 1.35rem;
  letter-spacing: 0.02em;
}
```

---

## 5. Component-Scoped Styles (Board & Cells)

Specific styles for the board container, grid, cells, and symbols. These will remain component-scoped and adapt to the theme tokens.

```css
.board-panel { /* panel container */ }
.board-panel--disabled { /* disabled state */ }
.board-panel--won .board-cell:not(.board-cell--winning) { /* dim losing cells */ }
.board-panel::after { /* overlay gradient */ }
.board-description { /* panel description text */ }
.board-grid { /* grid layout & bg */ }
.board-cell { /* individual cell default */ }
.board-cell--winning { /* winning cell highlight */ }
.board-cell:hover:not(:disabled) { /* hover state */ }
.board-cell:disabled { /* disabled cell */ }
.board-cell:focus-visible { /* focus ring */ }
.board-cell:active { /* active press */ }
.board-symbol { /* symbol base */ }
.board-symbol--x { /* X-mark color & glow */ }
.board-symbol--o { /* O-mark color & glow */ }
```

---

## Notes & Next Steps

- **Global tokens** (`:root`) should be reused and inverted/adapted for the light theme.
- **Base selectors** and **app-level surfaces** set structural and background contexts—update their color references to light counterparts.
- **Typography defaults** rely on `--muted-color` for secondary text; ensure legibility on light backgrounds.
- **Component-scoped** selectors remain intact but will reference the new theme tokens for coloring and shadows.
- This audit delineates global foundation rules vs. component styles. Use it as a reference when creating `light-theme.css` or updating `:root` for light mode.