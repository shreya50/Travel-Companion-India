import Link from "next/link";
import db from "@/lib/db";

interface CityGroup {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  poi_count: number;
}

export default function Home() {
  // Query the SQLite database for cities and POI counts
  const groups: CityGroup[] = db
    .prepare(`
      SELECT 
        g.id, 
        g.name, 
        g.latitude, 
        g.longitude,
        COUNT(p.id) as poi_count 
      FROM groups g
      LEFT JOIN points_of_interest p ON g.id = p.group_id
      GROUP BY g.id
    `)
    .all() as CityGroup[];

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100 flex flex-col items-center justify-between pb-12">
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-indigo-950/40 via-slate-950 to-slate-950 -z-10" />

      {/* Header / Hero Section */}
      <header className="w-full max-w-6xl mx-auto pt-24 px-6 text-center md:text-left flex flex-col gap-6 md:gap-8">
        <div className="flex flex-col gap-3">
          <div className="inline-flex items-center gap-2 self-center md:self-start bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-medium px-3.5 py-1.5 rounded-full backdrop-blur-sm">
            ✨ India Exploration Hub
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-50 via-slate-200 to-indigo-200">
            India Travel Companion
          </h1>
          <p className="max-w-2xl text-lg text-slate-400 leading-relaxed">
            Discover historical landmarks, monuments, and points of interest across India's most iconic cities. Powered by curated coordinates and live Wikipedia search.
          </p>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="w-full max-w-6xl mx-auto px-6 py-12 flex-1">
        <h2 className="text-xl font-bold tracking-wide text-slate-400 uppercase mb-8">
          Explore Cities ({groups.length})
        </h2>

        {groups.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 bg-slate-900/40 border border-slate-800 rounded-2xl text-center">
            <span className="text-4xl mb-4">📍</span>
            <h3 className="text-lg font-semibold text-slate-300">No Cities Discovered Yet</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-xs">
              Run the seeder or the agent script in the `worker/` directory to discover and add cities to the database!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group) => (
              <Link
                key={group.id}
                href={`/city/${group.id}`}
                className="group relative flex flex-col justify-between p-6 bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800/80 hover:border-indigo-500/30 rounded-2xl transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 cursor-pointer backdrop-blur-md"
              >
                {/* Hover glow */}
                <div className="absolute -inset-[1px] bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-300 -z-10 blur-sm" />

                <div>
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-2xl p-2.5 bg-slate-850 rounded-xl group-hover:scale-110 transition-transform duration-300">
                      🇮🇳
                    </span>
                    <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/25 text-indigo-400 rounded-full">
                      {group.poi_count} POIs
                    </span>
                  </div>

                  <h3 className="text-2xl font-bold text-slate-100 mb-1 group-hover:text-indigo-400 transition-colors duration-200">
                    {group.name}
                  </h3>

                  <p className="text-xs text-slate-500 font-mono">
                    Coords: {group.latitude.toFixed(4)}, {group.longitude.toFixed(4)}
                  </p>
                </div>

                <div className="mt-8 flex items-center justify-between text-sm font-medium text-slate-400 group-hover:text-indigo-300 transition-colors duration-200">
                  <span>Explore Landmarks</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                    stroke="currentColor"
                    className="w-4 h-4 transform group-hover:translate-x-1.5 transition-transform duration-200"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full max-w-6xl mx-auto px-6 border-t border-slate-900/60 pt-8 text-center text-xs text-slate-500">
        Travel Companion India — Scaffolding Monorepo App
      </footer>
    </div>
  );
}

