"""
Configuración global del generador de carruseles.

Ajustá estos valores a tu entorno. La única ruta que probablemente quieras
cambiar es IMAGES_DIR (dónde tenés guardadas las fotos base).
"""
import os

# Carpeta donde guardás las imágenes base (una por secuencia).
# En tu Windows: D:\Downloads\Imagenes para Carrossel
# El sistema busca acá el archivo indicado en el campo `image:` de cada copy.md.
IMAGES_DIR = r"D:\Downloads\Imagenes para Carrossel"

# Carpeta raíz de las secuencias (cada una es una subcarpeta con su copy.md).
SEQUENCES_DIR = os.path.join(os.path.dirname(__file__), "sequences")

# Carpeta de fuentes incluidas en el repo.
FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# Fuentes disponibles (nombre -> archivo). El copy.md elige una con `font:`.
FONTS = {
    "montserrat": "Montserrat-Bold.ttf",
    "bodoni": "BodoniModa-Bold.ttf",
    "playfair": "PlayfairDisplay-Black.ttf",
}
DEFAULT_FONT = "montserrat"

# Tamaño de salida (formato Stories 9:16).
WIDTH, HEIGHT = 1080, 1920

# Colores del sticker.
STICKER_BG = "#fcfbf8"   # fondo del globo (blanco crema)
STICKER_FG = "#181513"   # color del texto (casi negro)
