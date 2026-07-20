import { useEffect, useState, useCallback, useRef } from "react";
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

const PAGE_SIZE = 20;
const POLL_MS   = 60_000;  // re-check for newly summarized stories every 60s

export default function FeedPage() {
  const [stories, setStories]     = useState<StoryPreview[]>([]);
  const [lang, setLang]           = useState("en");
  const [category, setCategory]   = useState("all");
  const [loading, setLoading]     = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [searchMode, setSearchMode]   = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [offset, setOffset]       = useState(0);
  const [hasMore, setHasMore]     = useState(false);
  const [total, setTotal]         = useState(0);
  const [newCount, setNewCount]   = useState(0);   // stories added since last full load
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const navigate = useNavigate();

  // ── Full feed load (replaces current list) ──────────────────────────────────
  const fetchFeed = useCallback(async (resetOffset = true) => {
    const nextOffset = resetOffset ? 0 : offset;
    if (resetOffset) {
      setLoading(true);
      setError(null);
      setSearchMode(false);
      setSearchQuery("");
      setNewCount(0);
    }
    try {
      const params: Record<string, string | number> = { lang, offset: nextOffset, limit: PAGE_SIZE };
      if (category !== "all") params.category = category;
      const res = await client.get("/feed", { params });
      const data = res.data;
      if (resetOffset) {
        setStories(data.stories);
        setOffset(PAGE_SIZE);
      }
      setHasMore(data.has_more);
      setTotal(data.total);
    } catch {
      setError("Couldn't load the feed. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [lang, category, offset]);

  // ── Load more (appends to list) ─────────────────────────────────────────────
  async function loadMore() {
    setLoadingMore(true);
    try {
      const params: Record<string, string | number> = { lang, offset, limit: PAGE_SIZE };
      if (category !== "all") params.category = category;
      const res = await client.get("/feed", { params });
      const data = res.data;
      setStories((prev) => {
        const existingIds = new Set(prev.map((s) => s.id));
        const fresh = data.stories.filter((s: StoryPreview) => !existingIds.has(s.id));
        return [...prev, ...fresh];
      });
      setOffset((o) => o + data.stories.length);
      setHasMore(data.has_more);
      setTotal(data.total);
    } catch {
      setError("Couldn't load more. Please try again.");
    } finally {
      setLoadingMore(false);
    }
  }

  // ── Silent poll — picks up stories newly finished by the pipeline ────────────
  const silentPoll = useCallback(async () => {
    if (searchMode) return;
    try {
      const params: Record<string, string> = { lang, limit: "1", offset: "0" };
      if (category !== "all") params.category = category;
      const res = await client.get("/feed", { params });
      const latestTotal: number = res.data.total;
      if (latestTotal > total && total > 0) {
        setNewCount(latestTotal - total);
      }
    } catch {
      // silent — don't disrupt the user
    }
  }, [lang, category, searchMode, total]);

  // ── Effects ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    fetchFeed(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, category]);

  // Start / reset the poll timer whenever deps change
  useEffect(() => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = setInterval(silentPoll, POLL_MS);
    return () => { if (pollTimer.current) clearInterval(pollTimer.current); };
  }, [silentPoll]);

  // ── Search ───────────────────────────────────────────────────────────────────
  async function handleSearch(query: string) {
    if (!query) { fetchFeed(true); return; }
    setLoading(true);
    setError(null);
    setSearchMode(true);
    setSearchQuery(query);
    setNewCount(0);
    try {
      const res = await client.get("/search", { params: { q: query, lang } });
      const mapped: StoryPreview[] = res.data.results.map((r: Record<string, unknown>) => ({
        id:           r.id as number,
        title:        (r.title as string) ?? (r.canonical_title as string) ?? "",
        category:     (r.category as string) ?? "general",
        sentiment:    (r.sentiment as string) ?? "Neutral",
        summary:      (r.summary as string) ?? "",
        language:     (r.language as string) ?? "en",
        source_count: (r.source_count as number) ?? 0,
        created_at:   (r.created_at as string) ?? new Date().toISOString(),
        published_at: (r.published_at as string) ?? (r.created_at as string),
        sources:      (r.sources as StoryPreview["sources"]) ?? [],
      }));
      setStories(mapped);
      setHasMore(false);
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
      <div className="bg-white/60 backdrop-blur-sm border border-teallt/50 rounded-2xl px-4 py-3 mb-5 flex flex-wrap items-center gap-3 shadow-sm">
        <LanguageToggle value={lang} onChange={setLang} />
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

      {/* ── New stories banner ── */}
      {newCount > 0 && !searchMode && (
        <button
          onClick={() => fetchFeed(true)}
          className="w-full mb-4 py-2.5 rounded-xl bg-ocean/10 border border-ocean/30 text-ocean text-sm font-semibold hover:bg-ocean/20 transition-all flex items-center justify-center gap-2"
        >
          <span>↑</span> {newCount} new {newCount === 1 ? "story" : "stories"} — tap to refresh
        </button>
      )}

      {/* ── Search mode banner ── */}
      {searchMode && !loading && (
        <div className="flex items-center justify-between mb-5 px-4 py-2.5 bg-ocean/5 border border-ocean/20 rounded-xl">
          <p className="text-sm text-ocean">
            Results for <span className="font-bold">"{searchQuery}"</span>
            <span className="text-teal ml-1">({stories.length} found)</span>
          </p>
          <button
            onClick={() => fetchFeed(true)}
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
          <p className="text-teal text-sm">
            {searchMode
              ? "Try a different search term."
              : "The pipeline is processing articles — check back in a minute."}
          </p>
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
              {stories.length}{!searchMode && total > 0 ? ` / ${total}` : ""} stories
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stories.map((story) => (
              <SummaryCard key={story.id} story={story} />
            ))}
          </div>

          {/* ── Load more button ── */}
          {!searchMode && hasMore && (
            <div className="mt-8 flex justify-center">
              <button
                id="load-more-btn"
                onClick={loadMore}
                disabled={loadingMore}
                className="flex items-center gap-3 px-8 py-3 rounded-2xl bg-ocean text-white font-semibold
                           hover:bg-ocean/90 active:scale-95 transition-all shadow-md shadow-ocean/20
                           disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loadingMore ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Loading…
                  </>
                ) : (
                  <>
                    <span>↓</span>
                    Load more stories
                  </>
                )}
              </button>
            </div>
          )}

          {/* ── End of list ── */}
          {!searchMode && !hasMore && stories.length > 0 && (
            <p className="text-center text-xs text-teal/60 mt-8 pb-4">
              You've seen all {total} available stories.
              The pipeline adds more every hour. ✓
            </p>
          )}
        </>
      )}
    </div>
  );
}
