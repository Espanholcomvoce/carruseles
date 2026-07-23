# HANDOFF — Contexto del proyecto (para retomar en una sesión nueva)

> Pasale este archivo al Claude nuevo (local, en `D:\carruseles`) junto con el
> proyecto. Resume TODO lo que venimos haciendo para que continúe sin fricción.

---

## 0. Qué es esto y estado actual

Sistema para generar **carruseles/stories de Instagram** para la cuenta
**@espanholcomvoce / Espanhol Com Você** (enseña español a brasileños), a partir
de una **copy** (`copy.md`) + una **foto base**, con un **sticker de texto
conectado** estilo Instagram (bandas por línea fusionadas con filtro SVG "goo",
que crea las muescas cóncavas). Formato **Stories 1080×1920**.

**Tarea pendiente inmediata:** renderizar la secuencia `sotaque-x-pronuncia` con
la foto real (mate) que está en `D:\Downloads\Imagenes para Carrossel\sotaque-x-pronuncia.jpg`.
En la sesión anterior (remota, en la nube) no se pudo porque no accedía al `D:\`
local; por eso pasamos a correr en la compu del usuario.

Comandos para renderizar (PowerShell dentro de `D:\carruseles`):
```powershell
python -m pip install -r requirements.txt   # una vez
python -m playwright install chromium        # una vez
python run.py approve sotaque-x-pronuncia
python run.py render  sotaque-x-pronuncia
```

---

## 1. La persona (a quién le habla la cuenta)

**"A pessoa brasileira que entende espanhol, mas trava na hora de falar."**
Ya estudió antes (escuela, app, cursinho), cae en portunhol y falsos amigos,
quiere usar el idioma de verdad (viaje/trabajo/LATAM), tiene miedo a equivocarse.
El programa que se vende es **Imersão Nativa** (método que une estudio + práctica).

---

## 2. Estructura de copy que funciona (plantilla "A × B")

Para **dos conceptos complementarios** que la gente trata como o-uno-o-el-otro
pero necesita los dos. Secuencia lógica de 13 slides (calca el carrusel original
de @alepaness "O que postar no Reels e o que postar nos Stories"):

1. Gancho — "A ou B?"
2. Promesa — "têm funções diferentes, vou te contar…"
3. Autoridad A — para qué sirve A
4. Lista práctica A (checklist)
5. Pregunta-filtro de A
6. Autoridad B — para qué sirve B
7. Lista práctica B (checklist)
8. Pregunta-filtro de B
9. Mnemotecnia — **REGLA DE TRES** (3 pares A = x / B = y) ← importante
10. Tensión — A sin B no sirve
11. Tensión — B sin A no sirve
12. Síntesis — "os dois trabalham juntos…"
13. CTA — Imersão Nativa / link na bio

**Reglas aprendidas:**
- Slide 9 SIEMPRE 3 pares (más memorable). El primer draft tenía 2 y se corrigió.
- No todos los temas son simétricos: hay **reencuadres** y **falsos dilemas**
  (ver abajo) que usan una variación de esta estructura.
- El cierre puede ser conclusión potente (más guardados/compartidos) o CTA
  directo; en estas secuencias usamos CTA a Imersão Nativa integrado como
  "consecuencia lógica", no venta de golpe.

---

## 3. Decisiones de diseño (visual)

- **Formato:** Stories 1080×1920.
- **Tipografía:** **Montserrat Bold** (elección final del usuario). Están también
  Bodoni Moda y Playfair en `fonts/`. (Cormorant Garamond se descartó: bug real
  de acentos portugueses "ê" en el render.)
- **Sticker:** fondo blanco crema `#fcfbf8`, texto casi negro `#181513`.
- **Efecto conexión:** filtro SVG "goo" (blur + threshold del alpha) fusiona las
  bandas por línea en una silueta única con muescas cóncavas (el sticker nativo
  de Instagram). Se renderiza con **Playwright + Chromium** (HTML→captura), que
  da mejor calidad que dibujar con PIL.
- **Ajustes finos que pidió el usuario:** poco blanco alrededor del texto y
  líneas juntas (padding chico, `margin-top` negativo). Banda casi de ancho
  completo, letra grande.
- **Banderas (emoji):** NO pueden ir en el sticker goo (se vuelven manchas de
  color al difuminar). Van en un recuadro sólido aparte → tipo de grupo
  `listbox`. Los emoji de bandera renderizan a color vía Noto Color Emoji.

---

## 4. Cómo funciona el sistema (pipeline con compuerta de aprobación)

Dos "roles" + gate humano: **NADA se renderiza hasta que el usuario apruebe la copy.**

1. Agente de copy escribe `sequences/<nombre>/copy.md` con `status: draft` (incluye
   el CAPTION de la publicación).
2. El usuario revisa y aprueba (`status: approved`).
3. Agente de imágenes renderiza (falla si no está `approved`).

**CLI:**
```
python run.py list                  # secuencias y estado
python run.py show    <nombre>      # ver la copy parseada
python run.py caption <nombre>      # ver el caption
python run.py approve <nombre>      # habilita el render
python run.py render  <nombre>      # genera slides + caption.txt en output/
```

**Estructura del repo:**
```
config.py            # IMAGES_DIR = D:\Downloads\Imagenes para Carrossel ; fuentes ; colores ; tamaño
run.py               # CLI
carousel/parse.py    # copy.md -> estructura
carousel/render.py   # estructura + imagen -> slides (Playwright/Chromium)
carousel/pipeline.py # orquestador + compuerta de aprobación
fonts/               # Montserrat, Bodoni, Playfair (OFL)
sequences/<nombre>/copy.md          # la copy (se aprueba acá)
sequences/<nombre>/source.<ext>     # imagen (opcional, fallback si no está en IMAGES_DIR)
sequences/<nombre>/output/          # slides renderizados + caption.txt
content-plan.md      # persona + plantillas + banco de temas
README.md            # doc general
SETUP-WINDOWS.md     # guía de instalación en Windows
```

**Resolución de la imagen:** busca `image:` del copy.md en `IMAGES_DIR`; si no,
en la carpeta de la secuencia (`source.png/jpg`).

### Formato de `copy.md`
```
sequence: mi-secuencia
image: mi-foto.jpg
font: montserrat
status: draft
===

# CAPTION
Texto de la publicación… #hashtags

# SLIDES

## 1
Línea A | Línea B | Línea C          # "|" separa líneas dentro de un sticker

## 2
Sticker 1: línea 1 | línea 2

Sticker 2 (separado por línea en blanco)

## 4
:title: Por isso, estude:            # título del checklist
- Gramática                          # "- " = ítem con check
- Vocabulário

## 6
:title: Olha só:                     # listbox (banderas), recuadro sólido
> 🇲🇽 México — palomitas             # "> " = ítem sin check (para banderas)
> 🇦🇷 Argentina — pochoclo
```

---

## 5. Secuencias existentes (todas en `sequences/`)

| Secuencia | Tipo | Estado | Nota |
|---|---|---|---|
| `estudar-vs-praticar` | A×B simétrica | approved (renderizada) | La primera. Slide 9 ya con 3 pares (base/fluência). |
| `sotaque-x-pronuncia` | reencuadre | **draft** | Tesis: sotaque=identidade (se mantém) / pronúncia=clareza (se trabalha). **PENDIENTE de render con foto del mate.** |
| `espanha-x-america-latina` | falso dilema | draft | El español es UNO (+20 países); hasta dentro de España hay variedad. |
| `como-se-diz-pipoca` | línea editorial "1 palabra, +20 países" | draft | Usa `listbox` con banderas. Cierre contra-corriente + posicionamiento del método. |

---

## 6. Línea editorial "1 palavra, +20 países" 🍿

Serie recurrente de posicionamiento: cada post toma una palabra cotidiana y
muestra cómo se dice por país (bandera + país + palabra), y cierra
**contra-corriente**: no necesitás memorizar todo, con el término neutro te
entienden en todos lados (base con autoridad: RAE / Diccionario de americanismos).
Posiciona a la profe como diferente: *enseña el español como un todo, no el de un
país; pero si querés las jergas de un lugar, también.*

- Primer ejemplo: `como-se-diz-pipoca` (draft).
- Ideas de palabras: pipoca 🍿, ônibus (autobús/camión/guagua/colectivo/micro),
  celular/móvil, morango/frutilla, abacaxi/piña/ananá, bala/caramelo/dulce…
- ⚠️ Verificar antes de publicar términos menos universales (Peru "canchita",
  Cuba "rositas de maíz", Bolívia "pipocas"). Sólidos: palomitas, pochoclo,
  cabritas, cotufas, crispetas, poporopos.

---

## 7. Cómo debe trabajar el Claude nuevo

1. Cuando el usuario da un brief/tema → escribir la copy en
   `sequences/<nombre>/copy.md` en `draft`, con caption, siguiendo la estructura
   y el tono cercano/cálido. Idioma del contenido: **portugués** (audiencia
   brasileña). Idioma de conversación: **español**.
2. Mostrar la copy y **esperar aprobación explícita** del usuario.
3. Recién ahí `approve` + `render`. Las imágenes salen en `output/`.
4. Al terminar cualquier cambio: el usuario trabaja con git; si corresponde,
   commitear en la rama `claude/instagram-carousel-copy-design-8hf6bu`.
5. Respetar SIEMPRE la compuerta: no renderizar sin aprobación.

**Pronombres/tono:** contenido inclusivo y neutro donde se pueda (la audiencia es
mixta). Tono cercano, cómplice, con autoridad suave.
