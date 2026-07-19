import { useState, FormEvent } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSearch(query.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-teal text-sm pointer-events-none">
          🔍
        </span>
        <input
          id="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search stories…"
          className="w-full pl-9 pr-4 py-2 rounded-xl border border-teal/40 bg-ivory text-ocean placeholder-teal/60 focus:outline-none focus:ring-2 focus:ring-ocean/40 focus:border-ocean transition text-sm"
        />
      </div>
      <button
        id="search-submit"
        type="submit"
        className="px-5 py-2 rounded-xl bg-ocean text-white font-semibold text-sm hover:bg-ocean/90 active:scale-95 transition-all shadow-sm"
      >
        Search
      </button>
    </form>
  );
}
