import socket
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from threading import Thread
import os
import sys
from PIL import Image, ImageTk
import platform 

class EscanerRedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escáner de Red")
        self.root.geometry("800x750")
        
        # --- COLORES ---
        self.color_fondo = "#000000"
        self.color_texto = "#00FF00"
        self.color_boton = "#003300"
        self.color_entrada = "#111111"
        
        self.root.configure(bg=self.color_fondo)
        self.ip_local = self.obtener_ip_interna()

        # --- RUTA DE IMAGEN ---
        if getattr(sys, 'frozen', False):
            ruta_base = os.path.dirname(sys.executable)
        else:
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            
        self.ruta_completa = os.path.join(ruta_base, "logo.png.jpg")

        # --- LOGO ---
        try:
            img = Image.open(self.ruta_completa)
            img = img.resize((220, 70), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            self.lbl_logo = tk.Label(self.root, image=self.logo_img, bg=self.color_fondo)
            self.lbl_logo.pack(pady=15)
        except:
            tk.Label(self.root, text=">> SISTEMA DE REDES INACAP <<", 
                     fg=self.color_texto, bg=self.color_fondo, font=("Courier", 20, "bold")).pack(pady=15)

        # --- CONTROLES ---
        marco = tk.Frame(self.root, bg=self.color_fondo, bd=2, relief="groove")
        marco.pack(fill="x", padx=20, pady=5)

        tk.Label(marco, text="IP/HOST:", fg=self.color_texto, bg=self.color_fondo, font=("Courier New", 11, "bold")).grid(row=0, column=0, padx=5, pady=15)
        
        self.entrada_target = tk.Entry(marco, bg=self.color_entrada, fg=self.color_texto, insertbackground=self.color_texto, font=("Courier New", 12), width=18)
        self.entrada_target.grid(row=0, column=1, padx=5)
        self.entrada_target.insert(0, self.ip_local)

        estilo_btn = {
            "fg": self.color_texto,
            "bg": self.color_boton,
            "activebackground": "#005500",
            "font": ("Courier New", 9, "bold"),
            "cursor": "hand2",
            "bd": 2,
            "relief": "raised"
        }
        
        tk.Button(marco, text="PING A HOST", command=self.iniciar_ping_unico, **estilo_btn).grid(row=0, column=2, padx=4)
        tk.Button(marco, text="ESCANEAR REDES", command=self.iniciar_escaneo_red, **estilo_btn).grid(row=0, column=3, padx=4)
        tk.Button(marco, text="ESCANEAR PUERTOS", command=self.iniciar_puertos, **estilo_btn).grid(row=0, column=4, padx=4)
        tk.Button(marco, text="GUARDAR LOG", command=self.guardar_resultados, **estilo_btn).grid(row=0, column=5, padx=4)

        # --- BOTÓN NUEVO ---
        tk.Button(marco, text="VER SISTEMA", command=self.mostrar_sistema, **estilo_btn).grid(row=0, column=6, padx=4)

        # --- CONSOLA ---
        self.txt_resultados = scrolledtext.ScrolledText(
            self.root,
            width=90,
            height=30,
            bg="#050505",
            fg=self.color_texto,
            font=("Courier New", 10),
            bd=0
        )
        self.txt_resultados.pack(padx=20, pady=15, fill="both", expand=True)
        
        self.escribir_log(f">> IP DETECTADA: {self.ip_local}")
        self.escribir_log(">> LISTO. INGRESE IP Y SELECCIONE ACCIÓN...")

    def obtener_ip_interna(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def escribir_log(self, mensaje):
        self.txt_results_config = self.txt_resultados
        self.txt_results_config.config(state=tk.NORMAL)
        self.txt_results_config.insert(tk.END, mensaje + "\n")
        self.txt_results_config.see(tk.END)
        self.txt_results_config.config(state=tk.DISABLED)

    def guardar_resultados(self):
        contenido = self.txt_resultados.get("1.0", tk.END)
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de Texto", "*.txt")]
        )
        if ruta:
            with open(ruta, "w", encoding='utf-8') as f:
                f.write(contenido)
            self.escribir_log(f">> LOG GUARDADO EN: {ruta}")

    # --- NUEVA FUNCIÓN ---
    def mostrar_sistema(self):
        sistema = platform.system()
        version = platform.version()
        arquitectura = platform.machine()
        self.escribir_log(f">> SISTEMA OPERATIVO: {sistema}")
        self.escribir_log(f">> VERSIÓN: {version}")
        self.escribir_log(f">> ARQUITECTURA: {arquitectura}")

    # --- TAREAS ---
    def tarea_ping_unico(self):
        obj = self.entrada_target.get()
        self.escribir_log(f">> HACIENDO PING A: {obj}...")
        res = subprocess.run(
            ["ping", "-n", "4", obj],
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        self.escribir_log(res.stdout)

    def tarea_escaneo_red(self):
        seg = ".".join(self.ip_local.split('.')[:-1]) + "."
        self.escribir_log(f">> ESCANEANDO RED: {seg}0/24...")
        encontrados = 0
        for i in range(1, 16):
            ip = f"{seg}{i}"
            res = subprocess.run(
                ["ping", "-n", "1", "-w", "400", ip],
                capture_output=True,
                text=True,
                creationflags=0x08000000
            )
            if "TTL=" in res.stdout:
                encontrados += 1
                self.escribir_log(f"[+] DISPOSITIVO: {ip}")
        self.escribir_log(f">> FIN. {encontrados} ACTIVOS.")

    def tarea_puertos(self):
        obj = self.entrada_target.get()
        self.escribir_log(f">> ANALIZANDO PUERTOS: {obj}...")
        puertos = {
            21: "FTP",
            22: "SSH",
            23: "TELNET",
            80: "HTTP",
            443: "HTTPS",
            3389: "RDP"
        }
        for p, svc in puertos.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            if s.connect_ex((obj, p)) == 0:
                self.escribir_log(f"[OK] PUERTO {p} ({svc}) ABIERTO")
            s.close()
        self.escribir_log(">> ANÁLISIS FINALIZADO.")

    def iniciar_ping_unico(self):
        Thread(target=self.tarea_ping_unico, daemon=True).start()

    def iniciar_escaneo_red(self):
        Thread(target=self.tarea_escaneo_red, daemon=True).start()

    def iniciar_puertos(self):
        Thread(target=self.tarea_puertos, daemon=True).start()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = EscanerRedApp(ventana)
    ventana.mainloop()
