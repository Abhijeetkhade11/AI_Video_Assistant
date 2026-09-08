import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import lensLogo from "../assets/lenslogo.png";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("lensai_dark_mode") === "true";
  });

  useEffect(() => {
    localStorage.setItem("lensai_dark_mode", darkMode);
  }, [darkMode]);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getErrorMessage = (err) => {
    const detail = err.response?.data?.detail;

    if (Array.isArray(detail)) {
      const message = detail[0]?.msg || "Validation failed";
      return message.replace("Value error, ", "");
    }

    if (typeof detail === "string") {
      return detail;
    }

    return "Login failed. Please check your email and password.";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError("");

      await login(email, password);

      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`relative flex h-screen items-center justify-center overflow-hidden px-6 ${
        darkMode ? "bg-[#0B0E14]" : "bg-[#F6F3FB]"
      }`}
    >
      <div className="absolute -left-20 top-0 h-[380px] w-[380px] rounded-full bg-[#7C4DFF]/25 blur-3xl" />
      <div className="absolute -right-16 bottom-0 h-[340px] w-[340px] rounded-full bg-[#FF7A59]/20 blur-3xl" />

      <button
        onClick={() => setDarkMode(!darkMode)}
        title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        className={`absolute right-6 top-6 z-20 flex h-11 w-11 items-center justify-center rounded-full border text-lg transition ${
          darkMode
            ? "border-[#2A2E3A] bg-[#12151D] hover:border-[#7C4DFF]"
            : "border-[#E7E2F5] bg-white shadow-sm hover:border-[#7C4DFF]"
        }`}
      >
        {darkMode ? "☀️" : "🌙"}
      </button>

      <div
        className={`relative z-10 grid w-full max-w-4xl grid-cols-1 overflow-hidden rounded-[24px] border shadow-2xl md:grid-cols-[0.9fr_1.1fr] ${
          darkMode ? "border-[#2A2E3A] bg-[#12151D]" : "border-[#E7E2F5] bg-white"
        }`}
      >
        <div className="hidden flex-col justify-between bg-gradient-to-br from-[#7C4DFF] to-[#FF7A59] p-10 md:flex">
          <img
            src={lensLogo}
            alt="LensAI"
            className="h-12 w-12 rounded-2xl object-cover shadow-md"
          />
          <div>
            <h2 className="text-3xl font-black leading-tight text-white">
              Welcome back to your workspace.
            </h2>
            <p className="mt-3 text-sm text-white/80">
              Every transcript, summary, and answer you've captured is
              waiting right where you left it.
            </p>
          </div>
          <p className="text-xs text-white/60">LensAI &middot; Focus on what matters</p>
        </div>

        <div className="p-8 sm:p-10">
          <div className="mb-8 flex items-center gap-2 md:hidden">
            <img
              src={lensLogo}
              alt="LensAI"
              className="h-9 w-9 rounded-xl object-cover shadow-sm"
            />
            <span className={`text-lg font-bold ${darkMode ? "text-[#F5F3FF]" : "text-[#1B1B2A]"}`}>
              LensAI
            </span>
          </div>

          <h2 className={`text-2xl font-bold ${darkMode ? "text-[#F5F3FF]" : "text-[#1B1B2A]"}`}>
            Log in
          </h2>
          <p className={`mt-1 text-sm ${darkMode ? "text-[#9CA3B5]" : "text-slate-500"}`}>
            Pick up right where you left off.
          </p>

          <form onSubmit={handleSubmit} className="mt-7 space-y-4">
            <div>
              <label className={`text-xs font-semibold uppercase tracking-wide ${darkMode ? "text-[#9CA3B5]" : "text-slate-500"}`}>
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError("");
                }}
                placeholder="you@example.com"
                required
                className={`mt-2 w-full rounded-lg border px-4 py-3 text-sm outline-none transition focus:border-[#7C4DFF] focus:ring-2 focus:ring-[#7C4DFF]/30 ${
                  darkMode
                    ? "border-[#2A2E3A] bg-[#0B0E14] text-[#F5F3FF]"
                    : "border-[#E7E2F5] bg-[#F6F3FB] text-[#1B1B2A]"
                }`}
              />
            </div>

            <div>
              <label className={`text-xs font-semibold uppercase tracking-wide ${darkMode ? "text-[#9CA3B5]" : "text-slate-500"}`}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError("");
                }}
                placeholder="Enter your password"
                required
                className={`mt-2 w-full rounded-lg border px-4 py-3 text-sm outline-none transition focus:border-[#7C4DFF] focus:ring-2 focus:ring-[#7C4DFF]/30 ${
                  darkMode
                    ? "border-[#2A2E3A] bg-[#0B0E14] text-[#F5F3FF]"
                    : "border-[#E7E2F5] bg-[#F6F3FB] text-[#1B1B2A]"
                }`}
              />
            </div>

            {error && (
              <p className="rounded-lg border border-[#FF7A59]/30 bg-[#FF7A59]/10 px-3 py-2 text-xs text-[#E85D3D]">
                {String(error)}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] py-3 text-sm font-semibold text-white shadow-[0_0_25px_rgba(124,77,255,0.3)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className={`mt-6 text-center text-sm ${darkMode ? "text-[#9CA3B5]" : "text-slate-500"}`}>
            New to LensAI?{" "}
            <Link to="/signup" className="font-semibold text-[#B355FF]">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;