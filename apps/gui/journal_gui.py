"""journal-gui: desktop client, Tkinter, no external dependencies."""

import json
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

sys_path = str(Path(__file__).resolve().parent.parent.parent)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from journal.core import (  # noqa: E402
    append_entry,
    day_count,
    load_credentials,
    login_or_register,
    read_entries_parsed,
    save_credentials,
    sync_push,
)

DEFAULT_FILE = os.environ.get("JOURNAL_FILE", "journal.md")
DEFAULT_API = os.environ.get("JOURNAL_API", "http://127.0.0.1:8000")

BG = "#f4f4f0"
FG = "#000000"
PANEL = "#ffffff"
MUTED = "#3a3a38"
SHADOW = "#000000"
FONT = ("JetBrains Mono", 10)
FONT_SM = ("JetBrains Mono", 8)
FONT_H = ("JetBrains Mono", 14, "bold")


def _pill(parent, text, command, solid=False, **kw):
    b = tk.Button(
        parent,
        text=text,
        command=command,
        bg=(FG if solid else PANEL),
        fg=(PANEL if solid else FG),
        font=FONT_SM,
        relief="flat",
        padx=10,
        pady=4,
        cursor="hand2",
        highlightthickness=2,
        highlightbackground=FG,
        **kw,
    )
    b._solid = solid
    return b


class JournalGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("journal — desktop")
        self.geometry("860x620")
        self.minsize(620, 460)
        self.configure(bg=BG)

        self.file = DEFAULT_FILE
        self.api = DEFAULT_API
        self.credentials = None
        self._entries = []

        self._build_login()
        self._build_main()

        creds = self._load_any_credentials()
        if creds:
            self.api = list(creds)[0]
            self.credentials = creds[self.api]
            self._show_main()
        else:
            self._show_login()

    # ------------------------------------------------------------------ UI
    def _build_login(self):
        self.login_frame = tk.Frame(self, bg=BG)
        card = tk.Frame(self.login_frame, bg=PANEL, highlightthickness=3,
                        highlightbackground=FG)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=430)

        pad = tk.Frame(card, bg=PANEL)
        pad.pack(fill="both", expand=True, padx=34, pady=30)

        tk.Label(pad, text="journal/", bg=PANEL, fg=FG,
                 font=FONT_H).pack(anchor="w")
        tk.Label(pad, text="login or register · one account, every device",
                 bg=PANEL, fg=MUTED, font=FONT_SM).pack(anchor="w", pady=(2, 20))

        tk.Label(pad, text="server", bg=PANEL, fg=FG, font=FONT_SM).pack(anchor="w")
        self.var_server = tk.StringVar(value=DEFAULT_API)
        tk.Entry(pad, textvariable=self.var_server, font=FONT,
                 bg=BG, relief="flat", highlightthickness=2,
                 highlightbackground=FG).pack(fill="x", pady=(3, 12))

        tk.Label(pad, text="username", bg=PANEL, fg=FG, font=FONT_SM).pack(anchor="w")
        self.var_user = tk.StringVar()
        tk.Entry(pad, textvariable=self.var_user, font=FONT,
                 bg=BG, relief="flat", highlightthickness=2,
                 highlightbackground=FG).pack(fill="x", pady=(3, 12))

        tk.Label(pad, text="password", bg=PANEL, fg=FG, font=FONT_SM).pack(anchor="w")
        self.var_pass = tk.StringVar()
        pass_entry = tk.Entry(pad, textvariable=self.var_pass, show="•",
                              font=FONT, bg=BG, relief="flat", highlightthickness=2,
                              highlightbackground=FG)
        pass_entry.pack(fill="x", pady=(3, 18))
        pass_entry.bind("<Return>", lambda e: self._auth(False))

        row = tk.Frame(pad, bg=PANEL)
        row.pack(fill="x")
        _pill(row, "login", lambda: self._auth(False), solid=True).pack(side="left")
        _pill(row, "register", lambda: self._auth(True)).pack(side="left", padx=(8, 0))
        _pill(row, "work offline", self._show_main).pack(side="right")

        self.lbl_auth = tk.Label(pad, text="", bg=PANEL, fg=MUTED,
                                 font=FONT_SM, justify="left", wraplength=300)
        self.lbl_auth.pack(anchor="w", pady=(16, 0))

    def _build_main(self):
        self.main_frame = tk.Frame(self, bg=BG)

        bar = tk.Frame(self.main_frame, bg=PANEL, highlightthickness=2,
                       highlightbackground=FG)
        bar.pack(fill="x", padx=14, pady=(14, 8))
        self.lbl_user = tk.Label(bar, text="local only", bg=PANEL, fg=FG, font=FONT)
        self.lbl_user.pack(side="left", padx=12)
        _pill(bar, "sync", self._sync, solid=True).pack(side="right", padx=6, pady=4)
        _pill(bar, "open…", self._pick_file).pack(side="right", padx=6, pady=4)
        _pill(bar, "logout", self._logout).pack(side="right", padx=6, pady=4)

        compose = tk.Frame(self.main_frame, bg=BG)
        compose.pack(fill="x", padx=14, pady=6)
        self.var_entry = tk.StringVar()
        entry = tk.Entry(compose, textvariable=self.var_entry, font=FONT, bg=PANEL,
                         relief="flat", highlightthickness=2, highlightbackground=FG)
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.bind("<Return>", lambda e: self._add())
        _pill(compose, "add", self._add, solid=True).pack(side="left", padx=(8, 0))

        self.lbl_stats = tk.Label(self.main_frame, text="", bg=BG, fg=MUTED,
                                  font=FONT_SM)
        self.lbl_stats.pack(anchor="w", padx=16, pady=(6, 6))

        self.list = tk.Listbox(self.main_frame, font=FONT, bg=PANEL,
                               relief="flat", highlightthickness=2,
                               highlightbackground=FG, selectmode="single",
                               activestyle="none", bd=0)
        self.list.pack(fill="both", expand=True, padx=14, pady=(0, 6))
        self.list.bind("<Double-Button-1>", lambda e: self._delete_selected())
        self.list.bind("<Delete>", lambda e: self._delete_selected())
        self.list.bind("<Return>", lambda e: self._delete_selected())

        bottom = tk.Frame(self.main_frame, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(0, 10))
        self.lbl_file = tk.Label(bottom, text="", bg=BG, fg=MUTED, font=FONT_SM)
        self.lbl_file.pack(side="left")
        self.lbl_conn = tk.Label(bottom, text="", bg=BG, fg=MUTED, font=FONT_SM)
        self.lbl_conn.pack(side="right")

    def _show_login(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def _show_main(self):
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.lbl_auth.config(text="")
        self._refresh()

    # ------------------------------------------------------------ actions
    def _load_any_credentials(self):
        path = Path("~/.config/journal/credentials.json").expanduser()
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except Exception:
            return None

    def _auth(self, register):
        server = self.var_server.get().strip().rstrip("/")
        user = self.var_user.get().strip()
        password = self.var_pass.get()
        if not server or not user or len(password) < 8:
            messagebox.showerror("journal", "server, username and a password "
                                  "of 8+ chars are required")
            return
        self.api = server
        self.lbl_auth.config(text="connecting…")
        try:
            token = login_or_register(server, user, password, register=register)
        except Exception as e:
            self.lbl_auth.config(text="")
            messagebox.showerror("journal", f"auth failed: {e}")
            return
        save_credentials(server, user, token)
        self.credentials = {"username": user, "token": token}
        self._show_main()

    def _logout(self):
        self.credentials = None
        self.var_pass.set("")
        self._show_login()

    def _pick_file(self):
        p = filedialog.asksaveasfilename(
            title="journal file", defaultextension=".md",
            initialfile=Path(self.file).name)
        if p:
            self.file = p
            self._refresh()

    def _add(self):
        text = self.var_entry.get().strip()
        if not text:
            return
        append_entry(self.file, text)
        self.var_entry.set("")
        if self.credentials:
            self._push_async()
        else:
            self._refresh()

    def _sync(self):
        if not self.credentials:
            messagebox.showinfo("journal", "not logged in — using local file only")
            return
        self._sync_async()

    def _push_async(self):
        threading.Thread(target=self._do_sync, args=(False, True), daemon=True).start()

    def _sync_async(self):
        threading.Thread(target=self._do_sync, args=(True, True), daemon=True).start()

    def _do_sync(self, pull, push):
        try:
            msgs = sync_push(pull, push, self.file, self.api, self.credentials["token"])
            self.after(0, lambda: (self._refresh(),
                                   self._status("\n".join(msgs))))
        except Exception as e:
            self.after(0, lambda: self._status(f"sync failed: {e}"))

    def _status(self, text):
        self.lbl_stats.config(text=text)

    def _delete_selected(self):
        sel = self.list.curselection()
        if not sel:
            return
        entry = self._entries[sel[0]]
        if not messagebox.askyesno("journal", f"delete entry?\n\n{entry['body'][:120]}"):
            return
        path = Path(self.file)
        lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                 if not l.startswith(f"- {entry['created_at']} ")]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        self._refresh()

    def _fmt_day(self, iso):
        try:
            import datetime
            d = datetime.date.fromisoformat(iso[:10])
            if d == datetime.date.today():
                return "today"
            if d == datetime.date.today() - datetime.timedelta(days=1):
                return "yesterday"
            return d.strftime("%b %d, %Y")
        except Exception:
            return iso[:10]

    def _refresh(self):
        parsed = read_entries_parsed(self.file)
        self._entries = parsed
        self.list.delete(0, "end")
        last_day = None
        for e in parsed:
            day = e["created_at"][:10]
            if day != last_day:
                last_day = day
                self.list.insert("end", f"  ── {self._fmt_day(day)} ──────────")
                self.list.itemconfig("end", fg=MUTED, selectbackground=BG,
                                     selectforeground=MUTED)
            t = e["created_at"][11:16]
            self.list.insert("end", f"  {t}  {e['body']}")
        days = day_count(self.file)
        who = self.credentials["username"] if self.credentials else "local only"
        self.lbl_user.config(text=f"  {who}")
        self.lbl_stats.config(
            text=f"{len(parsed)} entries · {days} days"
        )
        self.lbl_file.config(text=Path(self.file).name)
        if self.credentials:
            self.lbl_conn.config(text="synced" if True else "")
            self.lbl_conn.config(text="· online")
        else:
            self.lbl_conn.config(text="· local only")


def main():
    JournalGui().mainloop()


if __name__ == "__main__":
    main()
