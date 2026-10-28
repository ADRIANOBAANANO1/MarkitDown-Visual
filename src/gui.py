import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import convertir_a_md


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MarkItDown GUI")
        self.geometry("580x230")
        self.resizable(False, False)

        self.archivo = tk.StringVar()
        self.carpeta = tk.StringVar(value=str(Path.home() / "MarkItDown"))
        self.estado = tk.StringVar(value="Elegí un archivo para empezar.")

        self._armar_ui()

    def _armar_ui(self):
        marco = ttk.Frame(self, padding=15)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(1, weight=1)

        # Archivo de entrada
        ttk.Label(marco, text="Archivo:").grid(row=0, column=0, sticky="w", pady=8)
        ttk.Entry(marco, textvariable=self.archivo, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(marco, text="Buscar...", command=self.elegir_archivo).grid(
            row=0, column=2
        )

        # Carpeta de salida
        ttk.Label(marco, text="Guardar en:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(marco, textvariable=self.carpeta, state="readonly").grid(
            row=1, column=1, sticky="ew", padx=8
        )
        ttk.Button(marco, text="Cambiar...", command=self.elegir_carpeta).grid(
            row=1, column=2
        )

        # Convertir
        self.boton = ttk.Button(marco, text="Convertir a MD", command=self.convertir)
        self.boton.grid(row=2, column=0, columnspan=3, pady=18)

        # Estado
        ttk.Label(marco, textvariable=self.estado, wraplength=540).grid(
            row=3, column=0, columnspan=3, sticky="w"
        )

    def elegir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Elegí el archivo a convertir",
            initialdir=str(Path.home()),
            filetypes=[
                ("Documentos", "*.pdf *.docx *.pptx *.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if ruta:
            self.archivo.set(ruta)
            self.estado.set("Listo para convertir.")

    def elegir_carpeta(self):
        ruta = filedialog.askdirectory(
            title="Elegí la carpeta de destino", initialdir=self.carpeta.get()
        )
        if ruta:
            self.carpeta.set(ruta)

    def convertir(self):
        if not self.archivo.get():
            messagebox.showwarning("Falta el archivo", "Primero elegí un archivo.")
            return

        self.boton.config(state="disabled")
        self.estado.set("Convirtiendo...")

        # En un hilo aparte para que la ventana no se congele
        threading.Thread(target=self._trabajo, daemon=True).start()

    def _trabajo(self):
        try:
            salida = convertir_a_md(self.archivo.get(), self.carpeta.get())
            self.after(0, self._terminar, f"Listo: {salida}", False)
        except Exception as error:
            self.after(0, self._terminar, f"Error: {error}", True)

    def _terminar(self, mensaje, es_error):
        self.estado.set(mensaje)
        self.boton.config(state="normal")
        if es_error:
            messagebox.showerror("No se pudo convertir", mensaje)


if __name__ == "__main__":
    App().mainloop()
