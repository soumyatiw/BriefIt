import { useNavigate } from "react-router-dom";
import { useState, useRef } from "react";
import {
  Monitor, TrendingUp, Trophy, Clapperboard, Landmark, Newspaper,
  ExternalLink, ChevronRight,
} from "lucide-react";
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

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  technology:    <Monitor size={13} />,
  finance:       <TrendingUp size={13} />,
  sports:        <Trophy size={13} />,
  entertainment: <Clapperboard size={13} />,
  politics:      <Landmark size={13} />,
  general:       <Newspaper size={13} />,
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

  const handleEnter = () => { if (closeTimer.current) clearTimeout(closeTimer.current); setOpen(true); };
  const handleLeave = () => { closeTimer.current = setTimeout(() => setOpen(false), 120); };

  if (!sources || sources.length === 0) return null;

  const primary = sources[0];
  const extra = sources.length - 1;

  let faviconUrl: string | null = null;
  try { faviconUrl = `https://www.google.com/s2/favicons?domain=${new URL(primary.url).hostname}&sz=32`; } catch {}

  return (
    <div className="relative" onMouseEnter={handleEnter} onMouseLeave={handleLeave}>
      <button
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                   bg-teal/10 border border-teal/25 text-teal/90
                   hover:bg-teal/20 hover:border-teal/50 transition-all duration-150 cursor-pointer"
      >
        {faviconUrl ? (
          <img src={faviconUrl} alt="" className="w-3.5 h-3.5 rounded-sm object-contain flex-shrink-0"
            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
        ) : (
          <Newspaper size={12} className="flex-shrink-0" />
        )}
        <span className="max-w-[110px] truncate">{primary.name}</span>
        {extra > 0 && <span className="ml-0.5 font-semibold text-ocean/70">+{extra}</span>}
      </button>

      {open && (
        <div
          onClick={(e) => e.stopPropagation()}
          onMouseEnter={handleEnter}
          onMouseLeave={handleLeave}
          className="absolute bottom-full left-0 mb-2 z-50 w-72
                     bg-[#0e1a2b] border border-teal/30 rounded-xl shadow-2xl shadow-black/40 overflow-hidden"
          style={{ animation: "fadeInUp 0.15s ease-out" }}
        >
          <div className="px-3 py-2 border-b border-teal/20 text-[10px] uppercase tracking-widest text-teal/50 font-semibold">
            {sources.length} source{sources.length !== 1 ? "s" : ""}
          </div>
          <ul className="max-h-60 overflow-y-auto divide-y divide-teal/10">
            {sources.map((src, i) => {
              let srcFavicon: string | null = null;
              try { srcFavicon = `https://www.google.com/s2/favicons?domain=${new URL(src.url).hostname}&sz=32`; } catch {}
              return (
                <li key={i}>
                  <a href={src.url} target="_blank" rel="noopener noreferrer"
                    className="flex flex-col gap-0.5 px-3 py-2.5 hover:bg-teal/10 transition-colors group/link">
                    <span className="text-[0.78rem] font-medium text-ocean/90 line-clamp-2 group-hover/link:text-teal transition-colors leading-snug">
                      {src.title}
                    </span>
                    <span className="text-[10px] text-teal/50 flex items-center gap-1.5">
                      {srcFavicon && (
                        <img src={srcFavicon} alt="" className="w-3 h-3 rounded-sm object-contain flex-shrink-0"
                          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                      )}
                      <span className="font-medium text-teal/70">{src.name}</span>
                      <ExternalLink size={9} />
                    </span>
                  </a>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function SummaryCard({
  story,
  onNavigate,
}: {
  story: StoryPreview;
  onNavigate?: () => void;
}) {
  const navigate = useNavigate();
  const icon = CATEGORY_ICONS[story.category?.toLowerCase()] ?? <Newspaper size={13} />;
  const handleClick = onNavigate ?? (() => navigate(`/story/${story.id}`));

  return (
    <article
      id={`story-card-${story.id}`}
      onClick={handleClick}
      className="group bg-card border border-teal/30 rounded-2xl p-5 cursor-pointer
                 hover:shadow-xl hover:shadow-ocean/10 hover:-translate-y-1
                 hover:border-ocean/40 transition-all duration-200 flex flex-col gap-3"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-teal">
          {icon}
          <span className="text-xs font-semibold uppercase tracking-widest">
            {story.category || "General"}
          </span>
        </div>
        <SentimentBadge sentiment={story.sentiment || "Neutral"} />
      </div>

      <h2 className="text-[0.95rem] font-bold text-ocean leading-snug line-clamp-2 group-hover:text-ocean/80 transition-colors">
        {story.title}
      </h2>

      <p className="text-sm text-ocean/70 leading-relaxed line-clamp-3 flex-1">
        {story.summary || <span className="italic text-teal/60">Summary loading…</span>}
      </p>

      <div className="flex items-center justify-between pt-2 border-t border-teal/20 text-xs text-teal/80">
        <SourcesChip sources={story.sources ?? []} />
        <span>{relativeTime(story.published_at || story.created_at)}</span>
      </div>
    </article>
  );
}
