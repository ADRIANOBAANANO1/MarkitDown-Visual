from pathlib import Path

from markitdown import MarkItDown

import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

def convertir_a_md(archivo_entrada: str, carpeta_salida: str) -> Path:
    """Convierte un archivo a Markdown y lo guarda en carpeta_salida.

    Devuelve la ruta del archivo .md generado.
    """
    entrada = Path(archivo_entrada)
    salida_dir = Path(carpeta_salida)

    if not entrada.is_file():
        raise FileNotFoundError(f"No existe el archivo: {entrada}")

    salida_dir.mkdir(parents=True, exist_ok=True)

    resultado = MarkItDown().convert(str(entrada))

    archivo_salida = salida_dir / f"{entrada.stem}.md"
    archivo_salida.write_text(resultado.text_content, encoding="utf-8")

    return archivo_salida


if __name__ == "__main__":
    # Prueba rápida desde consola:
    #   python src/converter.py ruta/al/archivo.pdf carpeta_destino
    import sys

    if len(sys.argv) != 3:
        print("Uso: python src/converter.py <archivo> <carpeta_salida>")
        sys.exit(1)

    print("Generado:", convertir_a_md(sys.argv[1], sys.argv[2]))
