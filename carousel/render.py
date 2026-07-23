"""
Renderizador de slides: toma los grupos parseados + una imagen base y genera
los JPG en formato Stories, con el sticker de texto conectado estilo Instagram
(bandas por línea fusionadas con el filtro SVG "goo", que crea las muescas
cóncavas donde cambia el ancho).

Requiere Playwright + Chromium:
    pip install playwright pillow
    playwright install chromium
"""
import os
import html

from PIL import Image

import config

CHECK_SVG = ('<svg class="chk" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
             '<polyline points="10,52 40,82 92,14" fill="none" stroke="{fg}" '
             'stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/></svg>')

GOO_FILTER = '''<svg width="0" height="0" style="position:absolute">
  <defs>
    <filter id="goo">
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur"/>
      <feColorMatrix in="blur" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -11"/>
    </filter>
  </defs>
</svg>'''

# Chromium fijo del entorno remoto; si no existe se usa el default de Playwright
# (lo que instala `playwright install chromium` en tu máquina local).
_REMOTE_CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def _group_html(g, fg):
    if g["type"] == "checklist":
        chk = CHECK_SVG.format(fg=fg)
        items = "".join(
            f'<div class="item">{chk}<span>{html.escape(it)}</span></div>'
            for it in g["items"])
        return f'<div class="sticker checklist"><div class="clbox">{items}</div></div>'
    lines = g["lines"]
    bg_lines = "".join(f'<div class="line">{html.escape(t)}</div>' for t in lines)
    fg_lines = "".join(f'<div class="line">{html.escape(t)}</div>' for t in lines)
    return (f'<div class="sticker text">'
            f'<div class="layer bg">{bg_lines}</div>'
            f'<div class="layer fg">{fg_lines}</div>'
            f'</div>')


def _build_html(font_path, image_path, groups, start_size,
                zone_top_pct=40, zone_bottom_pct=99):
    W, H = config.WIDTH, config.HEIGHT
    bg, fg = config.STICKER_BG, config.STICKER_FG
    body = "".join(_group_html(g, fg) for g in groups)
    font_url = "file://" + font_path.replace("\\", "/")
    img_url = "file://" + os.path.abspath(image_path).replace("\\", "/")
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'SF'; src:url('{font_url}') format('truetype'); font-weight:700; }}
:root {{ --fs:{start_size}px; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{W}px; height:{H}px; overflow:hidden; }}
body {{ position:relative; background:url('{img_url}') center/cover; font-family:'SF', sans-serif; }}
.zone {{ position:absolute; left:0; right:0; top:{zone_top_pct}%; bottom:{100-zone_bottom_pct}%;
  display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.sticker {{ margin: calc(var(--fs)*0.16) 0; }}
.sticker.text {{ display:grid; justify-items:center; }}
.layer {{ grid-area:1/1; display:flex; flex-direction:column; align-items:center; }}
.line {{ font-size:var(--fs); font-weight:700; line-height:1.06;
  padding: calc(var(--fs)*0.15) calc(var(--fs)*0.44);
  margin-top: calc(var(--fs)*-0.24); white-space:nowrap; text-align:center; }}
.line:first-child {{ margin-top:0; }}
.bg {{ filter:url(#goo); z-index:1; }}
.fg {{ z-index:2; }}
.bg .line {{ background:{bg}; color:transparent; border-radius: calc(var(--fs)*0.32); }}
.fg .line {{ color:{fg}; }}
.sticker.checklist .clbox {{ background:{bg}; color:{fg};
  border-radius: calc(var(--fs)*0.55); padding: calc(var(--fs)*0.5) calc(var(--fs)*0.62); }}
.item {{ display:flex; align-items:center; gap:calc(var(--fs)*0.26);
  font-size:var(--fs); font-weight:700; line-height:1.28; white-space:nowrap; }}
.chk {{ width:calc(var(--fs)*0.6); height:calc(var(--fs)*0.6); flex-shrink:0; }}
</style></head>
<body>
{GOO_FILTER}
<div class="zone">{body}</div>
</body></html>"""


def _fit_and_shoot(page, html_path, out_path, start_size,
                   min_size=34, max_h=1360, max_w=1010, step=2):
    W, H = config.WIDTH, config.HEIGHT
    page.goto("file://" + html_path.replace("\\", "/"))
    page.wait_for_timeout(60)
    size = start_size
    while size >= min_size:
        page.evaluate(f"document.documentElement.style.setProperty('--fs','{size}px')")
        zone_h = page.eval_on_selector(
            ".zone",
            "el => { let h=0; for(const s of el.children){h+=s.getBoundingClientRect().height;} return h; }")
        widths = page.eval_on_selector_all(
            ".fg .line, .item, .clbox",
            "els => els.map(e => e.getBoundingClientRect().width)")
        maxw = max(widths) if widths else 0
        if zone_h <= max_h and maxw <= max_w:
            break
        size -= step
    page.screenshot(path=out_path)
    im = Image.open(out_path)
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
        im.save(out_path, quality=95)
    return size


def _start_size(n_slides, n, groups):
    n_lines = sum(len(g.get("lines", g.get("items", []))) for g in groups)
    if n_lines >= 8:
        return 60
    if n_lines >= 6:
        return 68
    return 100


def render_sequence(slides, image_path, font_path, out_dir):
    """Renderiza todos los slides. Devuelve la lista de rutas generadas."""
    from playwright.sync_api import sync_playwright

    os.makedirs(out_dir, exist_ok=True)
    W, H = config.WIDTH, config.HEIGHT
    tmp_dir = os.path.join(out_dir, "_html")
    os.makedirs(tmp_dir, exist_ok=True)

    outputs = []
    launch_kwargs = {}
    if os.path.exists(_REMOTE_CHROMIUM):
        launch_kwargs["executable_path"] = _REMOTE_CHROMIUM

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for n in sorted(slides):
            groups = slides[n]
            start = _start_size(len(slides), n, groups)
            doc = _build_html(font_path, image_path, groups, start)
            hp = os.path.join(tmp_dir, f"slide_{n:02d}.html")
            with open(hp, "w", encoding="utf-8") as f:
                f.write(doc)
            out = os.path.join(out_dir, f"slide_{n:02d}.jpg")
            _fit_and_shoot(page, hp, out, start)
            outputs.append(out)
        browser.close()
    return outputs
