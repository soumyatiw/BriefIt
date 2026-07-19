import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import client from "../api/client";
import SentimentBadge from "../components/SentimentBadge";
import LanguageToggle from "../components/LanguageToggle";

interface StoryDetail {
  id: number;
  title: string;
  category: string;
  sentiment: string;
  perspective_note: string | null;
  summaries: Record<string, { text: string; simplified_text: string | null }>;
  created_at: string;
}

export default function StoryPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [story, setStory]           = useState<StoryDetail | null>(null);
  const [lang, setLang]             = useState("en");
  const [simplified, setSimplified] = useState(false);
  const [liked, setLiked]           = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [interacting, setInteracting] = useState(false);

  useEffect(() => {
    client.get(`/stories/${id}`).then((res) => setStory(res.data));
  }, [id]);

  async function toggleInteraction(type: "like" | "bookmark") {
    if (interacting) return;
    setInteracting(true);
    try {
      await client.post("/interactions", { story_id: Number(id), type });
      if (type === "like")     setLiked((p) => !p);
      if (type === "bookmark") setBookmarked((p) => !p);
    } finally {
      setInteracting(false);
    }
  }

  /* ── Skeleton ── */
  if (!story) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-card border border-teal/30 rounded-3xl p-7 animate-pulse space-y-4">
          <div className="h-3 w-24 bg-teal/30 rounded-full" />
          <div className="h-6 bg-ocean/20 rounded-xl" />
          <div className="h-5 bg-ocean/15 rounded-xl w-4/5" />
          <div className="h-40 bg-teallt/30 rounded-2xl mt-4" />
        </div>
      </div>
    );
  }

  const activeSummary = story.summaries[lang] ?? story.summaries["en"];
  const displayText   = simplified
    ? (activeSummary?.simplified_text ?? activeSummary?.text)
    : activeSummary?.text;

  const langCount = Object.keys(story.summaries).length;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">

      {/* Back */}
      <button
        id="back-btn"
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-teal hover:text-ocean font-medium mb-5 transition-colors group"
      >
        <span className="group-hover:-translate-x-0.5 transition-transform">←</span>
        Back to feed
      </button>

      {/* Story card */}
      <div className="bg-card border border-teal/30 rounded-3xl overflow-hidden shadow-xl shadow-ocean/8">

        {/* Colored top bar */}
        <div className="h-1 bg-gradient-to-r from-teal via-ocean to-teal" />

        <div className="p-7">

          {/* Category + Sentiment */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold uppercase tracking-widest text-teal">
              {story.category || "General"}
            </span>
            <SentimentBadge sentiment={story.sentiment || "Neutral"} />
          </div>

          {/* Title */}
          <h1 className="text-xl font-black text-ocean leading-snug mb-2">
            {story.title}
          </h1>
          <p className="text-xs text-teal/80 mb-6">
            {new Date(story.created_at).toLocaleDateString(undefined, {
              weekday: "long", year: "numeric", month: "long", day: "numeric",
            })}
            {langCount > 0 && (
              <span className="ml-2 bg-ocean/10 text-ocean px-2 py-0.5 rounded-full">
                {langCount} language{langCount > 1 ? "s" : ""} available
              </span>
            )}
          </p>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-3 mb-5">
            <LanguageToggle value={lang} onChange={setLang} />
            <button
              id="simplify-toggle"
              onClick={() => setSimplified((s) => !s)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-xl border font-semibold transition-all ${
                simplified
                  ? "bg-ocean text-white border-ocean shadow-sm"
                  : "bg-ivory text-ocean border-teal/40 hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              <span>{simplified ? "📖" : "✨"}</span>
              {simplified ? "Show original" : "Explain simpler"}
            </button>
          </div>

          {/* Summary box */}
          <div className="bg-ivory/80 border border-teal/30 rounded-2xl p-5 mb-5 min-h-[7rem]">
            {displayText ? (
              <p className="text-ocean leading-relaxed text-[0.9rem]">{displayText}</p>
            ) : (
              <p className="italic text-teal/60 text-sm">
                Summary not available in this language yet. Try English.
              </p>
            )}
          </div>

          {/* Perspective note */}
          {story.perspective_note && (
            <div className="bg-ocean/5 border border-ocean/20 rounded-2xl p-4 mb-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">🔍</span>
                <p className="text-xs font-bold text-ocean/70 uppercase tracking-wide">
                  Multi-Source Perspective
                </p>
              </div>
              <p className="text-sm text-ocean/80 leading-relaxed">
                {story.perspective_note}
              </p>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-3 pt-2 border-t border-teal/20">
            <button
              id="like-btn"
              onClick={() => toggleInteraction("like")}
              disabled={interacting}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-95 ${
                liked
                  ? "bg-ocean text-white shadow-md shadow-ocean/20"
                  : "bg-ivory text-ocean border border-teal/40 hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              <span className={`transition-transform ${liked ? "scale-125" : ""}`}>
                {liked ? "♥" : "♡"}
              </span>
              {liked ? "Liked" : "Like"}
            </button>

            <button
              id="bookmark-btn"
              onClick={() => toggleInteraction("bookmark")}
              disabled={interacting}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-95 ${
                bookmarked
                  ? "bg-ocean text-white shadow-md shadow-ocean/20"
                  : "bg-ivory text-ocean border border-teal/40 hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              <span>🔖</span>
              {bookmarked ? "Saved" : "Bookmark"}
            </button>

            <button
              onClick={() => navigate(-1)}
              className="ml-auto flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium text-teal hover:text-ocean hover:bg-teallt/20 transition-all border border-transparent hover:border-teal/30"
            >
              ← Feed
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
