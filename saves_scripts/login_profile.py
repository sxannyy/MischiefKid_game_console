#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────
#  Авторизация + скачивание сейвов  (клавиатура  +  гейм-пад)
# ─────────────────────────────────────────────────────────────
import os, sys, subprocess, requests, threading
from urllib.parse import urlparse, parse_qs, unquote
import evdev                       # ← приём гейм-пада
import tkinter as tk
from tkinter import messagebox

API_URL       = "http://192.168.0.105:8000"
WIFI_SELECTOR = "/home/d1sgu1sed/wifi_selector.py"
PROFILES_ROOT = os.path.expanduser("~/RetroPie/save-profiles")
CFG_PATH      = "/opt/retropie/configs/all/retroarch.cfg"

KEYS = [list("qwertyuiop"), list("asdfghjkl"),
        list("zxcvbnm"),    list("1234567890")]

# ───────── Wi-Fi перед запуском ─────────
def ensure_wifi():
    subprocess.call(["python3", WIFI_SELECTOR]) == 0 or sys.exit(1)

# ───────── подмена путей в retroarch.cfg ─
def patch_cfg(root):
    lines = [ln for ln in open(CFG_PATH)] if os.path.exists(CFG_PATH) else []
    lines = [ln for ln in lines
             if not ln.startswith(("savefile_directory",
                                   "savestate_directory",
                                   "save_profiles_current_name"))]
    lines += [
        f'save_profiles_current_name = "{os.path.basename(root)}"\n',
        f'savefile_directory         = "{root}/save-files"\n',
        f'savestate_directory        = "{root}/save-states"\n',
    ]
    with open(CFG_PATH, "w") as f: f.writelines(lines)

# ───────── гейм-пад → события Tk ─────────
class Gamepad(threading.Thread):
    MAP = {
        # D-Pad
        ("ABS_HAT0Y", -1): "<Up>",
        ("ABS_HAT0Y",  1): "<Down>",
        ("ABS_HAT0X", -1): "<Left>",
        ("ABS_HAT0X",  1): "<Right>",
        # Кнопки (универсально для Joy-Con и XBox-layout)
        ("BTN_EAST",   1): "A",         #  A  = OK
        ("BTN_SOUTH",  1): "t",         #  B  = Backspace
        ("BTN_WEST",   1): "t",         #  Y  = Backspace (у «Nintendo-B»)
        ("BTN_NORTH",  1): "f",         #  X  = Cancel / Back
        ("BTN_START",  1): "<Return>",  #  Start = OK
        ("BTN_SELECT", 1): "q"          #  Select = Quit
    }
    def __init__(self, root):
        super().__init__(daemon=True)
        self.root = root
        self.dev  = self._find()
        if self.dev: self.start()
    def _find(self):
        for path in evdev.list_devices():
            d = evdev.InputDevice(path)
            if evdev.ecodes.BTN_SOUTH in d.capabilities().get(evdev.ecodes.EV_KEY, []):
                return d
        return None
    def run(self):
        for ev in self.dev.read_loop():
            if ev.type == evdev.ecodes.EV_KEY and (ev.code, ev.value) in self.MAP:
                tk_evt = self.MAP[(ev.code, ev.value)]
                if tk_evt == "A":                 # «A» = символ + Enter
                    self.root.event_generate("h")
                    self.root.event_generate("<Return>")
                else:
                    self.root.event_generate(tk_evt)
            elif ev.type == evdev.ecodes.EV_ABS:
                key = (evdev.ecodes.ABS[ev.code], ev.value)
                if key in self.MAP:
                    self.root.event_generate(self.MAP[key])

# ───────── GUI ─────────
class TwoFieldGUI:
    def __init__(self):
        self.prompts = ["Введите логин", "Введите токен"]
        self.vals    = ["", ""]
        self.step    = 0
        self.sel_y = self.sel_x = 0

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        Gamepad(self.root)                 # ← приём гейм-пада
        self.root.bind("<Key>", self.key_press)    # ← клавиатура

        self.lbl_prompt = tk.Label(self.root, fg="white", bg="black",
                                   font=("Arial", 20))
        self.lbl_prompt.pack(pady=14)
        self.lbl_val = tk.Label(self.root, fg="white", bg="black",
                                font=("Arial", 18))
        self.lbl_val.pack(pady=8)

        self.kf = tk.Frame(self.root, bg="black"); self.kf.pack()
        self.k_lbl = []
        for yi, row in enumerate(KEYS):
            rf=tk.Frame(self.kf,bg="black"); rf.pack()
            rr=[]
            for xi, ch in enumerate(row):
                l=tk.Label(rf,text=ch,width=3,height=2,font=("Arial",14),
                           relief="ridge")
                l.pack(side=tk.LEFT,padx=4,pady=4); rr.append(l)
            self.k_lbl.append(rr)

        instr="D-Pad  |  A/Enter: OK   |  B: Backspace   |  X / Esc / q: Выход"
        tk.Label(self.root,text=instr,fg="gray",bg="black",
                 font=("Arial",12)).pack(pady=10)

        # навигация «стрелками» (осталось с прошлых версий)
        self.root.bind("<Up>",lambda e:self.move(0,-1))
        self.root.bind("<Down>",lambda e:self.move(0,1))
        self.root.bind("<Left>",lambda e:self.move(-1,0))
        self.root.bind("<Right>",lambda e:self.move(1,0))
        self.root.bind("t",self.back)
        self.root.bind("f",lambda e:self.exit())
        self.root.bind("<Return>",self.ok)
        self.root.bind("q",lambda e:self.exit())

        self.redraw_keys(); self.update_text(); self.root.mainloop()

    # ---------- клавиатура «живой» ----------
    def key_press(self, event):
        if event.keysym in ("Escape", "q"):
            self.exit()
        elif event.keysym in ("Return", "KP_Enter"):
            self.ok(None)
        elif event.keysym == "BackSpace":
            self.back(None)
        elif event.char and event.char.isprintable():
            self.vals[self.step] += event.char.lower()
            self.update_text()

    # ---------- виртуальная клавиатура -------
    def redraw_keys(self):
        for yi,row in enumerate(self.k_lbl):
            for xi,l in enumerate(row):
                sel=(yi,xi)==(self.sel_y,self.sel_x)
                l.config(fg="black" if sel else "white",
                         bg="white" if sel else "black")
    def move(self,dx,dy):
        self.sel_y=(self.sel_y+dy)%len(KEYS)
        self.sel_x=(self.sel_x+dx)%len(KEYS[self.sel_y])
        self.redraw_keys()
    def add(self,_): self.vals[self.step]+=KEYS[self.sel_y][self.sel_x]; self.update_text()
    def back(self,_): self.vals[self.step]=self.vals[self.step][:-1]; self.update_text()
    def update_text(self):
        self.lbl_prompt.config(text=self.prompts[self.step])
        self.lbl_val.config(text=self.vals[self.step])

    # ---------- OK / Enter ----------
    def ok(self,_):
        if self.step==0:
            self.step=1; self.sel_y=self.sel_x=0
        else:
            self.submit()
        self.redraw_keys(); self.update_text()

    # ---------- HTTP ----------
    def submit(self):
        login, token = self.vals
        try:
            r=requests.post(f"{API_URL}/auth/verify",
                            json={"username":login,"token":token},timeout=8)
        except Exception as e:
            messagebox.showerror("Сеть",str(e)); return
        if r.status_code!=200:
            messagebox.showerror("Ошибка",r.json().get("detail","bad")); return

        link=r.json().get("save_link","")
        prof_root=os.path.join(PROFILES_ROOT,login)
        os.makedirs(f"{prof_root}/save-files",exist_ok=True)
        os.makedirs(f"{prof_root}/save-states",exist_ok=True)
        patch_cfg(prof_root)

        if link:
            qs=parse_qs(urlparse(link).query)
            orig=unquote(qs.get("orig",[""])[0]) or "save.srm"
            dest=os.path.join(prof_root,"save-files",orig)
            try:
                data=requests.get(link,timeout=20).content
                open(dest,"wb").write(data)
            except Exception as e:
                messagebox.showwarning("Скачивание",str(e))
        messagebox.showinfo("OK","Профиль активирован"); self.exit(0)
    def exit(self,code=0): self.root.destroy(); sys.exit(code)

# ─────────────────────────────────────────────────────────────
if __name__=="__main__":
    ensure_wifi()
    TwoFieldGUI()
