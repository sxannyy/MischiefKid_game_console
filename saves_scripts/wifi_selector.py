#!/usr/bin/env python3
# Wi-Fi selector (клавиатура only)

import os, subprocess, sys, time, tkinter as tk
from tkinter import messagebox

PING_HOST = "8.8.8.8"
CONF      = "/etc/wpa_supplicant/wpa_supplicant.conf"

KEYS = [list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm"),
        list("1234567890")]

# ───────── helpers ────────────────────────────────────────────────
def has_net() -> bool:
    return subprocess.call(["ping", "-c1", "-W2", PING_HOST],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0

def scan() -> list[str]:
    out = subprocess.check_output(
        ["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
        text=True)
    return [s for s in out.splitlines() if s.strip()]

def nmcli_connect(ssid: str, pwd: str | None = None) -> bool:
    cmd = ["nmcli", "device", "wifi", "connect", ssid]
    if pwd:
        cmd += ["password", pwd]
    return subprocess.call(cmd) == 0

# ───────── GUI ────────────────────────────────────────────────────
class WiFiGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")
        self.stage = "list"   # list | kb
        self.sel = 0          # индекс выбранной сети
        self.refresh_list()
        self.root.mainloop()

    # ---------- клавиши «глобально» ----------
    def key_press(self, event):
        if self.stage == "list":
            self.list_keys(event)
        else:
            self.kb_keys(event)

    # ---------- список сетей ----------
    def refresh_list(self):
        self.nets = scan() or ["<нет сетей>"]
        self.draw_list()

    def draw_list(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.bind("<Key>", self.key_press)

        tk.Label(self.root, text="Выберите сеть",
                 fg="white", bg="black",
                 font=("Arial", 20)).pack(pady=14)

        self.labels = []
        frm = tk.Frame(self.root, bg="black"); frm.pack(expand=True)

        for i, ss in enumerate(self.nets):
            lbl = tk.Label(frm, text=ss or "<скрытая>",
                           width=32, anchor="w",
                           fg="black" if i == self.sel else "white",
                           bg="white" if i == self.sel else "black",
                           font=("Arial", 16))
            lbl.pack(pady=2, fill=tk.X)
            self.labels.append(lbl)

        info = "↑↓ выбрать  |  Enter: OK  |  Esc: выход"
        tk.Label(self.root, text=info, fg="gray",
                 bg="black", font=("Arial", 12)).pack(pady=10)

    def list_keys(self, event):
        if event.keysym == "Up":
            self.sel = (self.sel - 1) % len(self.nets)
            self.update_list()
        elif event.keysym == "Down":
            self.sel = (self.sel + 1) % len(self.nets)
            self.update_list()
        elif event.keysym in ("Return", "KP_Enter"):
            self.choose()
        elif event.keysym in ("Escape", "q"):
            self.exit(1)

    def update_list(self):
        for i, lbl in enumerate(self.labels):
            sel = i == self.sel
            lbl.config(fg="black" if sel else "white",
                       bg="white" if sel else "black")

    def choose(self):
        self.ssid = self.nets[self.sel]
        if self.ssid == "<нет сетей>":
            return
        self.stage = "kb"
        self.pwd = ""
        self.y = self.x = 0
        self.draw_kb()

    # ---------- экранная клавиатура ----------
    def draw_kb(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text=f"Пароль для {self.ssid}",
                 fg="white", bg="black",
                 font=("Arial", 20)).pack(pady=14)

        self.lbl_pwd = tk.Label(self.root, text="",
                                fg="white", bg="black",
                                font=("Arial", 18))
        self.lbl_pwd.pack(pady=8)

        self.k_labels = []
        kf = tk.Frame(self.root, bg="black"); kf.pack()
        for yi, row in enumerate(KEYS):
            rf = tk.Frame(kf, bg="black"); rf.pack()
            rr = []
            for xi, ch in enumerate(row):
                l = tk.Label(rf, text=ch,
                             width=3, height=2,
                             font=("Arial", 14),
                             relief="ridge")
                l.pack(side=tk.LEFT, padx=4, pady=4)
                rr.append(l)
            self.k_labels.append(rr)

        info = "Стрелки: навигация  |  Enter: OK  |  Backspace: ←  |  Esc: назад"
        tk.Label(self.root, text=info, fg="gray",
                 bg="black", font=("Arial", 12)).pack(pady=10)

        self.highlight()

    def kb_keys(self, event):
        if event.keysym == "Up":
            self.move(0, -1)
        elif event.keysym == "Down":
            self.move(0,  1)
        elif event.keysym == "Left":
            self.move(-1, 0)
        elif event.keysym == "Right":
            self.move( 1, 0)
        elif event.keysym == "BackSpace":
            self.back()
        elif event.keysym in ("Return", "KP_Enter"):
            self.try_connect()
        elif event.keysym in ("Escape", "q"):
            self.stage = "list"
            self.draw_list()
        elif event.char and event.char.isprintable():
            self.add_char(event.char)

    def move(self, dx, dy):
        self.y = (self.y + dy) % len(KEYS)
        self.x = (self.x + dx) % len(KEYS[self.y])
        self.highlight()

    def highlight(self):
        for yi, row in enumerate(self.k_labels):
            for xi, l in enumerate(row):
                sel = (yi, xi) == (self.y, self.x)
                l.config(fg="black" if sel else "white",
                         bg="white" if sel else "black")

    def add_char(self, ch=None):
        if ch is None:
            ch = KEYS[self.y][self.x]
        self.pwd += ch
        self.lbl_pwd.config(text="*" * len(self.pwd))

    def back(self):
        self.pwd = self.pwd[:-1]
        self.lbl_pwd.config(text="*" * len(self.pwd))

    def try_connect(self):
        if not nmcli_connect(self.ssid, self.pwd):
            messagebox.showerror("Ошибка", "Не удалось подключиться")
            self.stage = "list"
            self.refresh_list()
            return
        for _ in range(6):
            if has_net():
                self.exit(0)
            time.sleep(1)
        messagebox.showerror("Сеть", "Подключено, но интернета нет")
        self.stage = "list"
        self.refresh_list()

    # ---------- выход ----------
    def exit(self, code=0):
        self.root.destroy()
        sys.exit(code)

# ───────── авто-подключение перед GUI ─────────────────────────────
if has_net():
    sys.exit(0)

# пробуем известные сети без GUI
nets = scan()
for ss in nets:
    if nmcli_connect(ss):
        for _ in range(4):
            if has_net():
                sys.exit(0)
            time.sleep(1)

# запускаем интерфейс
WiFiGUI()
