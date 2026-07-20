import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  ArrowLeft, ChevronLeft, ChevronRight, Heart, Bookmark,
  ExternalLink, Search, Monitor, TrendingUp, Trophy,
  Clapperboard, Landmark, Newspaper, Globe,
} from "lucide-react";
import client from "../api/client";
import SentimentBadge from "../components/SentimentBadge";
import LanguageToggle from "../components/LanguageToggle";

interface ArticleSource {
  name: string;
  url: string;
  title: string;
  domain: string;
}

interface StoryDetail {
  id: number;
  title: string;
  category: string;
  sentiment: string;
  perspective_note: string | null;
  summaries: Record<string, { text: string; simplified_text: string | null }>;
  created_at: string;
  published_at?: string;
  sources?: ArticleSource[];
}

interface NavState {
  storyIds?: number[];
  currentIndex?: number;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  technology:    <Monitor size={14} />,
  finance:       <TrendingUp size={14} />,
  sports:        <Trophy size={14} />,
  entertainment: <Clapperboard size={14} />,
  politics:      <Landmark size={14} />,
  general:       <Newspaper size={14} />,
};

export default function StoryPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const navState = (location.state ?? {}) as NavState;
  const storyIds: number[] = navState.storyIds ?? [];
  const currentIndex: number = navState.currentIndex ?? -1;

  const [story, setStory]               = useState<StoryDetail | null>(null);
  const [lang, setLang]                 = useState("en");
  const [simplified, setSimplified]     = useState(false);
  const [liked, setLiked]               = useState(false);
  const [bookmarked, setBookmarked]     = useState(false);
  const [interacting, setInteracting]   = useState(false);

  // Load story + current interaction state
  useEffect(() => {
    setStory(null);
    setSimplified(false);
    const storyId = Number(id);
    client.get(`/stories/${storyId}`).then((res) => setStory(res.data));

    // Load existing like/bookmark state for this story
    Promise.all([
      client.get("/interactions", { params: { type: "like" } }),
      client.get("/interactions", { params: { type: "bookmark" } }),
    ]).then(([likeRes, bmRes]) => {
      setLiked(likeRes.data.story_ids.includes(storyId));
      setBookmarked(bmRes.data.story_ids.includes(storyId));
    }).catch(() => {}); // not logged in — silently ignore
  }, [id]);

  // Keyboard navigation
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.target as HTMLElement).tagName === "INPUT") return;
      if (e.key === "ArrowRight") goNext();
      if (e.key === "ArrowLeft")  goPrev();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const hasPrev = currentIndex > 0 && storyIds.length > 0;
  const hasNext = currentIndex >= 0 && currentIndex < storyIds.length - 1;

  function goNext() {
    if (!hasNext) return;
    navigate(`/story/${storyIds[currentIndex + 1]}`, {
      state: { storyIds, currentIndex: currentIndex + 1 },
    });
  }
  function goPrev() {
    if (!hasPrev) return;
    navigate(`/story/${storyIds[currentIndex - 1]}`, {
      state: { storyIds, currentIndex: currentIndex - 1 },
    });
  }

  async function toggleInteraction(type: "like" | "bookmark") {
    if (interacting) return;
    setInteracting(true);
    try {
      const res = await client.post("/interactions", { story_id: Number(id), type });
      const added = res.data.status === "added";
      if (type === "like")     setLiked(added);
      if (type === "bookmark") setBookmarked(added);
    } catch {
      // 401 → redirect handled by axios interceptor
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
  const categoryIcon = CATEGORY_ICONS[story.category?.toLowerCase()] ?? <Newspaper size={14} />;

  const NavBtn = ({
    onClick, disabled, children, id: btnId,
  }: { onClick: () => void; disabled: boolean; children: React.ReactNode; id?: string }) => (
    <button
      id={btnId}
      onClick={onClick}
      disabled={disabled}
      className={`w-9 h-9 flex items-center justify-center rounded-xl border font-bold transition-all
        ${disabled
          ? "border-teal/20 text-teal/30 cursor-not-allowed"
          : "border-teal/40 text-ocean hover:bg-teal/20 hover:border-ocean active:scale-95"}`}
    >
      {children}
    </button>
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">

      {/* ── Top nav ── */}
      <div className="flex items-center justify-between mb-5">
        <button
          id="back-btn"
          onClick={() => navigate("/feed")}
          className="flex items-center gap-2 text-sm text-teal hover:text-ocean font-medium transition-colors group"
        >
          <ArrowLeft size={15} className="group-hover:-translate-x-0.5 transition-transform" />
          Back to feed
        </button>

        {storyIds.length > 0 && (
          <div className="flex items-center gap-2">
            {currentIndex >= 0 && (
              <span className="text-xs text-teal/60 font-medium tabular-nums">
                {currentIndex + 1} / {storyIds.length}
              </span>
            )}
            <NavBtn id="prev-story-btn" onClick={goPrev} disabled={!hasPrev}>
              <ChevronLeft size={18} />
            </NavBtn>
            <NavBtn id="next-story-btn" onClick={goNext} disabled={!hasNext}>
              <ChevronRight size={18} />
            </NavBtn>
          </div>
        )}
      </div>

      {/* ── Story card ── */}
      <div className="bg-card border border-teal/30 rounded-3xl overflow-hidden shadow-xl shadow-ocean/8">
        <div className="h-1 bg-gradient-to-r from-teal via-ocean to-teal" />

        <div className="p-7">

          {/* Category + Sentiment */}
          <div className="flex items-center justify-between mb-4">
            <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-teal">
              {categoryIcon}
              {story.category || "General"}
            </span>
            <SentimentBadge sentiment={story.sentiment || "Neutral"} />
          </div>

          {/* Title */}
          <h1 className="text-xl font-black text-ocean leading-snug mb-2">{story.title}</h1>
          <p className="text-xs text-teal/80 mb-5">
            {new Date(story.published_at ?? story.created_at).toLocaleDateString(undefined, {
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
                  : "bg-white/70 text-ocean border-teal/40 hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              <Search size={14} />
              {simplified ? "Show original" : "Explain simpler"}
            </button>
          </div>

          {/* Summary */}
          <div className="bg-white/80 border border-teal/30 rounded-2xl p-5 mb-5 min-h-[7rem]">
            {displayText ? (
              <p className="text-ocean leading-relaxed text-[0.9rem]">{displayText}</p>
            ) : (
              <p className="italic text-teal/60 text-sm">
                Summary not available in this language yet. Try English.
              </p>
            )}
          </div>

          {/* Sources */}
          {story.sources && story.sources.length > 0 && (
            <div className="mb-5">
              <p className="text-[10px] font-bold uppercase tracking-widest text-teal/60 mb-2 flex items-center gap-1">
                <Globe size={10} />
                {story.sources.length} Source{story.sources.length > 1 ? "s" : ""}
              </p>
              <ul className="flex flex-col gap-2">
                {story.sources.map((src, i) => {
                  const faviconUrl = src.domain
                    ? `https://www.google.com/s2/favicons?domain=${src.domain}&sz=32`
                    : null;
                  return (
                    <li key={i}>
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="flex items-start gap-3 p-3 rounded-xl border border-teal/20
                                   bg-white/50 hover:bg-teallt/20 hover:border-ocean/30
                                   transition-all group/src"
                      >
                        {faviconUrl ? (
                          <img src={faviconUrl} alt="" className="w-5 h-5 rounded object-contain mt-0.5 flex-shrink-0"
                            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                        ) : (
                          <Globe size={16} className="text-teal/50 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="min-w-0 flex-1">
                          <p className="text-[0.8rem] font-semibold text-ocean leading-snug line-clamp-2 group-hover/src:text-ocean/80 transition-colors">
                            {src.title}
                          </p>
                          <p className="text-[10px] text-teal/60 mt-0.5 flex items-center gap-1">
                            <span className="font-medium">{src.name}</span>
                            <ExternalLink size={9} />
                          </p>
                        </div>
                      </a>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Perspective */}
          {story.perspective_note && (
            <div className="bg-ocean/5 border border-ocean/20 rounded-2xl p-4 mb-5">
              <div className="flex items-center gap-2 mb-2">
                <Search size={14} className="text-ocean/60" />
                <p className="text-xs font-bold text-ocean/70 uppercase tracking-wide">
                  Multi-Source Perspective
                </p>
              </div>
              <p className="text-sm text-ocean/80 leading-relaxed">{story.perspective_note}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2 border-t border-teal/20">
            <button
              id="like-btn"
              onClick={() => toggleInteraction("like")}
              disabled={interacting}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-95 ${
                liked
                  ? "bg-rose-500 text-white shadow-md shadow-rose-500/20"
                  : "bg-white/70 text-ocean border border-teal/40 hover:border-rose-400 hover:text-rose-500"
              }`}
            >
              <Heart size={15} className={liked ? "fill-white" : ""} />
              {liked ? "Liked" : "Like"}
            </button>

            <button
              id="bookmark-btn"
              onClick={() => toggleInteraction("bookmark")}
              disabled={interacting}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-95 ${
                bookmarked
                  ? "bg-ocean text-white shadow-md shadow-ocean/20"
                  : "bg-white/70 text-ocean border border-teal/40 hover:border-ocean hover:bg-teallt/20"
              }`}
            >
              <Bookmark size={15} className={bookmarked ? "fill-white" : ""} />
              {bookmarked ? "Saved" : "Bookmark"}
            </button>

            <div className="ml-auto flex items-center gap-2">
              <NavBtn onClick={goPrev} disabled={!hasPrev}>
                <ChevronLeft size={18} />
              </NavBtn>
              <NavBtn onClick={goNext} disabled={!hasNext}>
                <ChevronRight size={18} />
              </NavBtn>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
