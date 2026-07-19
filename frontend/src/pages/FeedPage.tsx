import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import SummaryCard, { StoryPreview } from "../components/SummaryCard";
import LanguageToggle from "../components/LanguageToggle";
import SearchBar from "../components/SearchBar";

const CATEGORIES = [
  { value: "all",           label: "All" },
  { value: "general",       label: "General" },
  { value: "technology",    label: "Tech" },
  { value: "finance",       label: "Finance" },
  { value: "sports",        label: "Sports" },
  { value: "entertainment", label: "Entertainment" },
  { value: "politics",      label: "Politics" },
];

export default function FeedPage() {
  const [stories, setStories]   = useState<StoryPreview[]>([]);
  const [lang, setLang]         = useState("en");
  const [category, setCategory] = useState("all");
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const [searchMode, setSearchMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const fetchFeed = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSearchMode(false);
    setSearchQuery("");
    try {
      const params: Record<string, string> = { lang };
      if (category !== "all") params.category = category;
      const res = await client.get("/feed", { params });
      setStories(res.data.stories);
    } catch {
      setError("Couldn't load the feed. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [lang, category]);

  useEffect(() => { fetchFeed(); }, [fetchFeed]);

  async function handleSearch(query: string) {
    if (!query) { fetchFeed(); return; }
    setLoading(true);
    setError(null);
    setSearchMode(true);
    setSearchQuery(query);
    try {
      const res = await client.get("/search", { params: { q: query } });
      const mapped: StoryPreview[] = res.data.results.map((r: Record<string, unknown>) => ({
        id:           r.id as number,
        title:        (r.canonical_title as string) ?? (r.title as string) ?? "",
        category:     (r.category as string) ?? "",
        sentiment:    (r.sentiment as string) ?? "Neutral",
        summary:      "",
        language:     "en",
        source_count: 0,
        created_at:   new Date().toISOString(),
      }));
      setStories(mapped);
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("briefit_token");
    navigate("/login");
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">

      {/* ── Header ── */}
      <header className="flex items-center justify-between mb-7">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-ocean shadow-md shadow-ocean/30 flex items-center justify-center">
            <span className="text-white font-black text-lg">B</span>
          </div>
          <div>
            <h1 className="text-2xl font-black text-ocean tracking-tight leading-none">BriefIt</h1>
            <p className="text-[11px] text-teal font-medium">Your news, distilled</p>
          </div>
        </div>
        <button
          id="logout-btn"
          onClick={handleLogout}
          className="text-sm text-teal hover:text-ocean font-medium transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-teallt/20"
        >
          <span>↪</span> Log out
        </button>
      </header>

      {/* ── Controls ── */}
      <div className="bg-white/60 backdrop-blur-sm border border-teallt/50 rounded-2xl px-4 py-3 mb-6 flex flex-wrap items-center gap-3 shadow-sm">
        <LanguageToggle value={lang} onChange={setLang} />

        {/* Category pills */}
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map((c) => (
            <button
              key={c.value}
              id={`cat-${c.value}`}
              onClick={() => setCategory(c.value)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                category === c.value
                  ? "bg-ocean text-white shadow-sm"
                  : "bg-ivory border border-teal/30 text-ocean hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="flex-1 min-w-[200px]">
          <SearchBar onSearch={handleSearch} />
        </div>
      </div>

      {/* ── Search mode banner ── */}
      {searchMode && !loading && (
        <div className="flex items-center justify-between mb-5 px-4 py-2.5 bg-ocean/5 border border-ocean/20 rounded-xl">
          <p className="text-sm text-ocean">
            Results for <span className="font-bold">"{searchQuery}"</span>
            <span className="text-teal ml-1">({stories.length} found)</span>
          </p>
          <button
            onClick={fetchFeed}
            className="text-xs font-semibold text-ocean bg-ivory border border-ocean/20 px-3 py-1 rounded-lg hover:bg-teallt/20 transition"
          >
            ← Back to feed
          </button>
        </div>
      )}

      {/* ── Loading skeletons ── */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-card border border-teal/20 rounded-2xl p-5 animate-pulse">
              <div className="flex justify-between mb-3">
                <div className="h-3 w-20 bg-teal/30 rounded-full" />
                <div className="h-3 w-16 bg-teal/20 rounded-full" />
              </div>
              <div className="h-4 bg-ocean/20 rounded-lg mb-2" />
              <div className="h-4 bg-ocean/15 rounded-lg w-4/5 mb-4" />
              <div className="space-y-1.5">
                <div className="h-3 bg-teal/20 rounded" />
                <div className="h-3 bg-teal/15 rounded w-5/6" />
                <div className="h-3 bg-teal/10 rounded w-3/4" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Error ── */}
      {!loading && error && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-2xl px-5 py-4">
          <span className="text-2xl">⚠️</span>
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* ── Empty state ── */}
      {!loading && !error && stories.length === 0 && (
        <div className="text-center py-24 flex flex-col items-center gap-3">
          <div className="w-16 h-16 rounded-2xl bg-teallt/30 flex items-center justify-center text-3xl">📭</div>
          <p className="text-ocean font-semibold text-lg">No stories found</p>
          <p className="text-teal text-sm">Try a different category or search term.</p>
        </div>
      )}

      {/* ── Story grid ── */}
      {!loading && !error && stories.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs text-teal font-medium uppercase tracking-widest">
              {searchMode ? "Search results" : "Latest stories"}
            </p>
            <span className="text-xs text-teal/70 bg-teallt/20 px-2 py-0.5 rounded-full">
              {stories.length} stories
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stories.map((story) => (
              <SummaryCard key={story.id} story={story} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
