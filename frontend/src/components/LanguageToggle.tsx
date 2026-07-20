interface LanguageToggleProps {
  value: string;
  onChange: (lang: string) => void;
}

const LANGUAGES = [
  { code: "en", label: "EN", full: "English" },
  { code: "hi", label: "HI", full: "हिंदी" },
  { code: "ta", label: "TA", full: "தமிழ்" },
  { code: "te", label: "TE", full: "తెలుగు" },
];

export default function LanguageToggle({ value, onChange }: LanguageToggleProps) {
  return (
    <div className="inline-flex rounded-xl border border-teal/40 bg-white/70 overflow-hidden shadow-sm">
      {LANGUAGES.map((lang, i) => (
        <button
          key={lang.code}
          id={`lang-toggle-${lang.code}`}
          title={lang.full}
          onClick={() => onChange(lang.code)}
          className={`px-3.5 py-2 text-xs font-semibold transition-all duration-150 ${
            i > 0 ? "border-l border-teal/30" : ""
          } ${
            value === lang.code
              ? "bg-ocean text-white shadow-inner"
              : "text-ocean hover:bg-teallt/30"
          }`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
