# Frontend Startup & Stylesheet Loading Audit

This document maps out how the global stylesheet and any initial theme-related bootstrap logic are loaded at build/runtime. Use it as a reference when adding new theme initialization without altering existing behavior.

---

## 1. Vite Configuration

**File:** `vite.config.ts`

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

- No custom CSS handling options are defined.
- Vite uses ES module imports to bundle CSS files by default.
- PostCSS, CSS HMR, and CSS code splitting follow Vite defaults.

---

## 2. React Application Entrypoint

**File:** `src/main.tsx`

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- No theme-related code runs here currently.
- This is an ideal spot to inject global theme providers or initialization before `<App />`.

---

## 3. Root Application Component

**File:** `src/App.tsx`

```tsx
import React from "react"
import LandingPage from "./components/LandingPage"

export default function App() {
  return <LandingPage />
}
```

- `<App />` simply renders the landing page; no theme logic.
- Wrapping `<LandingPage />` with a theme context/provider here is another potential insertion point.

---

## 4. Global Stylesheet Import

**File:** `src/components/LandingPage.tsx`

```tsx
import React, { useState, useEffect, useCallback, useRef } from "react"
import "../styles/global.css"
```

- The global stylesheet (`global.css`) is imported at the top of `LandingPage`.
- As an ES module import, global CSS is evaluated and injected into the document head at bundle startup before React mounting.
- No other CSS imports exist before this point.

---

## 5. Global Stylesheet Location

**File:** `src/styles/global.css`

- Contains the dark-theme `:root` tokens, base resets, layout, and component-scoped styles.
- Paired with an existing audit in `global-theme-audit.md` for color token reference.

---

## 6. Stylesheet Load Order Summary

1. Vite processes `main.tsx` → `App.tsx` → `LandingPage.tsx`.
2. Import of `../styles/global.css` in `LandingPage.tsx` triggers CSS injection at bundle initialization.
3. React mounts `<App />` and renders components.

> **Note:** order of execution ensures global.css is in place before any UI paint.

---

## 7. Theme Bootstrapping & Future Hooks

- To enable runtime theme swapping or initialization, add code:
  - In `src/main.tsx` before rendering `<App />`, e.g.:
    ```ts
    // Read persisted theme preference from localStorage or media query
    // Initialize CSS variables or add a `<link>` to a dynamic CSS chunk
    ```
  - Or wrap `<App />` in a `<ThemeProvider>` in `App.tsx`.
- No existing bootstrapping logic; both entrypoints are available for future insertion without altering current behavior.

---

## 8. Next Steps

- Define a lightweight theme context/provider to toggle `:root` variables or switch a `<body>` class.
- Ensure any new imports (e.g. `light-theme.css`) use ES module imports at bootstrap time.
- Reference this startup map when integrating dynamic theme loading.
