"""
PPA — iconos.py
Íconos SVG line-art (trazo grueso) para categorías y secciones.
Un solo lugar para todos: se reutilizan en home, tablero, institucional.

Uso:
    from iconos import ICONO
    html = ICONO["energia"]   # devuelve el <svg>...</svg>

El color y tamaño se controlan por CSS (stroke + width/height de la clase
contenedora), así que el mismo SVG sirve en rojo chico o tinta grande.
"""

# Cada SVG usa currentColor implícito vía CSS (stroke se define afuera).
# viewBox 0 0 32 32, sin fill, trazo redondeado.

ICONO = {
    "macro": '<svg viewBox="0 0 32 32" class="ic"><line x1="5" y1="27" x2="27" y2="27"/><rect x="7" y="18" width="4" height="9"/><rect x="14" y="13" width="4" height="14"/><rect x="21" y="8" width="4" height="19"/></svg>',

    "expectativas": '<svg viewBox="0 0 32 32" class="ic"><polyline points="5,22 12,16 17,19 26,8"/><polyline points="21,8 26,8 26,13"/></svg>',

    "politica": '<svg viewBox="0 0 32 32" class="ic"><polyline points="6,12 16,6 26,12"/><line x1="8" y1="12" x2="8" y2="24"/><line x1="13" y1="12" x2="13" y2="24"/><line x1="19" y1="12" x2="19" y2="24"/><line x1="24" y1="12" x2="24" y2="24"/><line x1="5" y1="24" x2="27" y2="24"/></svg>',

    "energia": '<svg viewBox="0 0 32 32" class="ic"><polygon points="18,4 8,18 15,18 14,28 24,14 17,14"/></svg>',

    # Agro: espiga afinada (limpia)
    "agro": '<svg viewBox="0 0 32 32" class="ic"><line x1="16" y1="29" x2="16" y2="13"/><path d="M16 14 q-5 -1 -5 -6 q5 1 5 6"/><path d="M16 14 q5 -1 5 -6 q-5 1 -5 6"/><path d="M16 20 q-4 -1 -4 -5 q4 1 4 5"/><path d="M16 20 q4 -1 4 -5 q-4 1 -4 5"/></svg>',

    # Minería: casco minero con lámpara
    "mineria": '<svg viewBox="0 0 32 32" class="ic"><path d="M5 22 C 5 14, 11 9, 16 9 C 21 9, 27 14, 27 22"/><line x1="4" y1="22" x2="28" y2="22"/><rect x="14" y="6" width="4" height="5"/><circle cx="16" cy="14" r="2"/></svg>',

    "comex": '<svg viewBox="0 0 32 32" class="ic"><path d="M5 20 L27 20 L24 26 L8 26 Z"/><rect x="11" y="13" width="5" height="7"/><rect x="16" y="13" width="5" height="7"/><line x1="16" y1="8" x2="16" y2="13"/></svg>',

    "automotor": '<svg viewBox="0 0 32 32" class="ic"><path d="M5 21 L7 14 L25 14 L27 21"/><line x1="4" y1="21" x2="28" y2="21"/><circle cx="10" cy="23" r="2.5"/><circle cx="22" cy="23" r="2.5"/></svg>',

    "logistica": '<svg viewBox="0 0 32 32" class="ic"><rect x="4" y="11" width="13" height="10"/><path d="M17 14 L23 14 L27 18 L27 21 L17 21"/><circle cx="10" cy="23" r="2.5"/><circle cx="23" cy="23" r="2.5"/></svg>',

    "internacional": '<svg viewBox="0 0 32 32" class="ic"><circle cx="16" cy="16" r="11"/><ellipse cx="16" cy="16" rx="5" ry="11"/><line x1="5" y1="16" x2="27" y2="16"/></svg>',

    # Extra para secciones del tablero
    "dolares": '<svg viewBox="0 0 32 32" class="ic"><circle cx="16" cy="16" r="11"/><line x1="16" y1="9" x2="16" y2="23"/><path d="M19 12 C 19 10, 17 10, 16 10 C 14 10, 13 11, 13 13 C 13 15, 15 15, 16 16 C 18 16, 19 17, 19 19 C 19 21, 17 22, 16 22 C 14 22, 13 21, 13 20"/></svg>',

    "mercado": '<svg viewBox="0 0 32 32" class="ic"><polyline points="5,22 12,15 17,18 26,7"/><polyline points="21,7 26,7 26,12"/></svg>',

    "empleo": '<svg viewBox="0 0 32 32" class="ic"><circle cx="16" cy="11" r="5"/><path d="M6 27 C 6 20, 11 18, 16 18 C 21 18, 26 20, 26 27"/></svg>',

    "fiscal": '<svg viewBox="0 0 32 32" class="ic"><rect x="7" y="5" width="18" height="22" rx="2"/><line x1="11" y1="11" x2="21" y2="11"/><line x1="11" y1="16" x2="21" y2="16"/><line x1="11" y1="21" x2="17" y2="21"/></svg>',

    # Banda cambiaria (candado/límites)
    "banda": '<svg viewBox="0 0 32 32" class="ic"><line x1="6" y1="16" x2="26" y2="16"/><line x1="6" y1="11" x2="6" y2="21"/><line x1="26" y1="11" x2="26" y2="21"/><circle cx="16" cy="16" r="3"/></svg>',
}


def icono(clave):
    """Devuelve el SVG de una clave, o vacío si no existe."""
    return ICONO.get(clave, "")
