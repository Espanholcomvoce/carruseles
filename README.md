# Generador de Carruseles / Stories

Sistema para crear secuencias de slides estilo Instagram (formato Stories 9:16)
a partir de una **copy** y una **imagen base**, con el sticker de texto conectado
(las muescas cóncavas nativas de Instagram) sobre tu foto.

El flujo tiene **dos roles** y una **compuerta de aprobación**:

1. **Agente de copy** → escribe `sequences/<nombre>/copy.md` (estado `draft`),
   incluyendo el texto de la publicación (caption).
2. **Vos aprobás** → revisás/editás el `copy.md` y lo aprobás.
3. **Agente de imágenes** → recién ahí renderiza los slides.
   **No sale nada a producción hasta que apruebes la copy.**

---

## Instalación (una sola vez)

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuración

Editá `config.py`:

- `IMAGES_DIR` → carpeta donde guardás tus fotos base.
  Por defecto: `D:\Downloads\Imagenes para Carrossel`
- Fuentes disponibles: `montserrat`, `bodoni`, `playfair` (elegís por secuencia
  en el campo `font:` del `copy.md`).

## Uso

```bash
# ver todas las secuencias y su estado
python run.py list

# ver la copy parseada de una secuencia
python run.py show    <nombre>

# ver solo el caption
python run.py caption <nombre>

# aprobar (habilita el render)
python run.py approve <nombre>

# renderizar los slides (falla si no está aprobada)
python run.py render  <nombre>
```

Los slides quedan en `sequences/<nombre>/output/slide_01.jpg …` y el caption en
`sequences/<nombre>/output/caption.txt`.

---

## Crear una secuencia nueva

1. Creá la carpeta `sequences/<nombre>/`.
2. Poné adentro un `copy.md` (copiá el de `estudar-vs-praticar` como plantilla).
3. Guardá la imagen base:
   - en `IMAGES_DIR` con el nombre del campo `image:`, **o**
   - dentro de la carpeta de la secuencia como `source.png`.
4. `python run.py approve <nombre>` y después `python run.py render <nombre>`.

> Con Claude Code: le pasás el brief/copy y Claude actúa como **agente de copy**,
> escribe el `copy.md` en `draft` y espera tu OK. Cuando aprobás, corre el
> **agente de imágenes** (`render`).

---

## Formato de `copy.md`

```
sequence: mi-secuencia
image: mi-foto.jpg          # archivo dentro de IMAGES_DIR
font: montserrat            # montserrat | bodoni | playfair
status: draft               # draft -> approved
===

# CAPTION
Texto de la publicación...
#hashtags #aca

# SLIDES

## 1
Línea A | Línea B | Línea C          # "|" separa líneas dentro de un mismo sticker

## 2
Primer sticker: línea 1 | línea 2

Segundo sticker (separado por línea en blanco)

## 4
:title: Por isso, estude:            # título del checklist (banda aparte)
- Gramática                          # cada "- " es un ítem con check
- Vocabulário
```

**Reglas:**
- Cada `## N` es un slide.
- Dentro de un slide, los párrafos separados por una línea en blanco son
  **stickers** independientes (globos separados).
- Dentro de un sticker de texto, las líneas se separan con `|` o con saltos de
  línea. Cada línea tiene su propio ancho → se genera la muesca cóncava.
- Un sticker con ítems `- ...` se renderiza como **checklist** con tildes.

---

## Estructura del proyecto

```
config.py                 # rutas, fuentes, colores, tamaño
run.py                    # CLI
carousel/
  parse.py                # copy.md -> estructura
  render.py               # estructura + imagen -> slides (sticker goo)
  pipeline.py             # orquestador + compuerta de aprobación
fonts/                    # fuentes (OFL)
sequences/
  <nombre>/
    copy.md               # la copy (se aprueba acá)
    source.png            # (opcional) imagen base si no usás IMAGES_DIR
    output/               # slides renderizados + caption.txt
```
