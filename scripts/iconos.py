"""
PPA — iconos.py
Íconos SVG line-art (trazo grueso) para categorías y secciones.
Un solo lugar para todos: se reutilizan en home, tablero, institucional.

IMPORTANTE: cada SVG lleva los atributos de presentación INLINE
(fill, stroke, stroke-width, width, height). NO dependen de CSS externo.
Así nunca pueden salir gigantes ni rellenos de negro aunque el CSS no cargue.
- stroke="currentColor": toman el color del texto del contenedor.
- width/height=1em: escalan con el font-size del contexto.
"""

_A = ('viewBox="0 0 32 32" class="ic" width="1em" height="1em" '
      'fill="none" stroke="currentColor" stroke-width="2.4" '
      'stroke-linecap="round" stroke-linejoin="round"')

ICONO = {

    "expectativas": f'<svg {_A}><polyline points="5,22 12,16 17,19 26,8"/><polyline points="21,8 26,8 26,13"/></svg>',


    "energia": f'<svg {_A}><polygon points="18,4 8,18 15,18 14,28 24,14 17,14"/></svg>',

    "agro": f'<svg {_A}><line x1="16" y1="29" x2="16" y2="13"/><path d="M16 14 q-5 -1 -5 -6 q5 1 5 6"/><path d="M16 14 q5 -1 5 -6 q-5 1 -5 6"/><path d="M16 20 q-4 -1 -4 -5 q4 1 4 5"/><path d="M16 20 q4 -1 4 -5 q-4 1 -4 5"/></svg>',

    "mineria": f'<svg {_A}><path d="M5 22 C 5 14, 11 9, 16 9 C 21 9, 27 14, 27 22"/><line x1="4" y1="22" x2="28" y2="22"/><rect x="14" y="6" width="4" height="5"/><circle cx="16" cy="14" r="2"/></svg>',

    "comex": f'<svg {_A}><path d="M5 20 L27 20 L24 26 L8 26 Z"/><rect x="11" y="13" width="5" height="7"/><rect x="16" y="13" width="5" height="7"/><line x1="16" y1="8" x2="16" y2="13"/></svg>',

    "automotor": f'<svg {_A}><path d="M5 21 L7 14 L25 14 L27 21"/><line x1="4" y1="21" x2="28" y2="21"/><circle cx="10" cy="23" r="2.5"/><circle cx="22" cy="23" r="2.5"/></svg>',

    "logistica": f'<svg {_A}><rect x="4" y="11" width="13" height="10"/><path d="M17 14 L23 14 L27 18 L27 21 L17 21"/><circle cx="10" cy="23" r="2.5"/><circle cx="23" cy="23" r="2.5"/></svg>',

    "internacional": f'<svg {_A}><circle cx="16" cy="16" r="11"/><ellipse cx="16" cy="16" rx="5" ry="11"/><line x1="5" y1="16" x2="27" y2="16"/></svg>',

    "dolares": f'<svg {_A}><circle cx="16" cy="16" r="11"/><line x1="16" y1="9" x2="16" y2="23"/><path d="M19 12 C 19 10, 17 10, 16 10 C 14 10, 13 11, 13 13 C 13 15, 15 15, 16 16 C 18 16, 19 17, 19 19 C 19 21, 17 22, 16 22 C 14 22, 13 21, 13 20"/></svg>',

    "mercado": f'<svg {_A}><polyline points="5,22 12,15 17,18 26,7"/><polyline points="21,7 26,7 26,12"/></svg>',

    "empleo": f'<svg {_A}><circle cx="16" cy="11" r="5"/><path d="M6 27 C 6 20, 11 18, 16 18 C 21 18, 26 20, 26 27"/></svg>',

    "fiscal": f'<svg {_A}><rect x="7" y="5" width="18" height="22" rx="2"/><line x1="11" y1="11" x2="21" y2="11"/><line x1="11" y1="16" x2="21" y2="16"/><line x1="11" y1="21" x2="17" y2="21"/></svg>',

    "banda": f'<svg {_A}><line x1="6" y1="16" x2="26" y2="16"/><line x1="6" y1="11" x2="6" y2="21"/><line x1="26" y1="11" x2="26" y2="21"/><circle cx="16" cy="16" r="3"/></svg>',

    "finanzas": f'<svg {_A}><circle cx="16" cy="16" r="11"/><line x1="16" y1="9" x2="16" y2="23"/><path d="M19 12 C 19 10, 17 10, 16 10 C 14 10, 13 11, 13 13 C 13 15, 15 15, 16 16 C 18 16, 19 17, 19 19 C 19 21, 17 22, 16 22 C 14 22, 13 21, 13 20"/></svg>',

    "laboral": f'<svg {_A}><circle cx="16" cy="11" r="5"/><path d="M6 27 C 6 20, 11 18, 16 18 C 21 18, 26 20, 26 27"/></svg>',

    "fulbito": f'<svg {_A}><circle cx="16" cy="16" r="11"/><path d="M16 5 L19 10 L16 13 L13 10 Z"/><path d="M27 13 L22 14 L20 18 L23 22"/><path d="M27 19 L22 18"/><path d="M5 13 L10 14 L12 18 L9 22"/><path d="M5 19 L10 18"/><path d="M16 27 L19 22 L16 19 L13 22 Z"/><polygon points="16,13 20,18 19,22 13,22 12,18" fill="currentColor" opacity="0.15"/></svg>',
}


def icono(clave):
    """Devuelve el SVG de una clave, o vacío si no existe."""
    return ICONO.get(clave, "")
