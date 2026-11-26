import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib, os, subprocess
from datetime import datetime

try:
    import mysql.connector
except ImportError:
    mysql = None

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
except ImportError:
    tb = None

DB_CONFIG = {"host": "localhost", "user": "root", "password": "", "database": "evoting_osis"}

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class DB:
    def __init__(self): self.conn = None
    def ensure(self):
        if mysql is None:
            raise RuntimeError("mysql-connector-python belum terpasang. Jalankan pip install -r requirements.txt")
        if self.conn is None or not self.conn.is_connected():
            self.conn = mysql.connector.connect(**DB_CONFIG)
    def run(self, sql, params=(), fetch=True):
        self.ensure()
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else None
        if not fetch: self.conn.commit()
        cur.close()
        return result

class App:
    NAV = [
        ("⌂", "Dashboard"),
        ("♙", "Data Kandidat"),
        ("☷", "Data Pemilih"),
        ("✓", "Pemungutan Suara"),
        ("▥", "Hasil Perolehan"),
        ("⚙", "Pengaturan"),
    ]
    def __init__(self, root):
        self.root, self.db, self.user = root, DB(), None
        self.root.title("E-Voting OSIS | Sistem Pemilihan Digital")
        self.root.geometry("1240x780")
        self.root.minsize(1050, 680)
        self.style()
        self.login()

    def style(self):
        if tb:
            try:
                self.root.style.theme_use("flatly")
            except Exception: pass
        style = ttk.Style()
        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10), background="#ffffff",
                        fieldbackground="#ffffff", foreground="#25324b")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#edf2f8",
                        foreground="#334155", padding=9)
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(12, 8))
        style.configure("TEntry", padding=7)

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def login(self):
        self.clear()
        page = tk.Frame(self.root, bg="#eef3f9"); page.pack(fill="both", expand=True)
        hero = tk.Frame(page, bg="#142b52", width=440); hero.pack(side="left", fill="y"); hero.pack_propagate(False)
        tk.Label(hero, text="EV", bg="#254b85", fg="white", font=("Segoe UI", 22, "bold"),
                 width=3, height=1).pack(anchor="w", padx=46, pady=(125, 25))
        tk.Label(hero, text="Pemilihan OSIS\nlebih mudah dan transparan.", bg="#142b52", fg="white",
                 font=("Segoe UI", 25, "bold"), justify="left").pack(anchor="w", padx=46)
        tk.Label(hero, text="Kelola kandidat, pemilih, dan hasil suara\nmelalui satu aplikasi desktop.",
                 bg="#142b52", fg="#c5d5ed", font=("Segoe UI", 11), justify="left").pack(anchor="w", padx=46, pady=18)
        tk.Label(hero, text="E-VOTING KETUA OSIS  •  ADMIN PANEL", bg="#142b52", fg="#91acd2",
                 font=("Segoe UI", 8, "bold")).pack(side="bottom", anchor="w", padx=46, pady=28)

        right = tk.Frame(page, bg="#ffffff"); right.pack(side="left", fill="both", expand=True)
        box = tk.Frame(right, bg="white", width=390); box.place(relx=.5, rely=.5, anchor="center")
        tk.Label(box, text="Selamat datang 👋", bg="white", fg="#172b4d",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(box, text="Masuk untuk mengelola pemilihan Ketua OSIS.",
                 bg="white", fg="#718096", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 28))
        tk.Label(box, text="USERNAME", bg="white", fg="#42526b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.user_entry = ttk.Entry(box, width=45); self.user_entry.pack(fill="x", pady=(7, 18), ipady=5)
        tk.Label(box, text="PASSWORD", bg="white", fg="#42526b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.pass_entry = ttk.Entry(box, width=45, show="●"); self.pass_entry.pack(fill="x", pady=(7, 20), ipady=5)
        btn = tk.Button(box, text="MASUK KE DASHBOARD  →", command=self.do_login,
                        bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
                        relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2", pady=12)
        btn.pack(fill="x")
        tk.Label(box, text="Akun demo: admin  |  Password: admin123",
                 bg="white", fg="#8795a8", font=("Segoe UI", 9)).pack(anchor="w", pady=16)
        self.pass_entry.bind("<Return>", lambda e: self.do_login())
        self.user_entry.focus_set()

    def do_login(self):
        u, p = self.user_entry.get().strip(), self.pass_entry.get()
        if not u or not p:
            messagebox.showwarning("Login", "Username dan password harus diisi."); return
        try:
            rows = self.db.run("SELECT id,username,nama_lengkap,role FROM users WHERE username=%s AND password_hash=%s",
                               (u, sha(p)))
            if not rows:
                messagebox.showerror("Login gagal", "Username atau password tidak sesuai."); return
            self.user = rows[0]; self.dashboard()
        except Exception as e:
            messagebox.showerror("Database belum siap",
                f"Tidak dapat terhubung ke MySQL.\n\n{e}\n\nAktifkan MySQL di XAMPP dan import database/e_voting_osis.sql.")

    def layout(self, title, subtitle=""):
        self.clear()
        shell = tk.Frame(self.root, bg="#f3f6fb"); shell.pack(fill="both", expand=True)
        side = tk.Frame(shell, bg="#142b52", width=225); side.pack(side="left", fill="y"); side.pack_propagate(False)
        brand = tk.Frame(side, bg="#142b52"); brand.pack(fill="x", padx=20, pady=(23, 26))
        tk.Label(brand, text="EV", bg="#2f5fa7", fg="white", font=("Segoe UI", 16, "bold"),
                 width=3, height=1).pack(side="left")
        tk.Label(brand, text="E-VOTING\nKETUA OSIS", bg="#142b52", fg="white",
                 font=("Segoe UI", 10, "bold"), justify="left").pack(side="left", padx=10)
        tk.Label(side, text="MENU UTAMA", bg="#142b52", fg="#8fa8ca",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 8))
        for icon, name in self.NAV:
            active = name == title
            b = tk.Button(side, text=f" {icon}    {name}", anchor="w", command=lambda n=name: self.navigate(n),
                          bg="#254b85" if active else "#142b52", fg="white" if active else "#c5d5ed",
                          activebackground="#315f9e", activeforeground="white", relief="flat",
                          font=("Segoe UI", 10, "bold" if active else "normal"), cursor="hand2",
                          padx=18, pady=12, bd=0)
            b.pack(fill="x", padx=10, pady=3)
        tk.Frame(side, bg="#29466f", height=1).pack(fill="x", padx=18, pady=18)
        tk.Label(side, text="ADMINISTRATOR", bg="#142b52", fg="#8fa8ca",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22)
        tk.Label(side, text=self.user["nama_lengkap"], bg="#142b52", fg="white",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(5, 12))
        tk.Button(side, text="↪  Keluar", command=self.logout, bg="#142b52", fg="#fca5a5",
                  activebackground="#254b85", activeforeground="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), anchor="w", padx=20, pady=12).pack(side="bottom", fill="x", padx=10, pady=14)

        main = tk.Frame(shell, bg="#f3f6fb"); main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(main, bg="white", height=72); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text=title, bg="white", fg="#172b4d",
                 font=("Segoe UI", 17, "bold")).pack(side="left", padx=26)
        tk.Label(top, text=f"Administrator  •  {datetime.now().strftime('%d %b %Y')}",
                 bg="white", fg="#8492a6", font=("Segoe UI", 9)).pack(side="right", padx=26)
        self.body = tk.Frame(main, bg="#f3f6fb"); self.body.pack(fill="both", expand=True, padx=25, pady=22)
        tk.Label(self.body, text=subtitle, bg="#f3f6fb", fg="#718096",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

    def navigate(self, name):
        {"Dashboard":self.dashboard, "Data Kandidat":self.candidates,
         "Data Pemilih":self.voters, "Pemungutan Suara":self.voting,
         "Hasil Perolehan":self.results, "Pengaturan":self.settings}[name]()

    def logout(self):
        if messagebox.askyesno("Keluar", "Yakin ingin keluar dari aplikasi?"):
            self.user = None; self.login()

    def metric(self, parent, label, value, color, hint):
        card = tk.Frame(parent, bg="white", highlightbackground="#e3eaf3", highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 13), ipady=14)
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        inner = tk.Frame(card, bg="white"); inner.pack(side="left", padx=16, pady=11)
        tk.Label(inner, text=label, bg="white", fg="#718096", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(inner, text=str(value), bg="white", fg="#172b4d", font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=3)
        tk.Label(inner, text=hint, bg="white", fg="#9aa7b8", font=("Segoe UI", 8)).pack(anchor="w")

    def dashboard(self):
        self.layout("Dashboard", "Ringkasan singkat kondisi pemilihan Ketua OSIS.")
        try:
            candidates = self.db.run("SELECT COUNT(*) n FROM kandidat")[0]["n"]
            voters = self.db.run("SELECT COUNT(*) n FROM pemilih")[0]["n"]
            votes = self.db.run("SELECT COUNT(*) n FROM suara")[0]["n"]
            done = self.db.run("SELECT COUNT(*) n FROM pemilih WHERE sudah_memilih=1")[0]["n"]
        except Exception as e:
            messagebox.showerror("Database", str(e)); return
        row = tk.Frame(self.body, bg="#f3f6fb"); row.pack(fill="x")
        self.metric(row, "TOTAL KANDIDAT", candidates, "#3b82f6", "Pasangan calon terdaftar")
        self.metric(row, "TOTAL PEMILIH", voters, "#0f9f8f", "Pemilih terdaftar")
        self.metric(row, "SUARA MASUK", votes, "#8b5cf6", "Suara yang sudah tercatat")
        self.metric(row, "BELUM MEMILIH", max(voters-done,0), "#f59e0b", "Pemilih yang belum memilih")
        lower = tk.Frame(self.body, bg="#f3f6fb"); lower.pack(fill="both", expand=True, pady=20)
        left = tk.Frame(lower, bg="white", highlightbackground="#e3eaf3", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0,12))
        tk.Label(left, text="Selamat datang di E-Voting OSIS", bg="white", fg="#172b4d",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=22, pady=(22,7))
        tk.Label(left, text="Semua kebutuhan pemilihan tersedia dalam menu di sebelah kiri. Ikuti alur sederhana berikut:",
                 bg="white", fg="#718096", font=("Segoe UI", 9), wraplength=520, justify="left").pack(anchor="w", padx=22)
        for n, txt in enumerate(["1. Tambahkan pasangan kandidat.", "2. Masukkan daftar pemilih berdasarkan NIS.",
                                 "3. Catat suara melalui menu Pemungutan Suara.", "4. Pantau hasil dan ekspor laporan."], 1):
            tk.Label(left, text=txt, bg="white", fg="#334155", font=("Segoe UI", 10)).pack(anchor="w", padx=25, pady=8)
        right = tk.Frame(lower, bg="#eaf2ff", width=240); right.pack(side="right", fill="y"); right.pack_propagate(False)
        tk.Label(right, text="AKSES CEPAT", bg="#eaf2ff", fg="#315b96",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(20,12))
        for label, fn in [("+ Tambah Kandidat", self.candidates), ("+ Tambah Pemilih", self.voters),
                          ("Lihat Hasil Suara", self.results)]:
            tk.Button(right, text=label, command=fn, bg="white", fg="#2455a0",
                      activebackground="#dbeafe", relief="flat", font=("Segoe UI", 9, "bold"),
                      cursor="hand2", pady=11).pack(fill="x", padx=14, pady=5)

    def section(self, title, subtitle):
        self.layout(title, subtitle)

    def tree(self, parent, columns, headings, widths=None):
        wrap = tk.Frame(parent, bg="white", highlightbackground="#e3eaf3", highlightthickness=1)
        wrap.pack(fill="both", expand=True, pady=12)
        tree = ttk.Treeview(wrap, columns=columns, show="headings")
        for i, (col, head) in enumerate(zip(columns, headings)):
            tree.heading(col, text=head)
            tree.column(col, width=(widths[i] if widths else 130), anchor="w")
        sy = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        sx = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tree.pack(side="top", fill="both", expand=True, padx=7, pady=(7,0))
        sy.pack(side="right", fill="y"); sx.pack(side="bottom", fill="x")
        return tree

    def popup_form(self, title, fields, on_save):
        win = tk.Toplevel(self.root); win.title(title); win.configure(bg="white")
        win.transient(self.root); win.grab_set(); win.resizable(False, False)
        box = tk.Frame(win, bg="white", padx=24, pady=22); box.pack(fill="both", expand=True)
        tk.Label(box, text=title, bg="white", fg="#172b4d",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,15))
        entries = {}
        for label, key in fields:
            tk.Label(box, text=label, bg="white", fg="#475569",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(7,3))
            ent = ttk.Entry(box, width=43); ent.pack(fill="x", ipady=5); entries[key] = ent
        def save():
            vals = {k:v.get().strip() for k,v in entries.items()}
            if any(not v for v in vals.values()):
                messagebox.showwarning("Validasi", "Semua kolom wajib diisi.", parent=win); return
            try:
                on_save(vals); win.destroy()
            except Exception as e: messagebox.showerror("Gagal menyimpan", str(e), parent=win)
        tk.Button(box, text="SIMPAN DATA", command=save, bg="#2563eb", fg="white",
                  activebackground="#1d4ed8", relief="flat", font=("Segoe UI", 9, "bold"),
                  cursor="hand2", pady=10).pack(fill="x", pady=(20,0))
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width()-win.winfo_width())//2
        y = self.root.winfo_rooty() + (self.root.winfo_height()-win.winfo_height())//2
        win.geometry(f"+{max(x,0)}+{max(y,0)}")

    def candidates(self):
        self.section("Data Kandidat", "Kelola pasangan calon Ketua dan Wakil Ketua OSIS.")
        toolbar = tk.Frame(self.body, bg="#f3f6fb"); toolbar.pack(fill="x")
        search = ttk.Entry(toolbar, width=32); search.pack(side="left", ipady=5)
        tk.Label(toolbar, text="Cari nama kandidat", bg="#f3f6fb", fg="#8492a6").pack(side="left", padx=10)
        tree = self.tree(self.body, ("id","no","ketua","wakil","kelas"), ("ID","No. Urut","Nama Ketua","Nama Wakil","Kelas"), [55,90,220,220,110])
        def refresh():
            tree.delete(*tree.get_children())
            q = f"%{search.get().strip()}%"
            rows = self.db.run("SELECT id,nomor_urut,nama_ketua,nama_wakil,kelas FROM kandidat WHERE nama_ketua LIKE %s OR nama_wakil LIKE %s ORDER BY nomor_urut",(q,q))
            for r in rows: tree.insert("","end",values=(r["id"],r["nomor_urut"],r["nama_ketua"],r["nama_wakil"],r["kelas"]))
        def add():
            def save(v):
                self.db.run("INSERT INTO kandidat(nomor_urut,nama_ketua,nama_wakil,kelas) VALUES(%s,%s,%s,%s)",
                            (int(v["no"]),v["ketua"],v["wakil"],v["kelas"]),False); refresh()
            self.popup_form("Tambah Pasangan Kandidat",[("Nomor urut","no"),("Nama ketua","ketua"),("Nama wakil","wakil"),("Kelas","kelas")],save)
        def delete():
            sel=tree.selection()
            if not sel: messagebox.showinfo("Pilih data","Pilih kandidat yang ingin dihapus."); return
            if messagebox.askyesno("Konfirmasi","Hapus kandidat yang dipilih?"):
                try: self.db.run("DELETE FROM kandidat WHERE id=%s",(tree.item(sel[0],"values")[0],),False); refresh()
                except Exception as e: messagebox.showerror("Tidak bisa menghapus",str(e))
        tk.Button(toolbar,text="+ Tambah Kandidat",command=add,bg="#2563eb",fg="white",relief="flat",
                  font=("Segoe UI",9,"bold"),padx=13,pady=8,cursor="hand2").pack(side="right",padx=5)
        ttk.Button(toolbar,text="Cari",command=refresh).pack(side="right",padx=5)
        ttk.Button(toolbar,text="Hapus Terpilih",command=delete).pack(side="right",padx=5)
        refresh()

    def voters(self):
        self.section("Data Pemilih", "Tambahkan dan pantau daftar siswa yang memiliki hak pilih.")
        toolbar=tk.Frame(self.body,bg="#f3f6fb");toolbar.pack(fill="x")
        search=ttk.Entry(toolbar,width=32);search.pack(side="left",ipady=5)
        tree=self.tree(self.body,("id","nis","nama","kelas","status"),("ID","NIS","Nama Pemilih","Kelas","Status Memilih"),[55,130,260,120,140])
        def refresh():
            tree.delete(*tree.get_children());q=f"%{search.get().strip()}%"
            rows=self.db.run("SELECT id,nis,nama,kelas,sudah_memilih FROM pemilih WHERE nis LIKE %s OR nama LIKE %s ORDER BY nama",(q,q))
            for r in rows:tree.insert("","end",values=(r["id"],r["nis"],r["nama"],r["kelas"],"Sudah memilih" if r["sudah_memilih"] else "Belum memilih"))
        def add():
            def save(v):
                self.db.run("INSERT INTO pemilih(nis,nama,kelas,password_hash) VALUES(%s,%s,%s,%s)",
                            (v["nis"],v["nama"],v["kelas"],sha(v["nis"])),False);refresh()
            self.popup_form("Tambah Data Pemilih",[("NIS","nis"),("Nama lengkap","nama"),("Kelas","kelas")],save)
        def delete():
            sel=tree.selection()
            if not sel:messagebox.showinfo("Pilih data","Pilih pemilih terlebih dahulu.");return
            if messagebox.askyesno("Konfirmasi","Hapus data pemilih yang dipilih?"):
                try:self.db.run("DELETE FROM pemilih WHERE id=%s",(tree.item(sel[0],"values")[0],),False);refresh()
                except Exception as e:messagebox.showerror("Tidak bisa menghapus",str(e))
        tk.Button(toolbar,text="+ Tambah Pemilih",command=add,bg="#2563eb",fg="white",relief="flat",
                  font=("Segoe UI",9,"bold"),padx=13,pady=8,cursor="hand2").pack(side="right",padx=5)
        ttk.Button(toolbar,text="Cari",command=refresh).pack(side="right",padx=5)
        ttk.Button(toolbar,text="Hapus Terpilih",command=delete).pack(side="right",padx=5)
        refresh()

    def voting(self):
        self.section("Pemungutan Suara", "Catat pilihan siswa. Pastikan NIS terdaftar dan siswa belum pernah memilih.")
        panel=tk.Frame(self.body,bg="white",highlightbackground="#e3eaf3",highlightthickness=1,padx=25,pady=24)
        panel.pack(fill="x")
        tk.Label(panel,text="Formulir Pencatatan Suara",bg="white",fg="#172b4d",
                 font=("Segoe UI",15,"bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,16))
        tk.Label(panel,text="NIS Pemilih",bg="white",fg="#475569",font=("Segoe UI",9,"bold")).grid(row=1,column=0,sticky="w",pady=10)
        nis=ttk.Entry(panel,width=42);nis.grid(row=1,column=1,sticky="w",padx=18,ipady=5)
        tk.Label(panel,text="Pilih Pasangan Kandidat",bg="white",fg="#475569",font=("Segoe UI",9,"bold")).grid(row=2,column=0,sticky="w",pady=10)
        candidates=self.db.run("SELECT id,nomor_urut,nama_ketua,nama_wakil FROM kandidat WHERE aktif=1 ORDER BY nomor_urut")
        options=[f'{r["id"]}::{r["nomor_urut"]} - {r["nama_ketua"]} & {r["nama_wakil"]}' for r in candidates]
        combo=ttk.Combobox(panel,values=options,state="readonly",width=55);combo.grid(row=2,column=1,sticky="w",padx=18,ipady=5)
        tk.Label(panel,text="Periksa kembali pilihan sebelum menyimpan. Suara yang sudah dicatat tidak dapat diubah dari aplikasi.",
                 bg="white",fg="#b45309",font=("Segoe UI",9),wraplength=700).grid(row=3,column=0,columnspan=2,sticky="w",pady=16)
        def cast():
            if not nis.get().strip() or not combo.get():
                messagebox.showwarning("Data belum lengkap","Isi NIS dan pilih kandidat.");return
            try:
                self.db.ensure();cur=self.db.conn.cursor()
                cur.execute("SELECT id,sudah_memilih FROM pemilih WHERE nis=%s FOR UPDATE",(nis.get().strip(),));v=cur.fetchone()
                if not v:raise ValueError("NIS tidak ditemukan. Tambahkan siswa melalui menu Data Pemilih.")
                if v[1]:raise ValueError("Siswa ini sudah menggunakan hak pilih.")
                election=self.db.run("SELECT id FROM pemilihan WHERE status='berlangsung' ORDER BY id DESC LIMIT 1")
                if not election:raise ValueError("Tidak ada pemilihan yang sedang berlangsung.")
                kid=int(combo.get().split("::")[0])
                if not messagebox.askyesno("Konfirmasi pilihan","Yakin ingin mencatat suara untuk:\n"+combo.get().split("::",1)[1]+"?"):return
                cur.execute("INSERT INTO suara(pemilih_id,kandidat_id,pemilihan_id) VALUES(%s,%s,%s)",(v[0],kid,election[0]["id"]))
                cur.execute("UPDATE pemilih SET sudah_memilih=1 WHERE id=%s",(v[0],));self.db.conn.commit();cur.close()
                messagebox.showinfo("Berhasil","Suara berhasil dicatat.");nis.delete(0,"end");combo.set("")
            except Exception as e:
                if self.db.conn:self.db.conn.rollback()
                messagebox.showerror("Gagal mencatat suara",str(e))
        tk.Button(panel,text="✓  KONFIRMASI & SIMPAN SUARA",command=cast,bg="#0f9f8f",fg="white",
                  activebackground="#0d8276",relief="flat",font=("Segoe UI",10,"bold"),
                  cursor="hand2",padx=16,pady=11).grid(row=4,column=1,sticky="w",padx=18)

    def results(self):
        self.section("Hasil Perolehan", "Lihat jumlah suara setiap pasangan kandidat dan ekspor laporan.")
        rows=self.db.run("""SELECT k.nomor_urut,k.nama_ketua,k.nama_wakil,COUNT(s.id) jumlah
          FROM kandidat k LEFT JOIN suara s ON s.kandidat_id=k.id
          GROUP BY k.id ORDER BY jumlah DESC,k.nomor_urut""")
        total=sum(r["jumlah"] for r in rows)
        tk.Label(self.body,text=f"Total suara tercatat: {total}",bg="#eaf2ff",fg="#2455a0",
                 font=("Segoe UI",11,"bold"),padx=15,pady=12).pack(anchor="w")
        tree=self.tree(self.body,("no","ketua","wakil","suara"),("No. Urut","Nama Ketua","Nama Wakil","Jumlah Suara"),[100,250,250,150])
        for r in rows:tree.insert("","end",values=(r["nomor_urut"],r["nama_ketua"],r["nama_wakil"],r["jumlah"]))
        bar=tk.Frame(self.body,bg="#f3f6fb");bar.pack(fill="x")
        def pdf():
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
                if not path:return
                c=canvas.Canvas(path,pagesize=A4);c.setFont("Helvetica-Bold",16);c.drawString(48,800,"HASIL PEMILIHAN KETUA OSIS")
                c.setFont("Helvetica",10);y=765
                c.drawString(48,y,f"Tanggal cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}");y-=30
                for r in rows:
                    c.drawString(48,y,f'{r["nomor_urut"]}. {r["nama_ketua"]} / {r["nama_wakil"]} : {r["jumlah"]} suara');y-=22
                c.drawString(48,y,f"Total suara: {total}");c.save();messagebox.showinfo("Selesai","Laporan PDF berhasil dibuat.")
            except Exception as e:messagebox.showerror("PDF",str(e))
        def excel():
            try:
                from openpyxl import Workbook
                path=filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel","*.xlsx")])
                if not path:return
                wb=Workbook();ws=wb.active;ws.title="Hasil Suara";ws.append(["No Urut","Ketua","Wakil","Jumlah Suara"])
                for r in rows:ws.append([r["nomor_urut"],r["nama_ketua"],r["nama_wakil"],r["jumlah"]])
                wb.save(path);messagebox.showinfo("Selesai","Laporan Excel berhasil dibuat.")
            except Exception as e:messagebox.showerror("Excel",str(e))
        ttk.Button(bar,text="Ekspor PDF",command=pdf).pack(side="left",padx=4)
        ttk.Button(bar,text="Ekspor Excel",command=excel).pack(side="left",padx=4)

    def settings(self):
        self.section("Pengaturan", "Atur status pemilihan dan buat cadangan database.")
        panel=tk.Frame(self.body,bg="white",highlightbackground="#e3eaf3",highlightthickness=1,padx=22,pady=22)
        panel.pack(fill="x")
        tk.Label(panel,text="Status Pemilihan",bg="white",fg="#172b4d",
                 font=("Segoe UI",14,"bold")).pack(anchor="w")
        rows=self.db.run("SELECT id,nama_pemilihan,status FROM pemilihan ORDER BY id DESC")
        if rows:
            r=rows[0]
            tk.Label(panel,text=f'{r["nama_pemilihan"]}  •  Status saat ini: {r["status"]}',
                     bg="white",fg="#64748b",font=("Segoe UI",10)).pack(anchor="w",pady=8)
            for st in ["draft","berlangsung","selesai"]:
                ttk.Button(panel,text=f"Ubah ke {st}",command=lambda s=st,i=r["id"]:self.set_status(i,s)).pack(side="left",padx=(0,8),pady=8)
        else:
            tk.Label(panel,text="Belum ada data pemilihan. Impor ulang database awal.",bg="white").pack(anchor="w")
        backup=tk.Frame(self.body,bg="white",highlightbackground="#e3eaf3",highlightthickness=1,padx=22,pady=22)
        backup.pack(fill="x",pady=16)
        tk.Label(backup,text="Backup Database",bg="white",fg="#172b4d",font=("Segoe UI",14,"bold")).pack(anchor="w")
        tk.Label(backup,text="Simpan salinan data pemilihan ke file SQL.",bg="white",fg="#718096").pack(anchor="w",pady=7)
        ttk.Button(backup,text="Buat Backup SQL",command=self.backup).pack(anchor="w",pady=6)

    def set_status(self, ident, status):
        try:
            self.db.run("UPDATE pemilihan SET status=%s WHERE id=%s",(status,ident),False)
            messagebox.showinfo("Status diperbarui",f"Status pemilihan sekarang: {status}")
            self.settings()
        except Exception as e:messagebox.showerror("Pengaturan",str(e))

    def backup(self):
        path=filedialog.asksaveasfilename(defaultextension=".sql",filetypes=[("SQL","*.sql")])
        if not path:return
        cmd=["mysqldump","-h",DB_CONFIG["host"],"-u",DB_CONFIG["user"]]
        if DB_CONFIG["password"]:cmd.append("-p"+DB_CONFIG["password"])
        cmd.append(DB_CONFIG["database"])
        try:
            with open(path,"w",encoding="utf-8") as f:subprocess.run(cmd,stdout=f,check=True)
            messagebox.showinfo("Backup","Backup database berhasil disimpan.")
        except Exception as e:messagebox.showerror("Backup gagal",f"{e}\nPastikan mysqldump XAMPP tersedia di PATH.")

if __name__ == "__main__":
    root = tb.Window(themename="flatly") if tb else tk.Tk()
    App(root)
    root.mainloop()
