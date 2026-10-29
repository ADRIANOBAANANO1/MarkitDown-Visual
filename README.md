# MarkitDown-Visual

Interfaz gráfica para [MarkItDown](https://github.com/microsoft/markitdown) (Microsoft), pensada para convertir documentos (PDF, DOCX, PPTX, XLSX) a Markdown **sin tener que usar la consola** ni saber el nombre exacto del archivo o de la carpeta.

**Motivación:** convertir los apuntes de PDF a Markdown ocupa menos tokens al cargarlos en una IA. MarkItDown no lee imágenes, de eso se encarga la IA después.

> Proyecto personal, desarrollado y probado en **Ubuntu**.

## Estado de las versiones

| Versión | Estado | Qué incluye |
|---------|--------|-------------|
| 1 | Hecha | Conversión de un archivo (por consola y con ventana básica) |
| 2 | Hecha | Conversión en lote, configuración recordada, apertura de la carpeta |
| 3 | Planeada | Lanzador `.desktop` y arrastrar y soltar |
| 4 | Planeada | Contador aproximado de tokens |

---

## Requisitos

- Ubuntu con Python 3
- `venv` y Tkinter:

```bash
sudo apt install python3-venv python3-tk
```

## Instalación

```bash
git clone https://github.com/ADRIANOBAANANO1/MarkitDown-Visual.git
cd MarkitDown-Visual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Cada vez que quieras usar el programa en una terminal nueva, activá el entorno virtual primero:

```bash
cd MarkitDown-Visual
source venv/bin/activate
```

## Estructura

```
MarkitDown-Visual/
├── src/
│   ├── converter.py   # lógica: llama a MarkItDown
│   └── gui.py         # ventana Tkinter
├── requirements.txt
├── README.md
└── .gitignore
```

La lógica de conversión (`converter.py`) está separada de la ventana (`gui.py`), así la conversión se puede usar con o sin interfaz.

---

## Versión 1: conversión de un archivo

La primera versión convierte **un archivo a la vez**, de dos formas.

### Por consola (`converter.py`)

1. Activá el entorno virtual.
2. Ejecutá, desde la raíz del repo:

   ```bash
   python src/converter.py "/ruta/al/archivo.pdf" carpeta_destino
   ```

3. Se genera `carpeta_destino/archivo.md` (la carpeta se crea sola si no existe).

Esta forma sigue funcionando en las versiones siguientes.

### Con ventana básica

Una ventana con tres botones:

1. **Buscar...** para elegir el archivo, sin escribir su nombre.
2. **Cambiar...** para elegir la carpeta de destino (por defecto, `~/MarkItDown`).
3. **Convertir a MD** para generar el `.md`.

La conversión corre en un hilo aparte para que la ventana no se congele con archivos grandes, y al terminar muestra la ruta generada o el error.

> El código de esta ventana quedó reemplazado por el de la versión 2. Si querés verla, está en el historial de commits de git.

---

## Versión 2: lotes y comodidad

Reemplaza la ventana de la versión 1 con estas mejoras:

- **Varios archivos a la vez:** se agregan todos los que quieras y se convierten en lote.
- **Recuerda tus elecciones:** la última carpeta de salida, la última carpeta desde donde buscaste archivos y la casilla de abrir la carpeta.
- **Abre la carpeta de salida** al terminar (se puede desactivar).
- **Si un archivo falla, el lote sigue** con los demás y al final se informa cuáles fallaron.

### Cómo usarla

1. Activá el entorno virtual y abrí la ventana desde la raíz del repo:

   ```bash
   python src/gui.py
   ```

2. Tocá **Agregar archivos...** y elegí uno o varios (con `Ctrl` o `Shift` en el diálogo). Podés repetir para sumar más; los repetidos se ignoran.
3. Si querés cambiar el destino, tocá **Cambiar...** junto a "Guardar en".
4. Marcá o desmarcá **Abrir la carpeta al terminar**.
5. Tocá **Convertir a MD**. El estado muestra el avance (`Convirtiendo 2/5: nombre.pdf`).
6. Al terminar se abre la carpeta con los `.md` generados. **Limpiar lista** vacía la lista para empezar otro lote.

### Dónde guarda las preferencias

En `~/.config/markitdown-visual/config.json`, fuera del repo. Si lo borrás, la app vuelve a los valores por defecto.

### Limitaciones conocidas

- Si convertís dos archivos con el **mismo nombre** (de carpetas distintas) hacia la misma salida, el segundo pisa al primero.
- Las imágenes del documento no se extraen.
- Los avisos `Could not get FontBBox...` que a veces aparecen en la consola vienen de la librería de lectura de PDF y no afectan el resultado.

---

## Hoja de ruta

### Versión 3 (planeada)

- **Lanzador `.desktop`** para abrir la app con un clic desde el menú de aplicaciones de Ubuntu, sin usar la terminal.
- **Arrastrar y soltar** archivos sobre la ventana.

### Versión 4 (planeada)

- **Contador aproximado de tokens** del Markdown generado, para ver cuánto se ahorra al cargarlo en una IA.

---

## Créditos

La conversión la hace [MarkItDown](https://github.com/microsoft/markitdown), de Microsoft. Este proyecto solo le agrega una interfaz gráfica.
