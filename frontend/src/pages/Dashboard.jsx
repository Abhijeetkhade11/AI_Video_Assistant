import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";

import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import API from "../api/api";
import lensLogo from "../assets/lenslogo.png";

function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("lensai_dark_mode") === "true";
  });

  const [source, setSource] = useState("");
  const [language, setLanguage] = useState("english");
  const [searchQuery, setSearchQuery] = useState("");

  const [meetings, setMeetings] = useState([]);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [chats, setChats] = useState([]);

  const [activeView, setActiveView] = useState("home");
  const [processing, setProcessing] = useState(false);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    localStorage.setItem("lensai_dark_mode", darkMode);
  }, [darkMode]);

  const fetchMeetings = async () => {
    const res = await API.get("/meetings/");
    setMeetings(res.data);
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleNewMeeting = () => {
    setSelectedMeeting(null);
    setChats([]);
    setSource("");
    setQuestion("");
    setActiveView("home");
    setError("");
  };

  const loadMeeting = async (meetingId, view = "summary") => {
    const meetingRes = await API.get(`/meetings/${meetingId}`);
    setSelectedMeeting(meetingRes.data);

    const chatRes = await API.get(`/meetings/${meetingId}/chats`);
    setChats(chatRes.data);

    setActiveView(view === "chat" ? "summary" : view);
    setError("");
  };

  const handleDeleteMeeting = async (meetingId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this meeting?"
    );

    if (!confirmDelete) return;

    try {
      await API.delete(`/meetings/${meetingId}`);

      if (selectedMeeting?.id === meetingId) {
        handleNewMeeting();
      }

      await fetchMeetings();
    } catch {
      setError("Failed to delete meeting");
    }
  };
  const handleRenameMeeting = async (meetingId, title) => {
    try {
      await API.patch(`/meetings/${meetingId}/rename`, {
        title,
      });

      await fetchMeetings();

      if (selectedMeeting && selectedMeeting.id === meetingId) {
        await loadMeeting(meetingId);
      }
    } catch {
      setError("Failed to rename meeting");
    }
  };

  const handleProcessMeeting = async () => {
    if (!source.trim()) return;

    try {
      setProcessing(true);
      setError("");

      const res = await API.post("/meetings/process", {
        source,
        language,
      });

      await fetchMeetings();
      await loadMeeting(res.data.meeting_id, "summary");

      setSource("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to process meeting");
    } finally {
      setProcessing(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim() || !selectedMeeting) return;

    const userQuestion = question;

    try {
      setAsking(true);
      setError("");
      setQuestion("");

      const res = await API.post(`/meetings/${selectedMeeting.id}/ask`, {
        question: userQuestion,
      });

      setChats((prev) => [...prev, res.data]);

      await fetchMeetings();
    } catch {
      setError("Failed to get answer");
      setQuestion(userQuestion);
    } finally {
      setAsking(false);
    }
  };

  const filteredMeetings = meetings.filter((meeting) => {
    const text = `${meeting.title || ""} ${meeting.source || ""}`.toLowerCase();
    return text.includes(searchQuery.toLowerCase());
  });

  const isYoutube =
    source.includes("youtube.com") || source.includes("youtu.be");

  return (
    <div
      className={`relative flex h-screen overflow-hidden ${
        darkMode ? "bg-[#0A0A12] text-[#F5F3FF]" : "bg-[#F6F3FB] text-[#1B1B2A]"
      }`}
    >
      {/* ambient glows, matching the login/signup soft background treatment */}
      <div className="pointer-events-none absolute -left-24 -top-20 h-[420px] w-[420px] rounded-full bg-[#7C4DFF]/20 blur-3xl" />
      <div className="pointer-events-none absolute right-0 top-1/3 h-[380px] w-[380px] rounded-full bg-[#FF7A59]/15 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-[300px] w-[300px] rounded-full bg-[#B355FF]/10 blur-3xl" />

      <Sidebar
        user={user}
        darkMode={darkMode}
        logout={handleLogout}
        meetings={filteredMeetings}
        selectedMeeting={selectedMeeting}
        onNewMeeting={handleNewMeeting}
        onSelectMeeting={(id) => loadMeeting(id, "summary")}
        onSelectChat={(id) => loadMeeting(id, "chat")}
        onDeleteMeeting={handleDeleteMeeting}
        onRenameMeeting={handleRenameMeeting}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      <main className="relative z-10 flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-end gap-3 px-8 py-6">
          <button
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            className={`flex h-11 w-11 items-center justify-center rounded-full border text-lg transition ${
              darkMode
                ? "border-[#2A2E3A] bg-[#14141F] hover:border-[#7C4DFF]"
                : "border-[#E7E2F5] bg-white shadow-sm hover:border-[#7C4DFF]"
            }`}
          >
            {darkMode ? "☀️" : "🌙"}
          </button>

          <div
            className={`flex items-center gap-3 rounded-full py-1.5 pl-1.5 pr-4 shadow-sm ${
              darkMode ? "bg-[#14141F] border border-[#2A2E3A]" : "bg-white border border-[#E7E2F5]"
            }`}
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#FF7A59] text-sm font-bold text-white">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="leading-tight">
              <p className="text-sm font-semibold">{user?.name || "User"}</p>
              <p className="text-[11px] text-slate-500">{user?.email}</p>
            </div>
          </div>
        </header>

        <section className="flex flex-1 flex-col overflow-hidden px-8 pb-8">
          {activeView === "home" && (
            <div className="flex flex-1 items-center justify-center">
              <div
                className={`grid w-full max-w-4xl grid-cols-1 overflow-hidden rounded-[24px] border shadow-2xl md:grid-cols-[0.85fr_1.15fr] ${
                  darkMode ? "border-[#2A2E3A] bg-[#12151D]" : "border-[#E7E2F5] bg-white"
                }`}
              >
                {/* left brand panel, mirrors the login/signup split layout */}
                <div className="hidden flex-col justify-between bg-gradient-to-br from-[#7C4DFF] to-[#FF7A59] p-8 md:flex">
                  <img
                    src={lensLogo}
                    alt="LensAI"
                    className="h-12 w-12 rounded-2xl object-cover shadow-md"
                  />

                  <div>
                    <h2 className="text-2xl font-black leading-tight text-white">
                      What should we bring into focus today?
                    </h2>
                    <p className="mt-3 text-sm text-white/80">
                      Drop in a YouTube link or a recording path and LensAI
                      will transcribe it, summarize it, and stay around to
                      answer questions.
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/15 px-4 py-3 text-white backdrop-blur">
                    <p className="text-2xl font-bold">{meetings.length}</p>
                    <p className="text-xs text-white/70">meetings processed so far</p>
                  </div>
                </div>

                {/* right input panel */}
                <div className="p-8">
                  <div className="mb-6 flex items-center gap-2 md:hidden">
                    <img
                      src={lensLogo}
                      alt="LensAI"
                      className="h-9 w-9 rounded-xl object-cover shadow-sm"
                    />
                    <span className="text-lg font-bold">LensAI</span>
                  </div>

                  <h1 className="text-2xl font-bold">New meeting</h1>
                  <p className={`mt-1 text-sm ${darkMode ? "text-slate-400" : "text-slate-500"}`}>
                    Paste a YouTube URL or a meeting recording path.
                  </p>

                  <textarea
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    rows={5}
                    placeholder="https://youtube.com/watch?v=... or /path/to/recording.mp3"
                    className={`mt-5 w-full resize-none rounded-xl border px-4 py-3 text-sm outline-none transition ${
                      darkMode
                        ? "border-[#2A2E3A] bg-[#0A0A12] text-white placeholder:text-slate-500 focus:border-[#7C4DFF]"
                        : "border-[#E7E2F5] bg-[#F6F3FB] text-slate-900 placeholder:text-slate-400 focus:border-[#7C4DFF]"
                    }`}
                  />

                  <p className="mt-2 text-xs text-slate-500">
                    {source
                      ? isYoutube
                        ? "YouTube video detected"
                        : "Meeting file/path detected"
                      : "Supports YouTube links and local meeting paths"}
                  </p>

                  <div className="mt-5 flex items-center gap-3">
                    <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Language
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className={`rounded-lg border px-3 py-2 text-sm outline-none ${
                        darkMode
                          ? "border-[#2A2E3A] bg-[#0A0A12] text-white"
                          : "border-[#E7E2F5] bg-white text-slate-700"
                      }`}
                    >
                      <option value="english">English</option>
                      <option value="hinglish">Hinglish</option>
                    </select>
                  </div>

                  <button
                    onClick={handleProcessMeeting}
                    disabled={!source.trim() || processing}
                    className="mt-6 w-full rounded-xl bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] py-3.5 text-sm font-semibold text-white shadow-[0_0_25px_rgba(124,77,255,0.3)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {processing ? "Processing..." : "Process meeting"}
                  </button>

                  {processing && (
                    <div
                      className={`mt-5 rounded-xl border p-4 text-left ${
                        darkMode
                          ? "border-[#2A2E3A] bg-[#0A0A12] text-slate-300"
                          : "border-[#E7E2F5] bg-[#F6F3FB] text-slate-600"
                      }`}
                    >
                      <h3 className="mb-1 text-sm font-semibold">
                        {isYoutube
                          ? "Your YouTube video is being processed..."
                          : "Your meeting recording is being processed..."}
                      </h3>
                      <p className="text-xs leading-5">
                        Extracting audio, transcribing speech, and building
                        AI memory. This may take a few minutes.
                      </p>
                    </div>
                  )}

                  {error && (
                    <p className="mt-5 rounded-lg border border-[#FF7A59]/30 bg-[#FF7A59]/10 px-4 py-3 text-sm text-[#E85D3D]">
                      {String(error)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {selectedMeeting && activeView !== "home" && (
            <div className="flex h-full flex-col gap-5 overflow-hidden lg:flex-row">
              {/* left rail: meeting meta + vertical tab switcher */}
              <div
                className={`flex shrink-0 flex-col gap-4 rounded-2xl border p-5 lg:w-64 ${
                  darkMode ? "border-[#2A2E3A] bg-[#12151D]" : "border-[#E7E2F5] bg-white"
                }`}
              >
                <div>
                  <h1 className="text-xl font-black leading-tight tracking-tight">
                    {selectedMeeting.title}
                  </h1>
                  <p className="mt-1 truncate text-xs text-slate-500">
                    {selectedMeeting.source}
                  </p>
                </div>

                <div className="flex flex-row gap-2 lg:flex-col">
                  {["summary", "transcript"].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveView(tab)}
                      className={`rounded-xl px-4 py-2.5 text-left text-sm font-semibold capitalize transition ${
                        activeView === tab
                          ? "bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] text-white"
                          : darkMode
                          ? "bg-[#0A0A12] text-slate-300"
                          : "bg-[#F6F3FB] text-slate-700"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* right: content + chat */}
              <div
                className={`flex-1 overflow-y-auto rounded-2xl border p-6 ${
                  darkMode
                    ? "border-[#2A2E3A] bg-[#12151D]"
                    : "border-[#E7E2F5] bg-white"
                }`}
              >
                {activeView === "summary" && (
                  <div className={darkMode ? "text-slate-200" : "text-slate-800"}>
                    <div
                      className={`rounded-2xl border p-6 shadow-sm ${
                        darkMode
                          ? "border-[#2A2E3A] bg-[#0A0A12]"
                          : "border-[#E7E2F5] bg-[#F6F3FB]"
                      }`}
                    >
                      <div
                        className={`space-y-5 
                        [&_h1]:mb-4 [&_h1]:text-2xl [&_h1]:font-bold
                        [&_h2]:mb-3 [&_h2]:mt-7 [&_h2]:text-xl [&_h2]:font-bold
                        [&_h3]:mt-5 [&_h3]:text-lg [&_h3]:font-semibold
                        [&_p]:text-sm [&_p]:leading-7
                        [&_ul]:list-disc [&_ul]:pl-6 [&_li]:mb-2 [&_li]:text-sm`}
                      >
                        <ReactMarkdown>
                          {selectedMeeting.summary || "No summary available."}
                        </ReactMarkdown>
                      </div>
                    </div>

                    <div className="mt-6 grid gap-5 md:grid-cols-3">
                      <InfoCard
                        darkMode={darkMode}
                        title="Action Items"
                        icon="✅"
                        items={selectedMeeting.action_items}
                      />
                      <InfoCard
                        darkMode={darkMode}
                        title="Key Decisions"
                        icon="🎯"
                        items={selectedMeeting.key_decisions}
                      />
                      <InfoCard
                        darkMode={darkMode}
                        title="Open Questions"
                        icon="❓"
                        items={selectedMeeting.open_questions}
                      />
                    </div>
                  </div>
                )}

                {activeView === "transcript" && (
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-7">
                    {selectedMeeting.transcript}
                  </pre>
                )}

                <div
                  className={`mt-8 rounded-2xl border p-5 ${
                    darkMode ? "border-[#2A2E3A] bg-[#0A0A12]" : "border-[#E7E2F5] bg-[#F6F3FB]"
                  }`}
                >
                  <h2 className="mb-4 text-lg font-bold">
                    Chat about this meeting
                  </h2>

                  <div className="space-y-5">
                    {chats.length === 0 ? (
                      <p className="text-sm text-slate-500">
                        Ask your first question about this meeting.
                      </p>
                    ) : (
                      chats.map((chat) => (
                        <div key={chat.id} className="space-y-3">
                          <div className="ml-auto max-w-[72%] rounded-2xl bg-gradient-to-r from-[#7C4DFF] to-[#B355FF] px-5 py-3 text-sm leading-6 text-white">
                            <p className="mb-1 text-xs text-white/70">You</p>
                            {chat.question}
                          </div>

                          <div
                            className={`max-w-[78%] rounded-2xl px-5 py-4 text-sm leading-7 ${
                              darkMode
                                ? "bg-[#12151D] text-slate-100"
                                : "bg-white text-slate-800"
                            }`}
                          >
                            <p className="mb-1 text-xs font-semibold text-[#B355FF]">
                              LensAI
                            </p>
                            {chat.answer}
                          </div>
                        </div>
                      ))
                    )}

                    {asking && (
                      <div
                        className={`max-w-[78%] rounded-2xl px-5 py-4 text-sm ${
                          darkMode
                            ? "bg-[#12151D] text-slate-100"
                            : "bg-white text-slate-800"
                        }`}
                      >
                        <p className="mb-1 text-xs font-semibold text-[#B355FF]">
                          LensAI
                        </p>
                        Thinking<span className="animate-pulse">...</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-5 flex items-center gap-3">
                    <button
                      onClick={handleAskQuestion}
                      disabled={!question.trim() || asking}
                      className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] text-white shadow-md transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
                      title="Send"
                    >
                      {asking ? "..." : "➤"}
                    </button>

                    <input
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleAskQuestion();
                        }
                      }}
                      placeholder="Ask questions about this meeting..."
                      className={`flex-1 rounded-xl border px-4 py-3 text-sm outline-none transition ${
                        darkMode
                          ? "border-[#2A2E3A] bg-[#12151D] text-white placeholder:text-slate-500 focus:border-[#7C4DFF]"
                          : "border-[#E7E2F5] bg-white text-slate-900 placeholder:text-slate-500 shadow-sm focus:border-[#7C4DFF] focus:ring-2 focus:ring-[#7C4DFF]/20"
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function InfoCard({ darkMode, title, icon, items }) {
  let parsedItems = [];

  if (Array.isArray(items)) {
    parsedItems = items;
  } else if (typeof items === "string") {
    try {
      parsedItems = JSON.parse(items);
    } catch {
      parsedItems = items ? [items] : [];
    }
  }

  return (
    <div
      className={`rounded-2xl border p-5 shadow-sm ${
        darkMode
          ? "border-[#2A2E3A] bg-[#12151D]"
          : "border-[#E7E2F5] bg-white"
      }`}
    >
      <div className="mb-4 flex items-center gap-2">
        <span>{icon}</span>
        <h3 className="font-bold">{title}</h3>
      </div>

      {parsedItems.length === 0 ? (
        <p className="text-sm text-slate-500">None</p>
      ) : (
        <ul className="space-y-2 text-sm leading-6">
          {parsedItems.map((item, index) => (
            <li key={index}>• {item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Dashboard;