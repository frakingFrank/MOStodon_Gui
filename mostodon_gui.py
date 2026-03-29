#!/usr/bin/env python3
"""
MOStodon GUI Launcher
---------------------
Startet MOStodon mit einer grafischen Oberfläche im C64-Stil.
Speichert Konfiguration in ~/.mostodon_config.json
"""

import os
import sys
import json
import subprocess
import re
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
import queue

CONFIG_FILE = os.path.expanduser("~/.mostodon_config.json")

# C64-Farben
C64_BLUE   = "#4040e8"
C64_LBLUE  = "#7878f8"
C64_BG     = "#0000a8"
C64_TEXT   = "#aaaaff"
C64_WHITE  = "#ffffff"
C64_YELLOW = "#f8f878"
C64_GREEN  = "#70a870"
C64_RED    = "#f87878"
C64_BORDER = "#3535c8"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_local_ips():
    ips = []
    try:
        result = subprocess.run(["ip", "-4", "addr"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet ") and "127.0.0.1" not in line and "122." not in line \
               and "172." not in line and "100." not in line:
                ip = line.split()[1].split("/")[0]
                hint = ""
                if "wlp" in line or "wlan" in line:
                    hint = "WLAN"
                elif "enx" in line or "eth" in line or "enp" in line:
                    hint = "LAN"
                ips.append((ip, hint))
    except Exception:
        pass
    return ips


def find_mostodon():
    candidates = [
        os.path.expanduser("~/Programme/MOStodon/MOStodon-main/MOStodon.py"),
        os.path.expanduser("~/Downloads/MOStodon-main/MOStodon.py"),
        os.path.expanduser("~/MOStodon-main/MOStodon.py"),
        os.path.expanduser("~/MOStodon/MOStodon.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


class MOStodonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MOStodon Launcher")
        self.root.configure(bg=C64_BG)
        self.root.resizable(False, False)

        self.config = load_config()
        self.server_process = None
        self.log_queue = queue.Queue()
        self.running = False

        self._build_ui()
        self._load_config_into_ui()
        self._refresh_ips()
        self._poll_log()

    def _build_ui(self):
        root = self.root

        # Äußerer Rahmen (C64-Bordüre)
        outer = tk.Frame(root, bg=C64_BORDER, padx=8, pady=8)
        outer.pack(padx=0, pady=0)

        inner = tk.Frame(outer, bg=C64_BG, padx=16, pady=12)
        inner.pack()

        # Titel
        tk.Label(inner, text="* MOStodon Launcher *",
                 font=("Courier", 18, "bold"),
                 fg=C64_WHITE, bg=C64_BG).grid(row=0, column=0, columnspan=3, pady=(0, 4))

        tk.Label(inner, text="C64 MASTODON CLIENT",
                 font=("Courier", 9),
                 fg=C64_LBLUE, bg=C64_BG).grid(row=1, column=0, columnspan=3, pady=(0, 14))

        # --- Pfad zu MOStodon.py ---
        self._section(inner, "PROGRAMM-PFAD", row=2)

        tk.Label(inner, text="MOStodon.py:", font=("Courier", 10),
                 fg=C64_TEXT, bg=C64_BG, anchor="w").grid(row=3, column=0, sticky="w", pady=2)

        self.path_var = tk.StringVar()
        path_entry = tk.Entry(inner, textvariable=self.path_var, width=38,
                              font=("Courier", 10), bg=C64_BLUE, fg=C64_WHITE,
                              insertbackground=C64_WHITE, relief="flat", bd=4)
        path_entry.grid(row=3, column=1, padx=6, pady=2)

        tk.Button(inner, text="...", font=("Courier", 10, "bold"),
                  bg=C64_LBLUE, fg=C64_BG, activebackground=C64_WHITE,
                  relief="flat", bd=0, padx=6,
                  command=self._browse_path).grid(row=3, column=2, pady=2)

        # --- Mastodon-Konfiguration ---
        self._section(inner, "MASTODON", row=4)

        tk.Label(inner, text="Instanz:", font=("Courier", 10),
                 fg=C64_TEXT, bg=C64_BG, anchor="w").grid(row=5, column=0, sticky="w", pady=2)
        self.url_var = tk.StringVar(value="https://norden.social")
        tk.Entry(inner, textvariable=self.url_var, width=38,
                 font=("Courier", 10), bg=C64_BLUE, fg=C64_WHITE,
                 insertbackground=C64_WHITE, relief="flat", bd=4).grid(row=5, column=1, columnspan=2, padx=6, pady=2, sticky="w")

        tk.Label(inner, text="Token:", font=("Courier", 10),
                 fg=C64_TEXT, bg=C64_BG, anchor="w").grid(row=6, column=0, sticky="w", pady=2)
        self.token_var = tk.StringVar()
        self.token_entry = tk.Entry(inner, textvariable=self.token_var, width=38,
                                    font=("Courier", 10), bg=C64_BLUE, fg=C64_WHITE,
                                    insertbackground=C64_WHITE, relief="flat", bd=4, show="*")
        self.token_entry.grid(row=6, column=1, padx=6, pady=2)

        self.show_token = tk.BooleanVar(value=False)
        tk.Checkbutton(inner, text="zeigen", variable=self.show_token,
                       font=("Courier", 9), fg=C64_TEXT, bg=C64_BG,
                       selectcolor=C64_BLUE, activebackground=C64_BG,
                       command=self._toggle_token).grid(row=6, column=2, pady=2)

        # --- Netzwerk ---
        self._section(inner, "NETZWERK", row=7)

        self.ip_label = tk.Label(inner, text="", font=("Courier", 10),
                                  fg=C64_YELLOW, bg=C64_BG, justify="left", anchor="w")
        self.ip_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=2)

        tk.Button(inner, text="IP aktualisieren", font=("Courier", 9),
                  bg=C64_BORDER, fg=C64_TEXT, activebackground=C64_LBLUE,
                  relief="flat", bd=0, padx=8, pady=2,
                  command=self._refresh_ips).grid(row=9, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # --- Buttons ---
        btn_frame = tk.Frame(inner, bg=C64_BG)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=8)

        self.start_btn = tk.Button(btn_frame, text="▶  SERVER STARTEN",
                                   font=("Courier", 12, "bold"),
                                   bg=C64_GREEN, fg=C64_BG,
                                   activebackground=C64_WHITE,
                                   relief="flat", bd=0, padx=16, pady=8,
                                   command=self._start)
        self.start_btn.pack(side="left", padx=6)

        self.stop_btn = tk.Button(btn_frame, text="■  STOPPEN",
                                  font=("Courier", 12, "bold"),
                                  bg=C64_RED, fg=C64_BG,
                                  activebackground=C64_WHITE,
                                  relief="flat", bd=0, padx=16, pady=8,
                                  state="disabled",
                                  command=self._stop)
        self.stop_btn.pack(side="left", padx=6)

        # --- Log ---
        self._section(inner, "SERVER-LOG", row=11)

        self.log = scrolledtext.ScrolledText(inner, width=58, height=10,
                                              font=("Courier", 9),
                                              bg="#000030", fg=C64_TEXT,
                                              insertbackground=C64_WHITE,
                                              relief="flat", bd=4,
                                              state="disabled")
        self.log.grid(row=12, column=0, columnspan=3, pady=4)

        # Status
        self.status_var = tk.StringVar(value="READY.")
        tk.Label(inner, textvariable=self.status_var,
                 font=("Courier", 10, "bold"),
                 fg=C64_YELLOW, bg=C64_BG).grid(row=13, column=0, columnspan=3, pady=(4, 0))

    def _section(self, parent, title, row):
        tk.Label(parent, text=f" {title} ",
                 font=("Courier", 9, "bold"),
                 fg=C64_BG, bg=C64_LBLUE).grid(row=row, column=0, columnspan=3,
                                                sticky="w", pady=(10, 2))

    def _load_config_into_ui(self):
        path = self.config.get("mostodon_py", find_mostodon())
        self.path_var.set(path)
        self.url_var.set(self.config.get("api_base_url", "MASTODON-SERVER"))
        self.token_var.set(self.config.get("access_token", ""))

    def _toggle_token(self):
        self.token_entry.config(show="" if self.show_token.get() else "*")

    def _browse_path(self):
        path = filedialog.askopenfilename(
            title="MOStodon.py auswählen",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if path:
            self.path_var.set(path)

    def _refresh_ips(self):
        ips = get_local_ips()
        if ips:
            lines = []
            for ip, hint in ips:
                lines.append(f"atdt{ip}:6502  [{hint}]")
            self.ip_label.config(text="\n".join(lines))
        else:
            self.ip_label.config(text="(Keine IP gefunden)")

    def _save_and_patch(self):
        mostodon_py = self.path_var.get().strip()
        api_base_url = self.url_var.get().strip()
        access_token = self.token_var.get().strip()

        if not os.path.exists(mostodon_py):
            self._log(f"FEHLER: Datei nicht gefunden: {mostodon_py}", color=C64_RED)
            return None, None

        if not access_token:
            self._log("FEHLER: Kein Access Token eingegeben!", color=C64_RED)
            return None, None

        if not api_base_url.startswith("http"):
            api_base_url = "https://" + api_base_url

        # Konfiguration speichern
        self.config["mostodon_py"] = mostodon_py
        self.config["api_base_url"] = api_base_url
        self.config["access_token"] = access_token
        save_config(self.config)
        self._log("Konfiguration gespeichert.")

        # MOStodon.py patchen
        with open(mostodon_py, "r") as f:
            content = f.read()
        content = re.sub(r'access_token\s*=\s*"[^"]*"',
                         f'access_token = "{access_token}"', content)
        content = re.sub(r'api_base_url\s*=\s*"[^"]*"',
                         f'api_base_url = "{api_base_url}"', content)
        with open(mostodon_py, "w") as f:
            f.write(content)
        self._log("MOStodon.py aktualisiert.")

        mostodon_dir = os.path.dirname(mostodon_py)
        return mostodon_py, mostodon_dir

    def _ensure_venv(self, mostodon_dir):
        venv_dir = os.path.join(mostodon_dir, "venv")
        pip = os.path.join(venv_dir, "bin", "pip")
        python = os.path.join(venv_dir, "bin", "python")
        requirements = os.path.join(mostodon_dir, "requirements.txt")

        if not os.path.exists(python):
            self._log("Erstelle venv...")
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            self._log("venv erstellt.")

        self._log("Installiere Abhängigkeiten...")
        subprocess.run([pip, "install", "-q", "-r", requirements], check=True)
        self._log("Pakete OK.")
        return python

    def _start(self):
        self._log("=" * 40)
        mostodon_py, mostodon_dir = self._save_and_patch()
        if not mostodon_py:
            return

        def run():
            try:
                python = self._ensure_venv(mostodon_dir)
                self._log("Server wird gestartet...\n")
                self.running = True
                self.root.after(0, self._update_buttons)

                self.server_process = subprocess.Popen(
                    [python, mostodon_py],
                    cwd=mostodon_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                for line in self.server_process.stdout:
                    self.log_queue.put(("normal", line.rstrip()))

                self.server_process.wait()
                self.log_queue.put(("yellow", "Server beendet."))
                self.running = False
                self.root.after(0, self._update_buttons)

            except Exception as e:
                self.log_queue.put(("red", f"FEHLER: {e}"))
                self.running = False
                self.root.after(0, self._update_buttons)

        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        if self.server_process:
            self.server_process.terminate()
            self._log("Server gestoppt.", color=C64_YELLOW)
        self.running = False
        self._update_buttons()

    def _update_buttons(self):
        if self.running:
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_var.set("SERVER LAEUFT...")
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_var.set("READY.")

    def _log(self, text, color=None):
        self.log_queue.put((color or "normal", text))

    def _poll_log(self):
        color_map = {
            "normal": C64_TEXT,
            "red":    C64_RED,
            "yellow": C64_YELLOW,
            "green":  C64_GREEN,
        }
        try:
            while True:
                kind, text = self.log_queue.get_nowait()
                self.log.config(state="normal")
                color = color_map.get(kind, C64_TEXT)
                tag = f"col_{kind}"
                self.log.tag_config(tag, foreground=color)
                self.log.insert("end", text + "\n", tag)
                self.log.see("end")
                self.log.config(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log)


def main():
    # Prüfen ob tkinter verfügbar
    try:
        root = tk.Tk()
    except Exception:
        print("FEHLER: tkinter nicht verfügbar.")
        print("Installieren mit: sudo apt install python3-tk")
        sys.exit(1)

    app = MOStodonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
