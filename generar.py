"""
Genera dark_mode.svg y light_mode.svg para tu perfil de GitHub (estilo neofetch).
Edita DATOS y vuelve a correr:  python generar.py
Por defecto dibuja una telaraña. Si existe arte.txt, usa ese dibujo ASCII. Si pones una foto llamada foto.jpg en la misma carpeta, la convierte en arte ASCII
(necesita: pip install pillow).
"""
from html import escape
from pathlib import Path

USUARIO = "sotohn@github"

# (clave, valor). None = línea de sección.
DATOS = [
    ("OS", "Windows, macOS"),
    ("Major", "Biomedical Engineering"),
    ("Interests", "Reading, Poetry"),
    ("Mindset", "Read, reflect, rethink"),
    ("Status", "Programmer in progress"),
    ("", ""),
    ("Languages", "C, C++, Python"),
    ("Spoken", "Spanish, English"),
    ("", ""),
    (None, "Secret identity"),
    ("Alter ego", "Classified"),
]

ANCHO = 58          # caracteres del panel de datos
FS = 16             # tamaño de letra
LH = 20             # alto de línea
ASCII_ANCHO = 40    # caracteres del arte ASCII

TEMAS = {
    "dark_mode.svg":  dict(bg="#161b22", texto="#c9d1d9", clave="#ffa657", valor="#a5d6ff", punto="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", texto="#24292f", clave="#953800", valor="#0a3069", punto="#c2cfde"),
}

ASCII_DEFECTO = r"""
        |  |  |  |  |  |  |  |
     .--+--+--+--+--+--+--+--+--.
   --|                          |--
   --|   .------------------.   |--
   --|   |                  |   |--
   --|   |   o          o   |   |--
   --|   |                  |   |--
   --|   |    \________/    |   |--
   --|   |                  |   |--
   --|   '------------------'   |--
   --|                          |--
     '--+--+--+--+--+--+--+--+--'
        |  |  |  |  |  |  |  |
""".strip("\n").split("\n")


def telarana(x, y, w, h, color):
    """Telaraña vectorial con una araña colgando (dibujo original)."""
    import math
    cx, cy = x + w * 0.44, y + h * 0.45
    R = min(w, h) * 0.37
    n, rot = 9, -0.3
    ang = [rot + 2 * math.pi * k / n for k in range(n)]
    p = []
    for a in ang:  # radios
        ex, ey = cx + R * 1.18 * math.cos(a), cy + R * 1.18 * math.sin(a)
        p.append(f'M{cx:.1f},{cy:.1f}L{ex:.1f},{ey:.1f}')
    for r in (0.16, 0.34, 0.53, 0.74, 0.97):  # hilos con caída
        rr = R * r
        for k in range(n):
            a0, a1 = ang[k], ang[k] + 2 * math.pi / n
            am = (a0 + a1) / 2
            x0, y0 = cx + rr * math.cos(a0), cy + rr * math.sin(a0)
            x1, y1 = cx + rr * math.cos(a1), cy + rr * math.sin(a1)
            qx, qy = cx + rr * 0.80 * math.cos(am), cy + rr * 0.80 * math.sin(am)
            p.append(f'M{x0:.1f},{y0:.1f}Q{qx:.1f},{qy:.1f} {x1:.1f},{y1:.1f}')
    # araña colgando de un hilo
    sx = x + w * 0.88
    by = y + h * 0.80
    p.append(f'M{sx:.1f},{y:.1f}L{sx:.1f},{by - 9:.1f}')
    for s in (-1, 1):
        for i, dy in enumerate((-4, -1, 2, 5)):
            kx = 9 + (1 if i in (1, 2) else 0) * 2
            p.append(f'M{sx + s * 4:.1f},{by + dy * 0.6:.1f}'
                     f'L{sx + s * kx:.1f},{by + dy * 1.2 - 5:.1f}'
                     f'L{sx + s * (kx + 4):.1f},{by + dy * 1.8 + 4:.1f}')
    return (f'<path d="{"".join(p)}" fill="none" stroke="{color}" stroke-width="1.2" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>'
            f'<ellipse cx="{sx:.1f}" cy="{by + 1:.1f}" rx="5" ry="6.5" fill="{color}"/>'
            f'<circle cx="{sx:.1f}" cy="{by - 7:.1f}" r="3.5" fill="{color}"/>')


def ascii_desde_foto(ruta, ancho=ASCII_ANCHO, alto=24):
    from PIL import Image, ImageOps
    chars = "@%#*+=-:. "
    img = ImageOps.grayscale(Image.open(ruta))
    img = ImageOps.autocontrast(img).resize((ancho, alto))
    px = list(img.getdata())
    filas = []
    for y in range(alto):
        fila = px[y * ancho:(y + 1) * ancho]
        filas.append("".join(chars[p * (len(chars) - 1) // 255] for p in fila))
    return filas


def linea_dato(clave, valor):
    """Devuelve tspans con puntos de relleno para alinear el valor a la derecha."""
    puntos = ANCHO - len(clave) - len(valor) - 5
    return (f'<tspan class="punto">. </tspan><tspan class="clave">{escape(clave)}</tspan>:'
            f'<tspan class="punto"> {"." * max(puntos, 1)} </tspan>'
            f'<tspan class="valor">{escape(valor)}</tspan>')


def generar(nombre, c, arte):
    lineas = [f'{escape(USUARIO)} ' + "-" * (ANCHO - len(USUARIO) - 1)]
    for clave, valor in DATOS:
        if clave is None:
            lineas.append(f'- {escape(valor)} ' + "-" * (ANCHO - len(valor) - 3))
        elif clave == "":
            lineas.append('<tspan class="punto">. </tspan>')
        else:
            lineas.append(linea_dato(clave, valor))

    filas = max(len(arte) if arte != "telarana" else 15, len(lineas))
    alto = 30 + filas * LH + 10
    x_info = 15 + ASCII_ANCHO * FS * 0.6 + 30
    ancho_total = int(x_info + ANCHO * FS * 0.6 + 20)

    y0 = 30 + (filas - (len(arte) if arte != "telarana" else filas)) * LH // 2
    y1 = 30 + (filas - len(lineas)) * LH // 2

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{ancho_total}" height="{alto}" '
           f'font-size="{FS}px">',
           f'<style>.clave{{fill:{c["clave"]}}}.valor{{fill:{c["valor"]}}}.punto{{fill:{c["punto"]}}}'
           f'text,tspan{{white-space:pre;font-family:ui-monospace,SFMono-Regular,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace}}</style>',
           f'<rect width="{ancho_total}" height="{alto}" fill="{c["bg"]}" rx="15"/>']
    if arte == "telarana":
        svg.append(telarana(20, 15, x_info - 50, alto - 30, c["texto"]))
    else:
        svg.append(f'<text x="15" y="{y0}" fill="{c["texto"]}">')
        for i, f in enumerate(arte):
            svg.append(f'<tspan x="15" y="{y0 + i * LH}">{escape(f)}</tspan>')
        svg.append('</text>')
    svg.append(f'<text x="{x_info}" y="{y1}" fill="{c["texto"]}">')
    for i, l in enumerate(lineas):
        svg.append(f'<tspan x="{x_info}" y="{y1 + i * LH}">{l}</tspan>')
    svg.append('</text></svg>')
    Path(nombre).write_text("\n".join(svg), encoding="utf-8")


if __name__ == "__main__":
    foto, txt = Path("foto.jpg"), Path("arte.txt")
    if foto.exists():
        arte = ascii_desde_foto(foto)
    elif txt.exists():
        arte = txt.read_text(encoding="utf-8").split("\n")
    else:
        arte = "telarana"   # cambia por ASCII_DEFECTO si prefieres el chip
    for nombre, c in TEMAS.items():
        generar(nombre, c, arte)
    print("Listo: dark_mode.svg y light_mode.svg")
