import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import lensLogo from "../assets/lenslogo.png";

function Landing() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("lensai_dark_mode") === "true";
  });

  useEffect(() => {
    localStorage.setItem("lensai_dark_mode", darkMode);
  }, [darkMode]);

  return (
    <div
      className={`h-screen overflow-hidden ${
        darkMode ? "bg-[#0B0E14] text-[#F5F3FF]" : "bg-[#F6F3FB] text-[#1B1B2A]"
      }`}
    >
      <nav className="flex items-center justify-between px-10 py-6">
        <div className="flex items-center gap-3">
          <img
            src={lensLogo}
            alt="LensAI"
            className="h-11 w-11 rounded-2xl object-cover shadow-md"
          />

          <div>
            <h1 className="text-lg font-bold leading-tight tracking-tight">
              Lens<span className="text-[#B355FF]">AI</span>
            </h1>
            <p className={`text-[11px] uppercase tracking-[0.2em] ${darkMode ? "text-[#9CA3B5]" : "text-slate-500"}`}>
              Focus on what matters
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            className={`flex h-11 w-11 items-center justify-center rounded-full border text-lg transition ${
              darkMode
                ? "border-[#2A2E3A] bg-[#12151D] hover:border-[#7C4DFF]"
                : "border-[#E7E2F5] bg-white shadow-sm hover:border-[#7C4DFF]"
            }`}
          >
            {darkMode ? "☀️" : "🌙"}
          </button>

          <Link
            to="/login"
            className={`rounded-lg border px-5 py-2.5 text-sm font-semibold transition ${
              darkMode
                ? "border-[#2A2E3A] text-[#F5F3FF] hover:border-[#7C4DFF] hover:text-[#B355FF]"
                : "border-[#E7E2F5] bg-white text-[#1B1B2A] shadow-sm hover:border-[#7C4DFF] hover:text-[#7C4DFF]"
            }`}
          >
            Log in
          </Link>

          <Link
            to="/signup"
            className="rounded-lg bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] px-5 py-2.5 text-sm font-semibold text-white shadow-[0_0_30px_rgba(124,77,255,0.35)] transition hover:brightness-110"
          >
            Try LensAI
          </Link>
        </div>
      </nav>

      <main className="grid h-[calc(100vh-96px)] grid-cols-1 items-center gap-8 px-10 md:grid-cols-[1.2fr_0.8fr]">
        <section className="max-w-2xl">
          <div
            className={`mb-7 inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-medium text-[#B355FF] ${
              darkMode ? "border-[#2A2E3A] bg-[#12151D]" : "border-[#E7E2F5] bg-white shadow-sm"
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-[#FF7A59]" />
            Now reading meetings in real time
          </div>

          <h2 className="text-left text-5xl font-black leading-[1.05] tracking-tight md:text-6xl">
            Every meeting,
            <br />
            <span className="bg-gradient-to-r from-[#7C4DFF] via-[#B355FF] to-[#FF7A59] bg-clip-text text-transparent">
              brought into focus.
            </span>
          </h2>

          <p className={`mt-6 max-w-xl text-left text-base leading-7 md:text-lg ${darkMode ? "text-[#9CA3B5]" : "text-slate-600"}`}>
            Drop in a YouTube link or a recording path. LensAI transcribes
            the conversation, sharpens it into a summary, pulls out action
            items and decisions, and stays around to answer your questions.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              to="/signup"
              className="rounded-lg bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] px-8 py-3.5 text-sm font-semibold text-white shadow-[0_0_30px_rgba(124,77,255,0.35)] transition hover:brightness-110"
            >
              Start free
            </Link>

            <Link
              to="/login"
              className={`rounded-lg border px-8 py-3.5 text-sm font-semibold transition ${
                darkMode
                  ? "border-[#2A2E3A] text-[#F5F3FF] hover:border-[#7C4DFF]"
                  : "border-[#E7E2F5] bg-white text-[#1B1B2A] shadow-sm hover:border-[#7C4DFF]"
              }`}
            >
              I have an account
            </Link>
          </div>
        </section>

        <section className="relative hidden h-[420px] items-center justify-center md:flex">
          <div className="absolute h-72 w-72 rounded-full bg-[#7C4DFF]/20 blur-3xl" />
          <div className="absolute right-0 h-64 w-64 rounded-full bg-[#FF7A59]/20 blur-3xl" />
          <div
            className={`relative flex h-64 w-64 items-center justify-center rounded-[32px] border shadow-2xl ${
              darkMode ? "border-[#2A2E3A] bg-[#12151D]" : "border-[#E7E2F5] bg-white"
            }`}
          >
            <img
              src={lensLogo}
              alt="LensAI"
              className="h-32 w-32 rounded-3xl object-cover"
            />
          </div>
        </section>
      </main>
    </div>
  );
}

export default Landing;