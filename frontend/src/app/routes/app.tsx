import { Link } from "react-router";
import { Button } from "@/components/ui/button";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 p-4">
      <div className="group relative mb-8">
        {/* Glow effect */}
        <div className="absolute -inset-4 animate-pulse rounded-full bg-white/10 blur-xl transition-all duration-1000 group-hover:bg-white/20" />

        {/* Logo container with animations */}
        <div className="animate-float relative">
          <img
            src="/ronins.png"
            alt="Ronins Logo"
            className="h-24 w-24 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all duration-500 group-hover:scale-110 group-hover:drop-shadow-[0_0_25px_rgba(255,255,255,0.5)]"
          />
        </div>
      </div>

      <h1 className="mb-4 text-4xl font-bold text-white">Ronins React</h1>
      <p className="mb-8 text-center text-neutral-400">
        Production-ready React starter with TypeScript, Tailwind, and modern
        tooling
      </p>
      <Button asChild>
        <Link to="/stack">Tech Stack</Link>
      </Button>

      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) rotate(0deg);
          }
          25% {
            transform: translateY(-8px) rotate(1deg);
          }
          75% {
            transform: translateY(-4px) rotate(-1deg);
          }
        }
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
