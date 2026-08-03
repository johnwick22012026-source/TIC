# Theme Surface Mapping

This document maps each major top-level layout component to the CSS classes and global stylesheet rules that define its theme-dependent surface (background, border, text color).

---

## Global Stylesheet (`:root` and base)

- **Color scheme and variables** (src/styles/global.css, `:root`)
  - `color-scheme: dark`
  - Dark mode CSS custom properties:
    - `--bg-color`, `--panel-color`, `--card-color`, `--border-color`, `--accent-color`, `--muted-color`,
      `--board-shell-color`, `--board-cell-color`, `--board-cell-border`, `--x-mark-color`, `--o-mark-color`
- **Global page background** (src/styles/global.css, `html, body`)
  - `background: radial-gradient(circle at top, #14213d 0%, #060914 45%)`
  - `color: #f8fafc`

---

## LandingPage wrappers (src/components/LandingPage.tsx)

- **`.page`** wrapper (src/styles/global.css)
  - Full-viewport flex container with centered content and padding
- **`.game-shell`** panel (src/styles/global.css)
  - `background: rgba(15, 23, 42, 0.95)`
  - `border: 1px solid rgba(148, 163, 184, 0.25)`
  - `border-radius`, `padding`, `box-shadow`

---

## Board component surface (src/components/Board.tsx)

- **`.board-panel`** section (src/styles/global.css)
  - `background: linear-gradient(180deg, #1b2b47 0%, #0c1224 60%, #050812 100%)`
  - Panel border, border-radius, box-shadow, overflow styling
- **`.board-grid`** wrapper (src/styles/global.css)
  - Radial-gradient shell and inset border for the grid container
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

*No structural or behavioral changes have been made. This mapping will guide the upcoming light-theme pass without altering existing component layouts or logic.*
