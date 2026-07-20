import { useNavigate } from "react-router-dom";
import {
  Zap, Globe, Brain, Shield, ChevronRight, BarChart2,
  Layers, RefreshCw, Heart, Bookmark, ArrowRight,
  CheckCircle, Radio, Languages, Sparkles,
} from "lucide-react";

/* ── tiny reusable components ─────────────────────────── */

function GlowOrb({ className }: { className: string }) {
  return <div className={`absolute rounded-full pointer-events-none blur-3xl ${className}`} />;
}

function FeatureCard({
  icon, title, desc, delay,
}: { icon: React.ReactNode; title: string; desc: string; delay: string }) {
  return (
    <div
      className={`group relative glass rounded-2xl p-6 border border-white/60
                  hover:border-ocean/30 hover:shadow-xl hover:shadow-ocean/10
                  transition-all duration-300 hover:-translate-y-1 animate-fade-in-up ${delay}`}
    >
      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-ocean/10 to-teal/10 border border-ocean/20
                      flex items-center justify-center mb-4 text-ocean
                      group-hover:from-ocean/20 group-hover:to-teal/20 transition-all">
        {icon}
      </div>
      <h3 className="text-base font-bold text-slate-800 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
    </div>
  );
}

function StatBadge({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-3xl font-black text-gradient mb-1">{value}</div>
      <div className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</div>
    </div>
  );
}

function StepItem({ n, title, desc }: { n: string; title: string; desc: string }) {
  return (
    <div className="flex gap-5 group">
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-ocean text-white font-black text-sm
                      flex items-center justify-center shadow-md shadow-ocean/25
                      group-hover:scale-110 transition-transform">
        {n}
      </div>
      <div className="pt-1">
        <h4 className="font-bold text-slate-800 text-sm mb-1">{title}</h4>
        <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

/* ── mock news card for hero ───────────────────────────── */
function MockCard({
  category, title, source, time, delay,
}: { category: string; title: string; source: string; time: string; delay: string }) {
  return (
    <div
      className={`glass rounded-xl p-4 border border-white/70 shadow-lg hover:shadow-xl hover:scale-[1.02]
                  transition-all duration-300 cursor-default animate-fade-in-up ${delay}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-bold uppercase tracking-widest text-ocean/70 bg-ocean/10 px-2 py-0.5 rounded-full">
          {category}
        </span>
        <span className="text-[10px] text-slate-400">{time}</span>
      </div>
      <p className="text-[0.78rem] font-semibold text-slate-700 leading-snug line-clamp-2 mb-3">{title}</p>
      <div className="flex items-center gap-2 text-[10px] text-slate-400">
        <div className="w-3.5 h-3.5 rounded-sm bg-slate-200 flex-shrink-0" />
        {source}
      </div>
    </div>
  );
}

/* ── main page ─────────────────────────────────────────── */

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#EEF2F7] overflow-x-hidden font-sans">

      {/* ── NAVBAR ─────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-[#EEF2F7]/80 backdrop-blur-md border-b border-white/60">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-ocean shadow-md shadow-ocean/30 flex items-center justify-center">
              <span className="text-white font-black text-sm">B</span>
            </div>
            <span className="text-xl font-black text-ocean tracking-tight">BriefIt</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/login")}
              className="text-sm font-semibold text-slate-600 hover:text-ocean transition-colors px-4 py-2 rounded-lg hover:bg-ocean/5"
            >
              Log in
            </button>
            <button
              onClick={() => navigate("/login")}
              className="text-sm font-bold bg-ocean text-white px-5 py-2 rounded-xl shadow-md shadow-ocean/20
                         hover:bg-ocean/90 active:scale-95 transition-all flex items-center gap-1.5"
            >
              Get started <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </nav>

      {/* ── HERO ───────────────────────────────────────────── */}
      <section className="relative min-h-[92vh] flex items-center overflow-hidden">
        {/* background orbs */}
        <GlowOrb className="w-[500px] h-[500px] bg-ocean/8 top-[-100px] right-[-100px]" />
        <GlowOrb className="w-[350px] h-[350px] bg-teal/8 bottom-0 left-[-80px]" />
        <GlowOrb className="w-[200px] h-[200px] bg-ocean/6 top-1/2 left-1/3" />

        {/* subtle grid */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{ backgroundImage: "linear-gradient(#2973B2 1px,transparent 1px),linear-gradient(90deg,#2973B2 1px,transparent 1px)", backgroundSize: "60px 60px" }} />

        <div className="relative max-w-6xl mx-auto px-6 py-20 w-full grid lg:grid-cols-2 gap-16 items-center">

          {/* Left — copy */}
          <div>
            <div className="inline-flex items-center gap-2 bg-ocean/10 border border-ocean/20 text-ocean
                            text-xs font-bold px-3 py-1.5 rounded-full mb-6 animate-fade-in">
              <Radio size={11} className="animate-pulse" />
              AI-Powered News Intelligence
            </div>

            <h1 className="text-5xl lg:text-6xl font-black text-slate-800 leading-[1.08] tracking-tight mb-6 animate-fade-in-up">
              News from every<br />
              angle,{" "}
              <span className="text-gradient">distilled</span>
              <br />for you.
            </h1>

            <p className="text-lg text-slate-500 leading-relaxed mb-8 max-w-md animate-fade-in-up delay-100">
              BriefIt clusters hundreds of articles into single clear summaries —
              with multi-source perspective, sentiment analysis, and 4-language support.
            </p>

            <div className="flex flex-wrap gap-3 mb-10 animate-fade-in-up delay-200">
              <button
                onClick={() => navigate("/login")}
                className="flex items-center gap-2 px-7 py-3.5 bg-ocean text-white font-bold rounded-xl
                           shadow-xl shadow-ocean/25 hover:bg-ocean/90 active:scale-95 transition-all text-sm"
              >
                Start reading free <ArrowRight size={15} />
              </button>
              <button
                onClick={() => document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })}
                className="flex items-center gap-2 px-7 py-3.5 bg-white/70 border border-white text-slate-700
                           font-bold rounded-xl hover:bg-white transition-all text-sm shadow-sm"
              >
                See how it works
              </button>
            </div>

            {/* trust badges */}
            <div className="flex flex-wrap gap-5 animate-fade-in-up delay-300">
              {[
                { icon: <CheckCircle size={13} />, text: "No ads" },
                { icon: <CheckCircle size={13} />, text: "Multi-language" },
                { icon: <CheckCircle size={13} />, text: "Real-time updates" },
              ].map((b) => (
                <span key={b.text} className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                  <span className="text-teal">{b.icon}</span>
                  {b.text}
                </span>
              ))}
            </div>
          </div>

          {/* Right — mock cards */}
          <div className="relative hidden lg:block">
            {/* floating deck */}
            <div className="relative h-[480px]">
              <div className="absolute top-0 right-0 w-[300px] animate-float" style={{ animationDelay: "0s" }}>
                <MockCard
                  category="Politics" delay="delay-200"
                  title="Parliament session sees record participation as opposition tables landmark bill"
                  source="The Hindu" time="2h ago"
                />
              </div>
              <div className="absolute top-32 left-0 w-[280px] animate-float" style={{ animationDelay: "1.2s" }}>
                <MockCard
                  category="Technology" delay="delay-300"
                  title="India's AI startup ecosystem crosses $4B in funding — analysts call it a turning point"
                  source="TechCrunch" time="5h ago"
                />
              </div>
              <div className="absolute top-[270px] right-8 w-[270px] animate-float" style={{ animationDelay: "0.7s" }}>
                <MockCard
                  category="Finance" delay="delay-400"
                  title="Sensex closes above 85,000 for the first time amid strong FII inflows"
                  source="Business Standard" time="1h ago"
                />
              </div>

              {/* summary pill overlay */}
              <div className="absolute bottom-0 left-0 right-0 glass rounded-2xl p-4 border border-white/70
                              shadow-xl animate-fade-in-up delay-500">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-ocean flex items-center justify-center flex-shrink-0">
                    <Brain size={15} className="text-white" />
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-ocean/70 uppercase tracking-widest mb-1">AI Summary</p>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Three sources report the Sensex milestone, attributing gains to strong FII confidence
                      and positive macro indicators. Coverage tone is uniformly optimistic.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS ──────────────────────────────────────────── */}
      <section className="bg-white/60 border-y border-white/80 py-12">
        <div className="max-w-4xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 divide-x divide-slate-200/60">
            <StatBadge value="50+" label="RSS Sources" />
            <StatBadge value="4"   label="Languages" />
            <StatBadge value="1hr" label="Update Cycle" />
            <StatBadge value="AI"  label="Summarisation" />
          </div>
        </div>
      </section>

      {/* ── FEATURES ───────────────────────────────────────── */}
      <section className="py-24 relative overflow-hidden">
        <GlowOrb className="w-96 h-96 bg-teal/5 top-0 right-0" />
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14 animate-fade-in-up">
            <p className="text-xs font-bold uppercase tracking-widest text-ocean mb-3">What makes us different</p>
            <h2 className="text-4xl font-black text-slate-800 mb-4">
              Built for the <span className="text-gradient">informed reader</span>
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              Every feature designed to save you time while deepening your understanding.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <FeatureCard
              icon={<Brain size={20} />} delay="delay-100"
              title="AI Story Clustering"
              desc="Dozens of articles about the same event are automatically grouped and distilled into a single, coherent brief."
            />
            <FeatureCard
              icon={<Layers size={20} />} delay="delay-200"
              title="Multi-Source Perspective"
              desc="See how different outlets frame the same story. Our AI surfaces editorial differences so you can read critically."
            />
            <FeatureCard
              icon={<Languages size={20} />} delay="delay-300"
              title="4-Language Support"
              desc="Read news in English, Hindi, Tamil, or Telugu. Summaries are translated automatically for every story."
            />
            <FeatureCard
              icon={<BarChart2 size={20} />} delay="delay-100"
              title="Sentiment Analysis"
              desc="Know at a glance whether a story is being reported positively, negatively, or neutrally across sources."
            />
            <FeatureCard
              icon={<RefreshCw size={20} />} delay="delay-200"
              title="Hourly Refresh"
              desc="The pipeline fetches, clusters, and summarises new articles every hour — you never miss breaking news."
            />
            <FeatureCard
              icon={<Sparkles size={20} />} delay="delay-300"
              title="Explain Simpler"
              desc="Struggling with jargon? One tap rewrites any summary in plain language without losing the key facts."
            />
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ───────────────────────────────────── */}
      <section id="how" className="py-24 bg-white/50 border-y border-white/80 relative overflow-hidden">
        <GlowOrb className="w-72 h-72 bg-ocean/5 bottom-0 left-0" />
        <div className="max-w-6xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
          {/* Left — steps */}
          <div className="animate-slide-left">
            <p className="text-xs font-bold uppercase tracking-widest text-ocean mb-3">The pipeline</p>
            <h2 className="text-4xl font-black text-slate-800 mb-10">
              How BriefIt<br /><span className="text-gradient">works</span>
            </h2>
            <div className="space-y-8">
              <StepItem n="1" title="Ingest from 50+ RSS feeds"
                desc="Every hour, articles from major Indian and global outlets are fetched from curated RSS sources." />
              <StepItem n="2" title="Cluster by semantic similarity"
                desc="A vector embedding model groups articles covering the same event, regardless of source or wording." />
              <StepItem n="3" title="Generate multi-language summaries"
                desc="An LLM condenses each cluster into a neutral, factual brief — then translates it into 4 languages." />
              <StepItem n="4" title="Deliver to your feed"
                desc="Stories appear sorted by recency with sentiment tags, source chips, and perspective notes." />
            </div>
          </div>

          {/* Right — visual */}
          <div className="relative animate-fade-in-up delay-200">
            <div className="glass rounded-3xl p-8 border border-white/80 shadow-2xl shadow-ocean/10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-ocean flex items-center justify-center">
                  <Brain size={18} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-black text-slate-800">Story Summary</p>
                  <p className="text-xs text-slate-400">6 sources · 3 languages available</p>
                </div>
                <span className="ml-auto text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">
                  Neutral
                </span>
              </div>

              <div className="bg-slate-50/80 rounded-2xl p-4 mb-4 border border-slate-100">
                <p className="text-sm text-slate-600 leading-relaxed">
                  The Reserve Bank of India held interest rates steady at 6.5% for the third consecutive
                  quarter, citing controlled inflation and stable growth projections. Markets responded
                  positively with the Sensex closing 1.2% higher.
                </p>
              </div>

              <div className="space-y-2 mb-5">
                {["Times of India", "NDTV Business", "Mint"].map((src) => (
                  <div key={src} className="flex items-center gap-2 px-3 py-2 bg-white/70 rounded-xl border border-slate-100">
                    <div className="w-4 h-4 rounded bg-slate-200 flex-shrink-0" />
                    <span className="text-xs text-slate-600 font-medium flex-1">{src}</span>
                    <ArrowRight size={11} className="text-slate-300" />
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                {["EN", "HI", "TA", "TE"].map((l) => (
                  <span key={l}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all
                      ${l === "EN" ? "bg-ocean text-white" : "bg-slate-100 text-slate-500 hover:bg-ocean/10 hover:text-ocean"}`}>
                    {l}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── PERSONAL FEATURES ──────────────────────────────── */}
      <section className="py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14 animate-fade-in-up">
            <p className="text-xs font-bold uppercase tracking-widest text-ocean mb-3">For you</p>
            <h2 className="text-4xl font-black text-slate-800">
              Your personal news <span className="text-gradient">archive</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Liked card */}
            <div className="glass rounded-3xl p-8 border border-white/80 shadow-lg hover:shadow-xl hover:shadow-rose-500/5 transition-all duration-300 group animate-fade-in-up delay-100">
              <div className="w-12 h-12 rounded-2xl bg-rose-50 border border-rose-100 flex items-center justify-center mb-5
                              group-hover:bg-rose-100 transition-colors">
                <Heart size={22} className="text-rose-500" />
              </div>
              <h3 className="text-xl font-black text-slate-800 mb-3">Liked Stories</h3>
              <p className="text-slate-500 text-sm leading-relaxed">
                Heart any story to save it permanently. Revisit your favourite briefs any time from your personal Liked feed.
              </p>
            </div>

            {/* Bookmarked card */}
            <div className="glass rounded-3xl p-8 border border-white/80 shadow-lg hover:shadow-xl hover:shadow-ocean/5 transition-all duration-300 group animate-fade-in-up delay-200">
              <div className="w-12 h-12 rounded-2xl bg-ocean/10 border border-ocean/20 flex items-center justify-center mb-5
                              group-hover:bg-ocean/20 transition-colors">
                <Bookmark size={22} className="text-ocean" />
              </div>
              <h3 className="text-xl font-black text-slate-800 mb-3">Bookmarks</h3>
              <p className="text-slate-500 text-sm leading-relaxed">
                Save stories to read later. Your bookmarks are always available, sorted by when you saved them.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────────── */}
      <section className="py-24 relative overflow-hidden">
        <GlowOrb className="w-[600px] h-[600px] bg-ocean/7 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        <div className="relative max-w-3xl mx-auto px-6 text-center">
          <div className="glass rounded-3xl p-14 border border-white/80 shadow-2xl shadow-ocean/10 animate-fade-in-up">
            <div className="w-16 h-16 rounded-2xl bg-ocean shadow-xl shadow-ocean/30 flex items-center justify-center mx-auto mb-6 animate-pulse-glow">
              <Zap size={28} className="text-white" />
            </div>
            <h2 className="text-4xl font-black text-slate-800 mb-4">
              Ready to stay <span className="text-gradient">informed?</span>
            </h2>
            <p className="text-slate-500 mb-8 max-w-md mx-auto">
              Join BriefIt and spend less time reading more news. It's free, fast, and always fresh.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="inline-flex items-center gap-2 px-10 py-4 bg-ocean text-white font-bold rounded-xl
                         shadow-xl shadow-ocean/25 hover:bg-ocean/90 active:scale-95 transition-all text-base"
            >
              Create free account <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ─────────────────────────────────────────── */}
      <footer className="border-t border-white/60 bg-white/40 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-ocean flex items-center justify-center">
              <span className="text-white font-black text-xs">B</span>
            </div>
            <span className="font-black text-ocean">BriefIt</span>
            <span className="text-slate-400 text-xs ml-2">AI news intelligence</span>
          </div>
          <div className="flex items-center gap-2 flex-wrap justify-center">
            {["English", "हिंदी", "தமிழ்", "తెలుగు"].map((l) => (
              <span key={l} className="text-xs text-slate-400 px-2 py-0.5 rounded-full bg-slate-100">{l}</span>
            ))}
          </div>
          <p className="text-xs text-slate-400">
            {new Date().getFullYear()} BriefIt · All rights reserved
          </p>
        </div>
      </footer>
    </div>
  );
}
