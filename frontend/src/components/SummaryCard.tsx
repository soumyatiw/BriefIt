import { useNavigate } from "react-router-dom";
import SentimentBadge from "./SentimentBadge";

export interface StoryPreview {
  id: number;
  title: string;
  category: string;
  sentiment: string;
  summary: string;
  language: string;
  source_count: number;
  created_at: string;
}

const CATEGORY_ICONS: Record<string, string> = {
  technology: "💻",
  finance: "📈",
  sports: "⚽",
  entertainment: "🎬",
  politics: "🏛️",
  general: "📰",
};

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
        <span className="flex items-center gap-1">
          <span>📰</span>
          {story.source_count} source{story.source_count !== 1 ? "s" : ""}
        </span>
        <span>{new Date(story.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
      </div>
    </article>
  );
}
