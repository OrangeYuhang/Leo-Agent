// __APP_VERSION__ comes from vite.config.ts "define" section.
// Vite reads version from package.json at build time.

export default function VersionInfo() {
  return (
    <div className="fixed right-0 bottom-0 rounded-tl-md bg-neutral-800 px-2 py-0.5 text-xs text-neutral-400">
      v{__APP_VERSION__}
    </div>
  );
}
