"""
Orquestador con compuerta de aprobación.

Flujo:
  1. (Agente de copy) escribe sequences/<nombre>/copy.md con status: draft
  2. Vos revisás copy.md y lo aprobás:  python run.py approve <nombre>
  3. (Agente de imágenes) renderiza:     python run.py render  <nombre>
     -> se NIEGA a renderizar si status != approved

Comandos:
  python run.py list
  python run.py show     <nombre>
  python run.py caption  <nombre>
  python run.py approve  <nombre>
  python run.py render   <nombre>
"""
import os
import re
import sys

import config
from carousel.parse import parse_copy


def _seq_dir(name):
    return os.path.join(config.SEQUENCES_DIR, name)


def _copy_path(name):
    return os.path.join(_seq_dir(name), "copy.md")


def _resolve_image(meta, name):
    """Busca la imagen: primero en IMAGES_DIR, si no en la carpeta de la secuencia."""
    img = meta.get("image", "").strip()
    candidates = []
    if img:
        candidates.append(os.path.join(config.IMAGES_DIR, img))
        candidates.append(os.path.join(_seq_dir(name), img))
    # fallback: cualquier source.* en la carpeta de la secuencia
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidates.append(os.path.join(_seq_dir(name), f"source.{ext}"))
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(
        f"No encontré la imagen para '{name}'. Busqué:\n  " +
        "\n  ".join(candidates) +
        f"\nPoné la foto en {config.IMAGES_DIR} con el nombre del campo 'image:', "
        f"o como source.png en la carpeta de la secuencia.")


def _font_path(meta):
    key = (meta.get("font") or config.DEFAULT_FONT).strip().lower()
    fname = config.FONTS.get(key, config.FONTS[config.DEFAULT_FONT])
    return os.path.join(config.FONTS_DIR, fname)


def cmd_list(_):
    if not os.path.isdir(config.SEQUENCES_DIR):
        print("No hay carpeta de secuencias todavía.")
        return
    rows = []
    for name in sorted(os.listdir(config.SEQUENCES_DIR)):
        cp = _copy_path(name)
        if not os.path.exists(cp):
            continue
        data = parse_copy(cp)
        status = data["meta"].get("status", "draft")
        n = len(data["slides"])
        rows.append((name, status, n))
    if not rows:
        print("No hay secuencias todavía.")
        return
    print(f"{'SECUENCIA':<32} {'ESTADO':<10} SLIDES")
    for name, status, n in rows:
        print(f"{name:<32} {status:<10} {n}")


def cmd_show(name):
    data = parse_copy(_copy_path(name))
    print(f"# {name}  ({data['meta'].get('status','draft')})\n")
    for n in sorted(data["slides"]):
        print(f"## Slide {n}")
        for g in data["slides"][n]:
            if g["type"] == "checklist":
                for it in g["items"]:
                    print(f"  ✓ {it}")
            elif g["type"] == "listbox":
                for it in g["items"]:
                    print(f"  • {it}")
            else:
                print("  " + " / ".join(g["lines"]))
        print()


def cmd_caption(name):
    data = parse_copy(_copy_path(name))
    print(data["caption"] or "(sin caption)")


def cmd_approve(name):
    cp = _copy_path(name)
    with open(cp, encoding="utf-8") as f:
        txt = f.read()
    if re.search(r"^status:\s*\w+", txt, re.MULTILINE):
        txt = re.sub(r"^status:\s*\w+", "status: approved", txt, count=1, flags=re.MULTILINE)
    else:
        txt = "status: approved\n" + txt
    with open(cp, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"✓ '{name}' aprobada. Ya podés renderizar:  python run.py render {name}")


def cmd_render(name):
    data = parse_copy(_copy_path(name))
    status = data["meta"].get("status", "draft").lower()
    if status != "approved":
        print(f"✗ '{name}' está en estado '{status}'. No se renderiza hasta que la apruebes.")
        print(f"  Revisá el copy y cuando estés conforme:  python run.py approve {name}")
        sys.exit(1)

    image_path = _resolve_image(data["meta"], name)
    font_path = _font_path(data["meta"])
    out_dir = os.path.join(_seq_dir(name), "output")

    from carousel.render import render_sequence
    print(f"Renderizando '{name}' ({len(data['slides'])} slides) con imagen:\n  {image_path}")
    outputs = render_sequence(data["slides"], image_path, font_path, out_dir)
    print(f"✓ {len(outputs)} slides generados en:\n  {out_dir}")
    for o in outputs:
        print("   " + os.path.basename(o))
    cap = os.path.join(out_dir, "caption.txt")
    with open(cap, "w", encoding="utf-8") as f:
        f.write(data["caption"] or "")
    print(f"✓ Caption guardado en:\n  {cap}")


COMMANDS = {
    "list": cmd_list,
    "show": cmd_show,
    "caption": cmd_caption,
    "approve": cmd_approve,
    "render": cmd_render,
}


def main(argv):
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return
    cmd = argv[0]
    arg = argv[1] if len(argv) > 1 else None
    if cmd != "list" and not arg:
        print(f"Falta el nombre de la secuencia:  python run.py {cmd} <nombre>")
        return
    COMMANDS[cmd](arg)
