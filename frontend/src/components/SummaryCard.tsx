import { useNavigate } from "react-router-dom";
import { useState, useRef } from "react";
import SentimentBadge from "./SentimentBadge";

export interface ArticleSource {
  name: string;
  url: string;
  title: string;
}

export interface StoryPreview {
  id: number;
  title: string;
  category: string;
  sentiment: string;
  summary: string;
  language: string;
  source_count: number;
  created_at: string;
  published_at?: string;
  sources?: ArticleSource[];
}

const CATEGORY_ICONS: Record<string, string> = {
  technology: "💻",
  finance: "📈",
  sports: "⚽",
  entertainment: "🎬",
  politics: "🏛️",
  general: "📰",
};

function relativeTime(iso: string) {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHrs = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHrs / 24);
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHrs < 24) return `${diffHrs}h ago`;
  if (diffDays === 1) return "Yesterday";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function SourcesChip({ sources }: { sources: ArticleSource[] }) {
  const [open, setOpen] = useState(false);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleEnter = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setOpen(true);
  };

  const handleLeave = () => {
    closeTimer.current = setTimeout(() => setOpen(false), 120);
  };

  if (!sources || sources.length === 0) return null;

  const primary = sources[0];
  const extra = sources.length - 1;

  return (
    <div
      className="relative"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {/* Chip — "India Today +1" */}
      <button
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                   bg-teal/10 border border-teal/25 text-teal/90
                   hover:bg-teal/20 hover:border-teal/50 transition-all duration-150 cursor-pointer"
      >
        <span>📰</span>
        <span className="max-w-[110px] truncate">{primary.name}</span>
        {extra > 0 && (
          <span className="ml-0.5 font-semibold text-ocean/70">+{extra}</span>
        )}
      </button>

      {/* Hover dropdown — news links */}
      {open && (
        <div
          onClick={(e) => e.stopPropagation()}
          onMouseEnter={handleEnter}
          onMouseLeave={handleLeave}
          className="absolute bottom-full left-0 mb-2 z-50 w-72
                     bg-[#0e1a2b] border border-teal/30 rounded-xl shadow-2xl shadow-black/40
                     overflow-hidden"
          style={{ animation: "fadeInUp 0.15s ease-out" }}
        >
          <div className="px-3 py-2 border-b border-teal/20 text-[10px] uppercase tracking-widest text-teal/50 font-semibold">
            {sources.length} source{sources.length !== 1 ? "s" : ""}
          </div>
          <ul className="max-h-60 overflow-y-auto divide-y divide-teal/10">
            {sources.map((src, i) => (
              <li key={i}>
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-col gap-0.5 px-3 py-2.5 hover:bg-teal/10 transition-colors group/link"
                >
                  <span className="text-[0.78rem] font-medium text-ocean/90 line-clamp-2 group-hover/link:text-teal transition-colors leading-snug">
                    {src.title}
                  </span>
                  <span className="text-[10px] text-teal/50 flex items-center gap-1">
                    <span>↗</span>
                    {src.name}
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function SummaryCard({ story }: { story: StoryPreview }) {
  const navigate = useNavigate();
  const icon = CATEGORY_ICONS[story.category?.toLowerCase()] ?? "📰";

  return (
    <article
      id={`story-card-${story.id}`}
      onClick={() => navigate(`/story/${story.id}`)}
      className="group bg-card border border-teal/30 rounded-2xl p-5 cursor-pointer
                 hover:shadow-xl hover:shadow-ocean/10 hover:-translate-y-1
                 hover:border-ocean/40 transition-all duration-200 flex flex-col gap-3"
    >
      {/* Top row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-base leading-none">{icon}</span>
          <span className="text-xs font-semibold uppercase tracking-widest text-teal">
            {story.category || "General"}
          </span>
        </div>
        <SentimentBadge sentiment={story.sentiment || "Neutral"} />
      </div>

      {/* Title */}
      <h2 className="text-[0.95rem] font-bold text-ocean leading-snug line-clamp-2 group-hover:text-ocean/80 transition-colors">
        {story.title}
      </h2>

      {/* Summary snippet */}
      <p className="text-sm text-ocean/70 leading-relaxed line-clamp-3 flex-1">
        {story.summary || <span className="italic text-teal/60">Summary loading…</span>}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-teal/20 text-xs text-teal/80">
        <SourcesChip sources={story.sources ?? []} />
        <span>{relativeTime(story.published_at || story.created_at)}</span>
      </div>
    </article>
  );
}
