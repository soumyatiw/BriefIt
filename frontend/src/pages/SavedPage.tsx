import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Heart, Bookmark, ArrowLeft, Inbox } from "lucide-react";
import client from "../api/client";
import SummaryCard, { StoryPreview } from "../components/SummaryCard";

type Tab = "like" | "bookmark";

export default function SavedPage() {
  const navigate = useNavigate();
  const [tab, setTab]         = useState<Tab>("like");
  const [stories, setStories] = useState<StoryPreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [lang]                = useState("en");

  useEffect(() => {
    setLoading(true);
    client
      .get("/interactions/stories", { params: { type: tab, lang } })
      .then((res) => setStories(res.data.stories ?? []))
      .catch(() => setStories([]))
      .finally(() => setLoading(false));
  }, [tab, lang]);

  const tabs: { key: Tab; label: string; icon: React.ReactNode; color: string }[] = [
    { key: "like",     label: "Liked",     icon: <Heart size={15} />,     color: "rose" },
    { key: "bookmark", label: "Bookmarked", icon: <Bookmark size={15} />, color: "ocean" },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">

      {/* Header */}
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
          onClick={() => navigate("/feed")}
          className="flex items-center gap-2 text-sm text-teal hover:text-ocean font-medium transition-colors group"
        >
          <ArrowLeft size={15} className="group-hover:-translate-x-0.5 transition-transform" />
          Back to feed
        </button>
      </header>

      {/* Tab bar */}
      <div className="flex gap-2 mb-6">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all ${
              tab === t.key
                ? t.key === "like"
                  ? "bg-rose-500 text-white shadow-md shadow-rose-500/20"
                  : "bg-ocean text-white shadow-md shadow-ocean/20"
                : "bg-white/60 border border-teal/30 text-ocean hover:border-ocean"
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* Section title */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-teal font-medium uppercase tracking-widest flex items-center gap-1.5">
          {tab === "like" ? <Heart size={12} /> : <Bookmark size={12} />}
          {tab === "like" ? "Liked Stories" : "Bookmarked Stories"}
        </p>
        {!loading && (
          <span className="text-xs text-teal/70 bg-teallt/20 px-2 py-0.5 rounded-full">
            {stories.length} {stories.length === 1 ? "story" : "stories"}
          </span>
        )}
      </div>

      {/* Skeletons */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
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
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && stories.length === 0 && (
        <div className="text-center py-24 flex flex-col items-center gap-3">
          <div className="w-16 h-16 rounded-2xl bg-teallt/30 flex items-center justify-center">
            <Inbox size={28} className="text-teal/50" />
          </div>
          <p className="text-ocean font-semibold text-lg">Nothing here yet</p>
          <p className="text-teal text-sm">
            {tab === "like"
              ? "Heart stories you want to revisit."
              : "Bookmark stories to read later."}
          </p>
          <button
            onClick={() => navigate("/feed")}
            className="mt-2 px-5 py-2 rounded-xl bg-ocean text-white font-semibold text-sm hover:bg-ocean/90 transition"
          >
            Browse feed
          </button>
        </div>
      )}

      {/* Grid */}
      {!loading && stories.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stories.map((story, idx) => (
            <SummaryCard
              key={story.id}
              story={story}
              onNavigate={() =>
                navigate(`/story/${story.id}`, {
                  state: { storyIds: stories.map((s) => s.id), currentIndex: idx },
                })
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
