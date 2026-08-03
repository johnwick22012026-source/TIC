# Theme Surface Mapping

This document maps each major top-level layout component to the CSS classes and global stylesheet rules that define its theme-dependent surface (background, border, text color) and elevation (box-shadow) tokens.

---

## Global Stylesheet (`:root` and base)

- **Color scheme and variables** (src/styles/global.css, `:root`)
  - `color-scheme: light` (the token set still reflects a light-leaning palette even though the rendered page currently layers darker gradients on top)
  - Light-mode CSS custom properties for surfaces and elevation (src/styles/global.css, `:root`):
    - **Core background & text:**
      - `--bg-color`, `--text-color`
    - **Shared surface tokens:** use these for consistent card/panel styling:
      - `--surface-card-color` (base surface background for cards and panels)
      - `--surface-border-color` (shared border color)
      - `--surface-shadow-faint` (subtle elevation for inline cards)
      - `--surface-shadow-soft` (soft elevation for status and scoreboard panels)
      - `--surface-shadow-mid` (mid elevation for board panels)
      - `--surface-shadow-deep` (deep elevation for the game shell)
    - **Alias tokens for backward compatibility:** (prefer surface-* tokens moving forward)
      - `--panel-color` = `var(--surface-card-color)`
      - `--card-color` = `var(--surface-card-color)`
      - `--border-color` = `var(--surface-border-color)`
    - **Additional palette variables:**
      - `--accent-color`, `--accent-shadow-color`, `--muted-color`
      - `--board-shell-color`, `--board-cell-color`, `--board-cell-border`
      - `--x-mark-color`, `--o-mark-color`, `--highlight-color`, `--highlight-color-transparent`
- **Global page background** (src/styles/global.css, `html, body`)
  - `background: var(--bg-color)`
  - `color: var(--text-color)`

---

## LandingPage wrappers (src/components/LandingPage.tsx)

- **`.page`** wrapper (src/styles/global.css)
  - Full-viewport flex container with centered content and padding
  - `background: radial-gradient(circle at top, rgba(79, 70, 229, 0.12), transparent 50%)`
- **`.game-shell`** panel (src/styles/global.css)
  - `background: var(--panel-color)`
  - `border: 1px solid var(--border-color)`
  - `border-radius`, `padding`, `box-shadow`

---

## Board component surface (src/components/Board.tsx)

- **`.board-panel`** section (src/styles/global.css)
  - `background: var(--panel-color)`
  - Panel border, border-radius, box-shadow, overflow styling
- **`.board-grid`** wrapper (src/styles/global.css)
  - `background: var(--board-shell-color)` with border and inset box-shadow
- **`.board-cell`**, **`.board-cell--winning`** (src/styles/global.css)
  - Cell background, border, hover/active/focus states, winning highlight gradient
- **`.board-symbol--x`**, **`.board-symbol--o`** (src/styles/global.css)
  - Text color and glow shadow for X and O marks

---

## Status area container (src/components/LandingPage.tsx)

- **`.status-area`** (src/styles/global.css)
  - `background: var(--card-color)`
  - `border: 1px solid var(--border-color)`
  - Padding and flex layout for status text and controls

---

## Scoreboard component surface (src/components/Scoreboard.tsx)

- **`.scoreboard-panel`** (src/styles/global.css)
  - Panel background, border, and border-radius (see matching rules in global.css)
- **`.score-grid`**, **`.score-card`** (src/styles/global.css)
  - Grid and card styling for individual score entries

---

*No structural or behavioral changes were introduced by the light-theme CSS updates. Refer to `src/styles/global-theme-audit.md` for the detailed audit results and verification notes. Follow-up Issue: #456 – Extract spacing tokens for gap properties (see replication notes in the global theme audit).*