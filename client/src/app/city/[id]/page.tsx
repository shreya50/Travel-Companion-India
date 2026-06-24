import Link from "next/link";
import { notFound } from "next/navigation";
import db from "@/lib/db";
import MapWrapper from "@/components/MapWrapper";

interface CityGroup {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

interface POI {
  pageid: number;
  title: string;
  latitude: number;
  longitude: number;
  summary: string;
  image_url: string;
}


export default async function CityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  
  // 1. Fetch group
  const group = db.prepare("SELECT * FROM groups WHERE id = ?").get(id) as CityGroup | undefined;
  if (!group) {
    notFound();
  }

  // 2. Fetch POIs
  const pois = db.prepare("SELECT * FROM points_of_interest WHERE group_id = ?").all(id) as POI[];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <nav className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/" className="inline-flex items-center gap-1.5 text-slate-400 hover:text-indigo-400 text-sm font-semibold transition-colors">
            &larr; Back to Cities
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <h1 className="text-xl font-bold tracking-tight text-slate-50 flex items-center gap-2">
            📍 {group.name}
          </h1>
          <span className="text-xs font-mono text-slate-500 hidden sm:inline">
            ({group.latitude.toFixed(4)}, {group.longitude.toFixed(4)})
          </span>
        </div>
        <div className="text-xs font-semibold px-3 py-1 bg-indigo-500/10 border border-indigo-500/25 text-indigo-400 rounded-full">
          {pois.length} Locations Saved
        </div>
      </nav>

      {/* Workspace Panel */}
      <div className="flex-1 flex flex-col md:flex-row min-h-[calc(100vh-69px)] overflow-hidden">
        {/* Left Sidebar (Points of Interest) */}
        <aside className="w-full md:w-[400px] border-r border-slate-900 flex flex-col bg-slate-900/20 max-h-[50vh] md:max-h-[calc(100vh-69px)]">
          <div className="p-4 border-b border-slate-900 bg-slate-950/20">
            <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
              Points of Interest
            </h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar">
            {pois.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-505">
                <span className="text-2xl mb-2">🏝️</span>
                <p className="text-sm font-medium">No places stored yet</p>
                <p className="text-xs text-slate-600 mt-1 max-w-[200px]">
                  Use the worker script or provision.py to query and seed articles for {group.name}!
                </p>
              </div>
            ) : (
              pois.map((poi) => (
                <div key={poi.pageid} className="group relative flex gap-4 p-3 bg-slate-900/40 hover:bg-slate-900/80 border border-slate-800/60 hover:border-indigo-500/25 rounded-xl transition-all duration-200">
                  {poi.image_url && (
                    <img 
                      src={poi.image_url} 
                      alt={poi.title} 
                      className="w-16 h-16 object-cover rounded-lg bg-slate-800 border border-slate-700/50 flex-shrink-0"
                    />
                  )}
                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-slate-100 text-sm group-hover:text-indigo-400 transition-colors duration-150 truncate mb-1">
                        {poi.title}
                      </h3>
                      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                        {poi.summary || "No summary available."}
                      </p>
                    </div>
                    <div className="mt-2 text-right">
                      <Link 
                        href={`/article/${poi.pageid}`}
                        className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-500 hover:text-indigo-400 transition-colors"
                      >
                        Read Article &rarr;
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Right Map Panel */}
        <main className="flex-1 relative h-[50vh] md:h-auto p-4 md:p-6 bg-slate-950">
          <MapWrapper center={[group.latitude, group.longitude]} pois={pois} />
        </main>
      </div>
    </div>
  );
}
