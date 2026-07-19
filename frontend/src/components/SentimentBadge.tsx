interface SentimentBadgeProps {
  sentiment: "Positive" | "Neutral" | "Negative" | string;
}

const STYLES: Record<string, string> = {
  Positive: "bg-ocean/10 text-ocean border-ocean/30",
  Neutral:  "bg-teal/10 text-teal border-teal/40",
  Negative: "bg-red-100 text-red-700 border-red-200",
};

const ICONS: Record<string, string> = {
  Positive: "↑",
  Neutral:  "–",
  Negative: "↓",
};

export default function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  const style = STYLES[sentiment] ?? STYLES.Neutral;
  const icon  = ICONS[sentiment]  ?? ICONS.Neutral;
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style}`}>
      <span>{icon}</span>
      {sentiment}
    </span>
  );
}
