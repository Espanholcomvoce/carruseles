# Cómo correr el generador en tu PC (Windows) — paso a paso

Guía para no-programadores. La primera vez lleva ~10 minutos; después, cada
render son 2 comandos.

---

## 1. Instalar Python (una sola vez)

1. Andá a https://www.python.org/downloads/
2. Descargá la última versión para Windows y abrí el instalador.
3. **IMPORTANTE:** en la primera pantalla, marcá la casilla
   **“Add python.exe to PATH”** (abajo de todo) antes de “Install Now”.
4. Instalá y cerrá.

Para verificar: abrí **PowerShell** (botón Inicio → escribí “PowerShell” → Enter)
y escribí:
```powershell
python --version
```
Tiene que mostrar algo como `Python 3.12.x`.

---

## 2. Descargar el proyecto (una sola vez)

**Opción fácil (ZIP):**
1. Entrá a la página del repo en GitHub: `Espanholcomvoce/carruseles`.
2. Arriba a la izquierda, donde dice la rama, cambiá a
   **`claude/instagram-carousel-copy-design-8hf6bu`**.
3. Botón verde **“Code” → “Download ZIP”**.
4. Descomprimí el ZIP, por ejemplo en `D:\carruseles`.

> Para actualizaciones futuras es más cómodo **GitHub Desktop** (te deja hacer
> “Pull” con un clic), pero para arrancar el ZIP alcanza.

---

## 3. Instalar las dependencias (una sola vez)

Abrí PowerShell **dentro de la carpeta del proyecto**. Truco: abrí la carpeta
`D:\carruseles` en el Explorador, hacé clic en la barra de dirección, escribí
`powershell` y Enter. Después:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

(Esto baja Pillow, Playwright y el navegador que arma las imágenes.)

---

## 4. Poner la foto

Guardá la imagen de fondo en:
```
D:\Downloads\Imagenes para Carrossel\
```
con el nombre que dice el `copy.md` de la secuencia. Para sotaque:
```
D:\Downloads\Imagenes para Carrossel\sotaque-x-pronuncia.jpg
```

---

## 5. Generar los slides

Siempre desde PowerShell en la carpeta del proyecto:

```powershell
# ver las secuencias y su estado
python run.py list

# ver la copy de una secuencia
python run.py show sotaque-x-pronuncia

# aprobar (habilita el render)
python run.py approve sotaque-x-pronuncia

# generar las imágenes
python run.py render sotaque-x-pronuncia
```

Los slides quedan en:
```
D:\carruseles\sequences\sotaque-x-pronuncia\output\slide_01.jpg …
```
y el texto de la publicación en `output\caption.txt`.

---

## Problemas comunes

- **“python no se reconoce…”** → no marcaste “Add to PATH” al instalar. Reinstalá
  Python y marcá la casilla, o usá `py` en vez de `python`.
- **“No encontré la imagen…”** → revisá que el nombre del archivo en
  `D:\Downloads\Imagenes para Carrossel\` sea exactamente el del campo `image:`
  del `copy.md`.
- **Tarda en el primer render** → normal, está abriendo el navegador. Los
  siguientes son más rápidos.
