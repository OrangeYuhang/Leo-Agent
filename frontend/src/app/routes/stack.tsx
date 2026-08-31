import { Link } from "react-router";
import { Button } from "@/components/ui/button";

const stack = [
  { category: "Build", tool: "Vite 7 + SWC" },
  { category: "Framework", tool: "React 19" },
  { category: "Language", tool: "TypeScript 5.9" },
  { category: "Styling", tool: "Tailwind CSS 4" },
  { category: "UI Components", tool: "shadcn/ui" },
  { category: "Routing", tool: "React Router 7" },
  { category: "Server State", tool: "TanStack Query 5" },
  { category: "Validation", tool: "Zod 4" },
  { category: "Linting", tool: "ESLint 9" },
  { category: "Formatting", tool: "Prettier" },
  { category: "Git Hooks", tool: "Husky" },
  { category: "Dead Code", tool: "Knip" },
];

export default function Stack() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 p-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex items-center gap-3">
          <img src="/ronins.png" alt="Ronins" className="h-8 w-8" />
          <h1 className="text-2xl font-bold text-white">Tech Stack</h1>
        </div>
        <ul className="mb-8 space-y-2">
          {stack.map((item) => (
            <li key={item.category} className="flex justify-between text-sm">
              <span className="text-neutral-500">{item.category}</span>
              <span className="text-white">{item.tool}</span>
            </li>
          ))}
        </ul>
        <div className="flex justify-center">
          <Button variant="outline" asChild>
            <Link to="/">Back</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
