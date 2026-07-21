import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, ArrowLeft } from "lucide-react";
import client from "../api/client";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [name, setName]         = useState("");
  const [error, setError]       = useState<string | null>(null);
  const [loading, setLoading]   = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        await client.post("/auth/register", { email, password, name });
      }
      const res = await client.post("/auth/login", { email, password });
      localStorage.setItem("briefit_token", res.data.access_token);
      navigate("/feed");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail ?? "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">

      {/* Subtle glow orbs — same as landing page */}
      <div className="absolute top-[-100px] right-[-100px] w-[400px] h-[400px] rounded-full bg-ocean/8 blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-80px] left-[-80px] w-[300px] h-[300px] rounded-full bg-teal/8 blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/3 w-48 h-48 rounded-full bg-ocean/5 blur-2xl pointer-events-none" />

      <div className="relative w-full max-w-[420px]">

        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-ocean shadow-lg shadow-ocean/30 flex items-center justify-center">
              <span className="text-white font-logo font-normal text-xl">B</span>
            </div>
            <div>
              <h1 className="text-3xl font-black text-ocean tracking-tight">BriefIt</h1>
              <p className="text-xs text-teal font-medium">Your news, distilled</p>
            </div>
          </div>
        </div>

        {/* Card */}
        <div className="glass rounded-3xl p-8 shadow-xl shadow-ocean/10">

          {/* Mode tabs */}
          <div className="flex rounded-xl bg-white/60 border border-white/80 mb-6 p-1">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(null); }}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                  mode === m
                    ? "bg-ocean text-white shadow-sm"
                    : "text-teal hover:text-ocean"
                }`}
              >
                {m === "login" ? "Log In" : "Register"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">

            {mode === "register" && (
              <div>
                <label htmlFor="name-input" className="block text-xs font-semibold text-ocean/70 mb-1.5 uppercase tracking-wide">
                  Full Name
                </label>
                <input
                  id="name-input"
                  type="text"
                  placeholder="Jane Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-teallt bg-white/70 text-ocean placeholder-teal/50 focus:outline-none focus:ring-2 focus:ring-ocean/30 focus:border-ocean transition text-sm"
                  required
                />
              </div>
            )}

            <div>
              <label htmlFor="email-input" className="block text-xs font-semibold text-ocean/70 mb-1.5 uppercase tracking-wide">
                Email
              </label>
              <input
                id="email-input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-teallt bg-white/70 text-ocean placeholder-teal/50 focus:outline-none focus:ring-2 focus:ring-ocean/30 focus:border-ocean transition text-sm"
                required
              />
            </div>

            <div>
              <label htmlFor="password-input" className="block text-xs font-semibold text-ocean/70 mb-1.5 uppercase tracking-wide">
                Password
              </label>
              <input
                id="password-input"
                type="password"
                placeholder={mode === "register" ? "Min. 8 characters" : "••••••••"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-teallt bg-white/70 text-ocean placeholder-teal/50 focus:outline-none focus:ring-2 focus:ring-ocean/30 focus:border-ocean transition text-sm"
                required
                minLength={mode === "register" ? 8 : 6}
              />
            </div>

            {error && (
              <div className="flex items-start gap-2.5 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
                <AlertTriangle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <button
              id="auth-submit"
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-ocean text-white font-bold text-sm
                         hover:bg-ocean/90 active:scale-[0.98] transition-all
                         disabled:opacity-50 shadow-md shadow-ocean/20 mt-1"
            >
              {loading
                ? "Please wait…"
                : mode === "login" ? "Log In →" : "Create Account →"}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-teal mt-5 font-medium">
          News distilled in English · हिंदी · தமிழ் · తెలుగు
        </p>
        <div className="text-center mt-4">
          <button
            onClick={() => navigate("/")}
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-ocean transition-colors"
          >
            <ArrowLeft size={12} /> Back to home
          </button>
        </div>
      </div>
    </div>
  );
}
