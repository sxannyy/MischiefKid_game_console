#!/usr/bin/env python3
import os, sys, glob, subprocess, requests, tkinter as tk
from tkinter import messagebox

API_URL       = "http://192.168.0.105:8000"
WIFI_SELECTOR = "/home/d1sgu1sed/wifi_selector.py"
CFG_PATH      = "/opt/retropie/configs/all/retroarch.cfg"
KEYS = [list("qwertyuiop"), list("asdfghjkl"),
        list("zxcvbnm"),    list("1234567890")]

def ensure_wifi():
    subprocess.call(["python3", WIFI_SELECTOR]) == 0 or sys.exit(1)

def active_profile():
    for ln in open(CFG_PATH):
        if ln.startswith("savefile_directory"):
            p = ln.split("=", 1)[1].strip().strip('"')
            return os.path.basename(os.path.dirname(p)), p
    return None, None

class TokenGUI:
    def __init__(self, user, files):
        self.user, self.files = user, files
        self.val = ""
        self.sel_y = self.sel_x = 0

        self.root = tk.Tk(); self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.lbl_prompt = tk.Label(self.root, text=f"Токен для {self.user}",
                                   fg="white", bg="black", font=("Arial", 20))
        self.lbl_prompt.pack(pady=14)
        self.lbl_val = tk.Label(self.root, text="", fg="white",
                                bg="black", font=("Arial", 18))
        self.lbl_val.pack(pady=8)

        self.kf = tk.Frame(self.root, bg="black"); self.kf.pack()
        self.key_labels=[]
        for yi,row in enumerate(KEYS):
            rf=tk.Frame(self.kf,bg="black"); rf.pack()
            r=[]
            for xi,ch in enumerate(row):
                l=tk.Label(rf,text=ch,width=3,height=2,font=("Arial",14),
                           relief="ridge")
                l.pack(side=tk.LEFT,padx=4,pady=4); r.append(l)
            self.key_labels.append(r)

        instr="←→↑↓ | h:ввод | t:Back | Enter:OK | q:выход"
        tk.Label(self.root,text=instr,fg="gray",bg="black",
                 font=("Arial",12)).pack(pady=10)

        # бинды
        self.root.bind("<Up>",    lambda e:self.move( 0,-1))
        self.root.bind("<Down>",  lambda e:self.move( 0, 1))
        self.root.bind("<Left>",  lambda e:self.move(-1, 0))
        self.root.bind("<Right>", lambda e:self.move( 1, 0))
        self.root.bind("h", self.add_char)
        self.root.bind("t", self.backspace)
        self.root.bind("<Return>", self.upload)
        self.root.bind("q", lambda e:self.exit())

        self.redraw_keys()
        self.root.mainloop()

    # --- управление клавишами ---
    def move(self,dx,dy):
        self.key_labels[self.sel_y][self.sel_x].config(fg="white", bg="black")
        self.sel_y=(self.sel_y+dy)%len(KEYS)
        self.sel_x=(self.sel_x+dx)%len(KEYS[self.sel_y])
        self.redraw_keys()

    def redraw_keys(self):
        for yi,row in enumerate(self.key_labels):
            for xi,l in enumerate(row):
                if (yi,xi)==(self.sel_y,self.sel_x): l.config(fg="black",bg="white")
                else: l.config(fg="white",bg="black")

    def add_char(self,_):
        self.val+=KEYS[self.sel_y][self.sel_x]
        self.lbl_val.config(text=self.val)

    def backspace(self,_):
        self.val=self.val[:-1]; self.lbl_val.config(text=self.val)

    # --- выгрузка файлов ---
    def upload(self,_):
        if not self.val: return
        for f in self.files:
            with open(f,"rb") as fh:
                r=requests.post(f"{API_URL}/saves/upload",
                    data={"username":self.user,"token":self.val},
                    files={"file":fh})
                if r.status_code!=200:
                    messagebox.showerror("Ошибка",
                        f"{os.path.basename(f)}:\n{r.text}")
                    return
        messagebox.showinfo("OK","Все файлы выгружены.")
        self.exit()

    def exit(self,code=0):
        self.root.destroy(); sys.exit(code)

# ---------- запуск ----------
if __name__=="__main__":
    ensure_wifi()
    user, save_dir = active_profile()
    if not user:
        messagebox.showerror("Профиль","Активный профиль не найден"); sys.exit(1)
    files = glob.glob(os.path.join(save_dir,"*"))
    if not files:
        messagebox.showinfo("Пусто","Сейвы не найдены"); sys.exit(0)
    TokenGUI(user, files)