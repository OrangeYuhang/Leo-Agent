/**
 * Clean script - Removes demo content and resets to blank slate
 * Run with: bun clean / npm run clean / pnpm clean
 */

import { existsSync, rmSync, writeFileSync, readFileSync } from "node:fs";
import { createInterface } from "node:readline";

function detectPackageManager() {
  if (existsSync("bun.lock") || existsSync("bun.lockb")) return "bun";
  if (existsSync("pnpm-lock.yaml")) return "pnpm";
  if (existsSync("yarn.lock")) return "yarn";
  return "npm";
}

function getDevCommand(pm) {
  return pm === "npm" ? "npm run dev" : `${pm} dev`;
}

const FILES_TO_DELETE = [
  "src/app/routes/stack.tsx",
  "public/ronins.png",
  "public/favicon.png",
];

const COLORS = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  cyan: "\x1b[36m",
  dim: "\x1b[2m",
};

function log(message, color = "reset") {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

async function confirm(question) {
  const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      const a = answer.trim().toLowerCase();
      resolve(a === "y" || a === "yes");
    });
  });
}

function deleteFiles(files) {
  for (const file of files) {
    if (existsSync(file)) {
      rmSync(file);
      log(`  Deleted: ${file}`, "dim");
    }
  }
}

function createMinimalAppPage() {
  const content = `export default function App() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <h1 className="text-4xl font-bold">Hello World</h1>
    </main>
  );
}
`;
  writeFileSync("src/app/routes/app.tsx", content);
  log(`  Replaced: src/app/routes/app.tsx`, "dim");
}

function updateRouter() {
  const content = `import { createBrowserRouter } from "react-router";
import RootLayout from "./layouts/RootLayout";
import App from "./routes/app";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: <App />,
      },
    ],
  },
]);
`;
  writeFileSync("src/app/router.tsx", content);
  log(`  Updated: src/app/router.tsx`, "dim");
}

function updateIndexHtml() {
  let content = readFileSync("index.html", "utf-8");
  content = content.replace(/<title>.*<\/title>/, "<title>React App</title>");
  content = content.replace(
    /<link rel="icon"[^>]*>/,
    '<link rel="icon" href="/favicon.ico" />',
  );
  writeFileSync("index.html", content);
  log(`  Updated: index.html`, "dim");
}

async function main() {
  console.log();
  log("Ronins React - Clean Demo Content", "cyan");
  console.log();

  const existingFiles = FILES_TO_DELETE.filter(existsSync);

  if (existingFiles.length === 0) {
    log("No demo files found. Project is already clean!", "green");
    return;
  }

  log("Files to delete:", "yellow");
  for (const file of existingFiles) {
    log(`  - ${file}`, "dim");
  }
  console.log();

  log("Files to replace/update:", "yellow");
  log(`  - src/app/routes/app.tsx (minimal page)`, "dim");
  log(`  - src/app/router.tsx (remove stack route)`, "dim");
  log(`  - index.html (update title)`, "dim");
  console.log();

  const confirmed = await confirm(
    `${COLORS.yellow}Proceed with cleanup? (y/N): ${COLORS.reset}`,
  );

  if (!confirmed) {
    log("Cleanup cancelled.", "red");
    process.exit(0);
  }

  console.log();
  log("Cleaning...", "cyan");

  deleteFiles(existingFiles);
  createMinimalAppPage();
  updateRouter();
  updateIndexHtml();

  const pm = detectPackageManager();
  const devCmd = getDevCommand(pm);

  console.log();
  log("Done! Your project is now a blank slate.", "green");
  log(`Run '${devCmd}' to start development.`, "dim");
  console.log();
}

main().catch(console.error);
