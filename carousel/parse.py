"""
Parser del formato copy.md.

Estructura de un copy.md:

    sequence: estudar-vs-praticar
    image: estudar-vs-praticar.jpg
    font: montserrat
    status: draft
    ===

    # CAPTION
    (texto libre de la publicación, hashtags incluidos)

    # SLIDES

    ## 1
    O que faz você | falar espanhol? | Estudar mais… | ou praticar mais?

    ## 2
    Estudar e praticar | não têm a mesma função.

    E entender essa diferença | pode acelerar muito | o seu aprendizado.

    ## 4
    :title: Por isso, estude:
    - Gramática
    - Vocabulário

Reglas dentro de cada slide (`## N`):
  * Los párrafos (separados por línea en blanco) son "stickers" independientes.
  * Dentro de un sticker de texto, las líneas se separan con `|` o con saltos
    de línea físicos.
  * Un sticker con líneas que empiezan con `- ` es un checklist. Una línea
    `:title:` define el encabezado del checklist (se dibuja como banda aparte).
"""
import re


def parse_copy(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    if "===" not in raw:
        raise ValueError(f"{path}: falta el separador '===' entre el encabezado y el cuerpo.")

    header_txt, body = raw.split("===", 1)

    meta = {}
    for line in header_txt.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()

    caption = _extract_section(body, "CAPTION")
    slides_txt = _extract_section(body, "SLIDES")
    slides = _parse_slides(slides_txt) if slides_txt else {}

    return {
        "meta": meta,
        "caption": (caption or "").strip(),
        "slides": slides,
    }


def _extract_section(body, name):
    """Devuelve el texto entre `# NAME` y el próximo `# OTRA` (o el final)."""
    m = re.search(rf"^#\s*{name}\s*$", body, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"^#\s+\w", body[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(body)
    return body[start:end].strip()


def _parse_slides(txt):
    """Divide por `## N` y parsea cada bloque en una lista de grupos (stickers)."""
    slides = {}
    parts = re.split(r"^##\s+(\d+)\s*$", txt, flags=re.MULTILINE)
    # parts = ['', '1', 'bloque1', '2', 'bloque2', ...]
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        block = parts[i + 1]
        slides[n] = _parse_slide_block(block)
    return slides


def _parse_slide_block(block):
    groups = []
    # párrafos separados por una o más líneas en blanco
    paragraphs = re.split(r"\n\s*\n", block.strip())
    for para in paragraphs:
        lines = [ln.rstrip() for ln in para.splitlines() if ln.strip()]
        if not lines:
            continue
        is_checklist = any(ln.lstrip().startswith("- ") for ln in lines)
        is_listbox = any(ln.lstrip().startswith("> ") for ln in lines)
        if is_checklist or is_listbox:
            marker = "- " if is_checklist else "> "
            gtype = "checklist" if is_checklist else "listbox"
            title = None
            items = []
            for ln in lines:
                s = ln.strip()
                if s.lower().startswith(":title:"):
                    title = s[len(":title:"):].strip()
                elif s.startswith(marker):
                    items.append(s[len(marker):].strip())
            if title:
                groups.append({"type": "text", "lines": [title]})
            groups.append({"type": gtype, "items": items})
        else:
            text_lines = []
            for ln in lines:
                text_lines.extend(part.strip() for part in ln.split("|") if part.strip())
            groups.append({"type": "text", "lines": text_lines})
    return groups
