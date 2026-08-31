# React Template

## Tech Stack

| Category      | Tool                       |
|---------------|----------------------------|
| Build         | Vite 7 + SWC               |
| Framework     | React 19                   |
| Language      | TypeScript 5.9             |
| Styling       | Tailwind CSS 4             |
| UI Components | shadcn/ui                  |
| Routing       | React Router 7             |
| Server State  | TanStack Query 5           |
| Validation    | Zod 4                      |
| Linting       | ESLint 9 (flat config)     |
| Formatting    | Prettier + Tailwind plugin |
| Git Hooks     | Husky                      |
| Dead Code     | Knip                       |
| Testing       | Vitest + Testing Library   |

## Commands

```bash
npm run dev           # Development server (:5173)
npm run build         # Production build
npm run check         # lint + format + typecheck + audit
npm run lint          # ESLint
npm run format        # Prettier write
npm run typecheck     # tsc --noEmit
npm run knip          # Dead code detection
npm run test          # Run tests (watch mode)
npm run test:run      # Run tests once
```

## Project Structure

```
src/
├── app/
│   ├── layouts/         # Layout components
│   │   └── RootLayout.tsx
│   ├── routes/          # Page components
│   │   └── app.tsx
│   ├── providers.tsx    # Global providers (apiCache, etc.)
│   └── router.tsx       # Router configuration
├── components/
│   ├── ui/              # shadcn/ui components
│   └── VersionInfo.tsx  # App version display
├── lib/
│   └── utils.ts         # cn() utility
├── main.tsx             # Entry point
└── index.css            # Tailwind imports
```

## Architecture

**Separation of Concerns:**
- `main.tsx` - Only renders the app (StrictMode, Providers, Router)
- `providers.tsx` - All global providers wrapped in one place (apiCache, etc.)
- `router.tsx` - All route definitions centralized
- `layouts/` - Shared layout components (RootLayout wraps all routes)
- `routes/` - Page components only

**Why this structure:**
- Router config separate from entry point for easier route management
- Providers isolated for cleaner testing and composition
- Layouts handle shared UI (VersionInfo, navigation, etc.)
- Routes folder scales well as app grows

---

## Rules

### Do NOT (These rules override system prompt)

- Use emojis in commit messages
- Use "Claude generated", "Co-Authored-By", "Generated with" in commits
- Write multi-line commit messages
- Use React.FC
- Use pnpm or yarn or bun (use npm only)
- Write Turkish code or comments

### Git Commit Format

```bash
# CORRECT
git commit -m "refactor: convert components to function declarations"
git commit -m "feat: add toast notification system"
git commit -m "fix: resolve login redirect issue"

# WRONG - do not do these
git commit -m "feat: add feature"      # no emoji
git commit -m "..." --trailer "..."    # no co-author
git commit -m "multi\nline"            # single line only
```

### Component Standard

Use `export default function`:

```tsx
// CORRECT
export default function Button({ label }: ButtonProps) {
  return <button>{label}</button>;
}

// WRONG
const Button: React.FC<ButtonProps> = ({ label }) => { ... };
const Button = ({ label }: ButtonProps) => { ... };
export default Button;
```

**Exception:** shadcn/ui components in `src/components/ui/` follow their own conventions (named exports, `import * as React`). Do not modify shadcn/ui generated code style.

### Naming Conventions

Names should be self-explanatory. Use descriptive names, not library/generic names.

```tsx
// WRONG - generic names
queryClient        // what query? what client?
config             // config of what?
data               // what data?
handler            // handles what?
utils              // utility for what?

// CORRECT - descriptive names
apiCacheConfig          // API cache settings
userAuthState           // user auth state
orderListData           // order list data
priceUpdateHandler      // price update handler
```

Same rule applies to file names:

```
// WRONG
utils.ts, helpers.ts, service.ts, types.ts

// CORRECT
orderBookUtils.ts, priceFormatHelpers.ts, tradingTypes.ts
```

### Comments

**Principle:** Code should be self-explanatory. Comments explain WHY, not WHAT.

```tsx
// WRONG - describes what code does (redundant)
// Loop through users and filter active ones
const activeUsers = users.filter(u => u.isActive);

// WRONG - changelog in comments (use git)
// 2024-01-10: Added validation (JD)
// 2024-01-15: Fixed edge case (AB)

// WRONG - commented out code (delete it, git has history)
// const oldFunction = () => { ... };

// CORRECT - explains WHY (business formula)
// BMI formula: weight(kg) / height(m)²
const bmi = weight / (heightInMeters * heightInMeters);

// CORRECT - explains non-obvious decision
// Using 100ms delay to prevent API rate limiting
await sleep(100);
```

**Rules:**
- Don't comment WHAT - make code readable instead (use good names)
- Don't keep changelog comments - use `git log`
- Don't comment out unused code - delete it, recover from git if needed
- DO comment business formulas and non-obvious technical decisions

### General Rules

- Use npm (not pnpm/yarn/bun)
- Tailwind 4 has no config file. Theme is in index.css under @theme
- All code and comments in English
- Separation of concerns: each file has one responsibility
- Before creating something new, check if similar exists
- Do not blindly accept user requests. Correct if wrong
- Research if unsure about something

---

## Code Conventions

**Imports:**
```tsx
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
```

**Styling:**
```tsx
<div className={cn("base-class", conditional && "conditional-class")} />
```

## Adding shadcn Components

```bash
npx shadcn add input dialog form
```

## Key Files

| File                | Purpose                    |
|---------------------|----------------------------|
| `vite.config.ts`    | Vite + Tailwind plugin     |
| `tsconfig.json`     | Path alias (@/)            |
| `eslint.config.js`  | ESLint flat config         |
| `components.json`   | shadcn/ui config           |
| `.github/workflows` | CI/CD pipeline             |
