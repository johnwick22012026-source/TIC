# Global Theme CSS Audit

**File:** `src/styles/global.css`

This document maps the current global styling rules in the primary stylesheet and highlights the reusable tokens that will form the foundation for the upcoming dark-mode and any future light-mode work. While the title used to reference a "light theme," the extracted snippets reflect the present dark-leaning default, so the commentary below reflects that reality while still calling out the tokens to preserve for theme expansions.

---

## 1. :root – Global Color Tokens & Base Settings

These CSS custom properties serve as the core color palette and base settings for the theme currently applied in `global.css`. They are crafted with darker surfaces in mind but should be treated as reusable tokens for any future theme variants.

```css
:root {
  color-scheme: light;
  font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
  --bg-color: #f8fafc;
  --panel-color: #ffffff;
  --card-color: #e2e8f0;
  --border-color: #cbd5e1;
  --accent-color: #3b82f6;
  --muted-color: #64748b;
  --board-shell-color: #e5e7eb;
  --board-cell-color: rgba(226, 232, 240, 0.85);
  --board-cell-border: rgba(100, 116, 139, 0.35);
  --x-mark-color: #ef4444;
  --o-mark-color: #14b8a6;
}
```

**Tokens to preserve for dark-theme foundation:** all `--*` variables above.

---

## 2. Base Selectors – Reset & Global Typography

These selectors set up fundamental box-sizing, reset margins, and define the global background and foreground for the UI. Even though the tokens lean light, the actual body background and text color used here reflect the darker visual system currently rendered by `global.css`.

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

These classes establish the overall page layout and container surfaces. While the colors referenced come from the darker layers of the current stylesheet, they remain adaptable through the tokens listed above when a new light or inverted theme is introduced.

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

Global typography styles for headings, subtitles, and state labels. They rely on the muted token for secondary text to stay legible against the existing dark surfaces.

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

Specific styles for the board container, grid, cells, and symbols. These remain component-scoped to preserve their structure while referencing the shared theme tokens when colors need adjusting in new variants.

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

- **Global tokens** (`:root`) are intentionally kept as the foundation for any future dark/light splits.
- **Base selectors** and **app-level surfaces** currently draw from darker gradients and transparencies, so update them when a light mode is introduced while keeping structural rules intact.
- **Typography defaults** rely on `--muted-color` for secondary text; ensure this token gains sufficient contrast for future theme contexts.
- **Component-scoped** selectors intentionally omit direct color values here; they should reference the tokens when implementing new themes.
- Use this audit as the reference point when creating `dark-theme.css` or updating the shared tokens for any additional theme modes.