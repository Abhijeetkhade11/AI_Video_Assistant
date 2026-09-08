import lensLogo from "../assets/lenslogo.png";

function Sidebar({
  user,
  darkMode,
  logout,
  meetings,
  selectedMeeting,
  onNewMeeting,
  onSelectMeeting,
  onSelectChat,
  onDeleteMeeting,
  onRenameMeeting,
  searchQuery,
  setSearchQuery,
}) {
  const initials = user?.name
    ? user.name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "U";

  return (
    <aside
      className={`flex h-screen w-72 flex-col border-r p-5 ${
        darkMode
          ? "border-[#2A2E3A] bg-[#0B0E14] text-[#F5F3FF]"
          : "border-[#E7E2F5] bg-[#FBFAFF] text-[#1B1B2A]"
      }`}
    >
      <div className="mb-6 flex items-center gap-3">
        <img
          src={lensLogo}
          alt="LensAI"
          className="h-10 w-10 rounded-xl object-cover shadow-sm"
        />

        <div>
          <h1 className="font-bold">
            Lens<span className="text-[#B355FF]">AI</span>
          </h1>
          <p className="text-[11px] uppercase tracking-wide text-slate-500">
            Meeting workspace
          </p>
        </div>
      </div>

      <button
        onClick={onNewMeeting}
        className="mb-6 rounded-lg bg-gradient-to-r from-[#7C4DFF] to-[#FF7A59] px-4 py-3 text-left text-sm font-semibold text-white shadow-[0_0_20px_rgba(124,77,255,0.25)] transition hover:brightness-110"
      >
        + New Meeting
      </button>

      <input
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search meetings..."
        className={`mb-6 w-full rounded-lg border px-4 py-2.5 text-sm outline-none transition ${
          darkMode
            ? "border-[#2A2E3A] bg-[#12151D] text-white placeholder:text-slate-500 focus:border-[#7C4DFF]"
            : "border-[#E7E2F5] bg-white text-slate-900 placeholder:text-slate-400 shadow-sm focus:border-[#7C4DFF]"
        }`}
      />

      <div className="flex-1 space-y-6 overflow-y-auto pr-1">
        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Meeting History
          </h3>

          <div className="space-y-2">
            {meetings.length === 0 ? (
              <p className="text-sm text-slate-500">No meetings yet</p>
            ) : (
              meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className={`group flex items-center gap-2 rounded-lg px-3 py-2 transition ${
                    selectedMeeting?.id === meeting.id
                      ? darkMode
                        ? "bg-[#7C4DFF]/15 text-white"
                        : "bg-[#7C4DFF]/10 text-[#1B1B2A]"
                      : darkMode
                      ? "text-slate-300 hover:bg-[#12151D]"
                      : "text-slate-700 hover:bg-white"
                  }`}
                >
                  <button
                    onClick={() => onSelectMeeting(meeting.id)}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p className="truncate text-sm font-medium">
                      {meeting.title || "Untitled Meeting"}
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(meeting.created_at).toLocaleDateString()}
                    </p>
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();

                        const newTitle = prompt(
                          "Enter new meeting title",
                          meeting.title
                        );

                        if (!newTitle?.trim()) return;

                        onRenameMeeting(meeting.id, newTitle);
                      }}
                      className={`opacity-0 transition group-hover:opacity-100 ${
                        darkMode ? "text-[#B355FF]" : "text-[#7C4DFF]"
                      }`}
                      title="Rename meeting"
                    >
                      ✏️
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteMeeting(meeting.id);
                      }}
                      className={`opacity-0 transition group-hover:opacity-100 ${
                        darkMode ? "text-[#FF9D82]" : "text-[#FF7A59]"
                      }`}
                      title="Delete meeting"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Chat History
          </h3>

          <div className="space-y-2">
            {meetings.filter((m) => m.chat_count > 0).length === 0 ? (
              <p className="text-sm text-slate-500">No chats yet</p>
            ) : (
              meetings
                .filter((meeting) => meeting.chat_count > 0)
                .map((meeting) => (
                  <button
                    key={meeting.id}
                    onClick={() => onSelectChat(meeting.id)}
                    className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                      darkMode
                        ? "text-slate-300 hover:bg-[#12151D]"
                        : "text-slate-700 hover:bg-white"
                    }`}
                  >
                    <p className="truncate font-medium">
                      {meeting.title || "Untitled Meeting"}
                    </p>
                    <p className="text-xs text-slate-500">
                      {meeting.chat_count} chats
                    </p>
                  </button>
                ))
            )}
          </div>
        </div>
      </div>

      <div
        className={`space-y-3 border-t pt-4 ${
          darkMode ? "border-[#2A2E3A]" : "border-[#E7E2F5]"
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#FF7A59] text-sm font-bold text-white">
            {initials}
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">
              {user?.name || "User"}
            </p>
            <p className="truncate text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>

        <button
          onClick={logout}
          className={`w-full rounded-lg px-3 py-2 text-left text-sm font-medium ${
            darkMode
              ? "text-[#FF9D82] hover:bg-[#FF7A59]/10"
              : "text-[#E85D3D] hover:bg-[#FF7A59]/10"
          }`}
        >
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;