"""journal-gui: desktop client, Tkinter, no external dependencies."""

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

sys_path = str(Path(__file__).resolve().parent.parent.parent)
import sys

if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from journal.core import (  # noqa: E402
    append_entry,
    day_count,
    load_credentials,
    login_or_register,
    read_entries,
    read_entries_parsed,
    save_credentials,
    sync_push,
)

DEFAULT_FILE = os.environ.get("JOURNAL_FILE", "journal.md")
DEFAULT_API = os.environ.get("JOURNAL_API", "http://127.0.0.1:8000")

BG = "#f4f4f0"
FG = "#000000"
ACCENT = "#000000"
PANEL = "#ffffff"
FONT = ("JetBrains Mono", 10)
FONT_H = ("JetBrains Mono", 13, "bold")


class JournalGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("journal — desktop")
        self.geometry("720x560")
        self.configure(bg=BG)

        self.file = DEFAULT_FILE
        self.api = DEFAULT_API
        self.credentials = None

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
        self.login_frame = tk.Frame(self, bg=BG, padx=48, pady=40)
        tk.Label(self.login_frame, text="journal/ login", bg=BG, fg=FG,
                 font=FONT_H).pack(anchor="w")
        tk.Label(self.login_frame, text="server", bg=BG, fg=FG,
                 font=FONT).pack(anchor="w", pady=(18, 2))
        self.var_server = tk.StringVar(value=DEFAULT_API)
        tk.Entry(self.login_frame, textvariable=self.var_server, font=FONT,
                 bg=PANEL, relief="solid", bd=2).pack(fill="x")
        tk.Label(self.login_frame, text="username", bg=BG, fg=FG,
                 font=FONT).pack(anchor="w", pady=(10, 2))
        self.var_user = tk.StringVar()
        tk.Entry(self.login_frame, textvariable=self.var_user, font=FONT,
                 bg=PANEL, relief="solid", bd=2).pack(fill="x")
        tk.Label(self.login_frame, text="password", bg=BG, fg=FG,
                 font=FONT).pack(anchor="w", pady=(10, 2))
        self.var_pass = tk.StringVar()
        tk.Entry(self.login_frame, textvariable=self.var_pass, show="•",
                 font=FONT, bg=PANEL, relief="solid", bd=2).pack(fill="x")
        row = tk.Frame(self.login_frame, bg=BG)
        row.pack(fill="x", pady=(16, 0))
        tk.Button(row, text="login", command=lambda: self._auth(False),
                  bg=ACCENT, fg="#fff", font=FONT, relief="flat",
                  activebackground=ACCENT).pack(side="left")
        tk.Button(row, text="register", command=lambda: self._auth(True),
                  bg=PANEL, fg=FG, font=FONT, relief="solid", bd=2,
                  activebackground=PANEL).pack(side="left", padx=(10, 0))
        tk.Button(row, text="work offline", command=self._show_main,
                  bg=PANEL, fg=FG, font=FONT, relief="solid", bd=2,
                  activebackground=PANEL).pack(side="right")

    def _build_main(self):
        self.main_frame = tk.Frame(self, bg=BG)
        bar = tk.Frame(self.main_frame, bg=PANEL, relief="solid", bd=2)
        bar.pack(fill="x", padx=12, pady=(12, 8))
        self.lbl_user = tk.Label(bar, text="local only", bg=PANEL, fg=FG,
                                 font=FONT)
        self.lbl_user.pack(side="left", padx=10)
        tk.Button(bar, text="sync", command=self._sync, bg=ACCENT, fg="#fff",
                  font=FONT, relief="flat").pack(side="right", padx=6, pady=4)
        tk.Button(bar, text="logout", command=self._logout, bg=PANEL, fg=FG,
                  font=FONT, relief="solid", bd=2).pack(side="right", padx=6, pady=4)

        compose = tk.Frame(self.main_frame, bg=BG)
        compose.pack(fill="x", padx=12, pady=6)
        self.var_entry = tk.StringVar()
        tk.Entry(compose, textvariable=self.var_entry, font=FONT, bg=PANEL,
                 relief="solid", bd=2).pack(side="left", fill="x", expand=True)
        tk.Button(compose, text="add", command=self._add, bg=ACCENT, fg="#fff",
                  font=FONT, relief="flat").pack(side="left", padx=(8, 0))

        self.lbl_stats = tk.Label(self.main_frame, text="0 entries · 0 days",
                                  bg=BG, fg=FG, font=FONT)
        self.lbl_stats.pack(anchor="w", padx=14, pady=(4, 6))

        self.list = tk.Listbox(self.main_frame, font=FONT, bg=PANEL,
                               relief="solid", bd=2, selectmode="single")
        self.list.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.list.bind("<Double-Button-1>", lambda e: self._delete_selected())

    def _show_login(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def _show_main(self):
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
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
        try:
            token = login_or_register(server, user, password, register=register)
        except Exception as e:
            messagebox.showerror("journal", f"auth failed: {e}")
            return
        save_credentials(server, user, token)
        self.credentials = {"username": user, "token": token}
        self._show_main()

    def _logout(self):
        self.credentials = None
        self.var_pass.set("")
        self._show_login()

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
            self.after(0, lambda: (self._refresh(), self._status("\n".join(msgs))))
        except Exception as e:
            self.after(0, lambda: self._status(f"sync failed: {e}"))

    def _status(self, text):
        self.lbl_stats.config(text=text)

    def _delete_selected(self):
        sel = self.list.curselection()
        if not sel:
            return
        entry = self._entries[sel[0]]
        path = Path(self.file)
        lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                 if not l.startswith(f"- {entry['created_at']} ")]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        self._refresh()

    def _refresh(self):
        parsed = read_entries_parsed(self.file)
        self._entries = parsed
        self.list.delete(0, "end")
        for e in parsed:
            self.list.insert("end", f"  {e['created_at'][:19]}  {e['body'][:60]}")
        days = day_count(self.file)
        who = self.credentials["username"] if self.credentials else "local only"
        self.lbl_user.config(text=who)
        self.lbl_stats.config(
            text=f"{len(parsed)} entries · {days} days · file: {self.file}"
        )


def main():
    JournalGui().mainloop()


if __name__ == "__main__":
    main()
