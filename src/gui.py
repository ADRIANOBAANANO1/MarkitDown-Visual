import json
import subprocess
import threading
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import convertir_a_md

CONFIG = Path.home() / ".config" / "markitdown-visual" / "config.json"
CARPETA_DEFECTO = str(Path.home() / "MarkItDown")


def cargar_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def guardar_config(datos):
    try:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(datos), encoding="utf-8")
    except OSError:
        pass


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("MarkItDown Visual")
        self.geometry("620x430")
        self.minsize(520, 360)

        self.datos = cargar_config()
        self.archivos = []
        self.carpeta = tk.StringVar(
            value=self.datos.get("carpeta_salida", CARPETA_DEFECTO)
        )
        self.abrir_al_final = tk.BooleanVar(
            value=self.datos.get("abrir_al_final", True)
        )
        self.estado = tk.StringVar(value="Agregá uno o más archivos para empezar.")

        self._armar_ui()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _armar_ui(self):
        marco = ttk.Frame(self, padding=15)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)

        # Archivos de entrada
        fila_botones = ttk.Frame(marco)
        fila_botones.grid(row=0, column=0, sticky="ew")
        ttk.Label(fila_botones, text="Archivos a convertir:").pack(side="left")
        self.btn_limpiar = ttk.Button(
            fila_botones, text="Limpiar lista", command=self.limpiar
        )
        self.btn_limpiar.pack(side="right")
        self.btn_agregar = ttk.Button(
            fila_botones, text="Agregar archivos...", command=self.agregar
        )
        self.btn_agregar.pack(side="right", padx=6)

        lista_marco = ttk.Frame(marco)
        lista_marco.grid(row=1, column=0, sticky="nsew", pady=8)
        lista_marco.columnconfigure(0, weight=1)
        lista_marco.rowconfigure(0, weight=1)

        self.lista = tk.Listbox(lista_marco, height=8, activestyle="none")
        self.lista.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(lista_marco, command=self.lista.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.lista.config(yscrollcommand=barra.set)

        for zona in (self.lista, self):
            zona.drop_target_register(DND_FILES)
            zona.dnd_bind("<<Drop>>", self._al_soltar)

        # Carpeta de salida
        fila_salida = ttk.Frame(marco)
        fila_salida.grid(row=2, column=0, sticky="ew", pady=4)
        fila_salida.columnconfigure(1, weight=1)
        ttk.Label(fila_salida, text="Guardar en:").grid(row=0, column=0)
        ttk.Entry(fila_salida, textvariable=self.carpeta, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=8
        )
        self.btn_carpeta = ttk.Button(
            fila_salida, text="Cambiar...", command=self.elegir_carpeta
        )
        self.btn_carpeta.grid(row=0, column=2)

        ttk.Checkbutton(
            marco,
            text="Abrir la carpeta al terminar",
            variable=self.abrir_al_final,
        ).grid(row=3, column=0, sticky="w", pady=4)

        # Convertir
        self.btn_convertir = ttk.Button(
            marco, text="Convertir a MD", command=self.convertir
        )
        self.btn_convertir.grid(row=4, column=0, pady=10)

        ttk.Label(marco, textvariable=self.estado, wraplength=580).grid(
            row=5, column=0, sticky="w"
        )

    # --- Acciones ---

    def agregar(self):
        rutas = filedialog.askopenfilenames(
            title="Elegí los archivos a convertir",
            initialdir=self.datos.get("carpeta_entrada", str(Path.home())),
            filetypes=[
                ("Documentos", "*.pdf *.docx *.pptx *.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if rutas:
            self.datos["carpeta_entrada"] = str(Path(rutas[0]).parent)
            self._agregar_rutas(rutas)

    def _al_soltar(self, evento):
        # splitlist maneja correctamente los nombres con espacios
        self._agregar_rutas(self.tk.splitlist(evento.data))
        return evento.action

    def _agregar_rutas(self, rutas):
        ignorados = 0
        for ruta in rutas:
            if not Path(ruta).is_file():
                ignorados += 1
                continue
            if ruta not in self.archivos:
                self.archivos.append(ruta)
                self.lista.insert("end", Path(ruta).name)
        mensaje = f"{len(self.archivos)} archivo(s) listo(s) para convertir."
        if ignorados:
            mensaje += f" Se ignoraron {ignorados} elemento(s) que no son archivos."
        self.estado.set(mensaje)

    def limpiar(self):
        self.archivos.clear()
        self.lista.delete(0, "end")
        self.estado.set("Lista vacía. Agregá archivos para empezar.")

    def elegir_carpeta(self):
        ruta = filedialog.askdirectory(
            title="Elegí la carpeta de destino", initialdir=self.carpeta.get()
        )
        if ruta:
            self.carpeta.set(ruta)

    def _bloquear(self, bloquear):
        estado = "disabled" if bloquear else "normal"
        for boton in (
            self.btn_agregar,
            self.btn_limpiar,
            self.btn_carpeta,
            self.btn_convertir,
        ):
            boton.config(state=estado)

    def convertir(self):
        if not self.archivos:
            messagebox.showwarning("Falta el archivo", "Primero agregá algún archivo.")
            return
        self._bloquear(True)
        # Copia de la lista, para que el hilo no dependa de cambios posteriores
        threading.Thread(
            target=self._trabajo, args=(list(self.archivos), self.carpeta.get()),
            daemon=True,
        ).start()

    def _trabajo(self, archivos, carpeta):
        correctos = 0
        errores = []
        total = len(archivos)
        for i, ruta in enumerate(archivos, start=1):
            nombre = Path(ruta).name
            self.after(0, self.estado.set, f"Convirtiendo {i}/{total}: {nombre}")
            try:
                convertir_a_md(ruta, carpeta)
                correctos += 1
            except Exception as error:
                errores.append(f"{nombre}: {error}")
        self.after(0, self._terminar, correctos, errores)

    def _terminar(self, correctos, errores):
        self._bloquear(False)
        self.estado.set(f"Listo: {correctos} convertido(s), {len(errores)} con error.")
        if errores:
            messagebox.showerror("Algunos archivos fallaron", "\n".join(errores))
        if correctos and self.abrir_al_final.get():
            try:
                subprocess.Popen(["xdg-open", self.carpeta.get()])
            except OSError:
                pass

    def _cerrar(self):
        self.datos["carpeta_salida"] = self.carpeta.get()
        self.datos["abrir_al_final"] = self.abrir_al_final.get()
        guardar_config(self.datos)
        self.destroy()


if __name__ == "__main__":
    App().mainloop()