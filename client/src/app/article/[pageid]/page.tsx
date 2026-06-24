import Link from "next/link";
import { notFound } from "next/navigation";
import db from "@/lib/db";

interface POIRecord {
  group_id: number;
  title: string;
}

interface WikiParseResponse {
  parse?: {
    title: string;
    displaytitle: string;
    text: {
      "*": string;
    };
  };
  error?: {
    code: string;
    info: string;
  };
}

async function fetchWikiArticle(pageid: string): Promise<WikiParseResponse | null> {
  const url = `https://en.wikipedia.org/w/api.php?action=parse&pageid=${pageid}&prop=text|displaytitle&format=json&origin=*`;
  try {
    const res = await fetch(url, { next: { revalidate: 3600 } });
    if (!res.ok) return null;
    return await res.json() as WikiParseResponse;
  } catch (error) {
    console.error("Failed fetching Wikipedia article:", error);
    return null;
  }
}

export default async function ArticlePage({ params }: { params: Promise<{ pageid: string }> }) {
  const { pageid } = await params;

  // 1. Query the database to find the POI and get the group_id (city ID) for back navigation
  const poiInfo = db
    .prepare("SELECT group_id, title FROM points_of_interest WHERE pageid = ?")
    .get(pageid) as POIRecord | undefined;

  // 2. Fetch parsed HTML from Wikipedia API
  const wikiData = await fetchWikiArticle(pageid);

  if (!wikiData || wikiData.error || !wikiData.parse) {
    notFound();
  }

  const articleTitle = wikiData.parse.title;
  const articleHtml = wikiData.parse.text["*"];

  const backLink = poiInfo ? `/city/${poiInfo.group_id}` : "/";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <nav className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={backLink} className="inline-flex items-center gap-1.5 text-slate-400 hover:text-indigo-400 text-sm font-semibold transition-colors">
            &larr; Back to City
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <span className="text-sm font-semibold text-slate-300 truncate max-w-[200px] sm:max-w-none">
            {poiInfo?.title || articleTitle}
          </span>
        </div>
        <div className="text-[10px] text-slate-500 font-mono hidden sm:block">
          Wikipedia Page ID: {pageid}
        </div>
      </nav>

      {/* Main Container */}
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-12">
        {/* Header Block */}
        <header className="mb-10 pb-8 border-b border-slate-900 flex flex-col gap-4">
          <div className="inline-flex items-center gap-2 self-start bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[10px] uppercase font-bold tracking-widest px-3 py-1 rounded-full">
            Wikipedia Encyclopedia
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-50">
            {articleTitle}
          </h1>
        </header>

        {/* Wiki Render Area */}
        <article 
          className="wiki-content" 
          dangerouslySetInnerHTML={{ __html: articleHtml }} 
        />
      </main>

      {/* Footer */}
      <footer className="w-full max-w-4xl mx-auto px-6 border-t border-slate-900/60 py-8 text-center text-xs text-slate-500">
        Content fetched live from Wikipedia. Licensed under CC BY-SA 4.0.
      </footer>
    </div>
  );
}
