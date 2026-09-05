"""Das Gene-Keys-Profil als Mandala -- Darstellung im Stil des Originals.

WOZU DAS HIER

genekeys.com zeigt das Profil als Rad: farbige Sphaeren-Kreise mit
Tor.Linie, durch Linien verbunden, umschaltbar zwischen den Sequenzen
(Full / Genius / Love / Prosperity / Harmony). Diese Datei baut denselben
Aufbau als autarke SVG-Seite nach.

WAS UEBERNOMMEN WIRD UND WAS NICHT

Nachgebaut wird das LAYOUT: Anordnung der Sphaeren, Verbindungslinien,
Farbcode je Sequenz, die Tabs. Das ist Oberflaeche, kein Text. NICHT
uebernommen wird die geschuetzte Deutungssprache von Gene Keys (die
Schatten/Gabe/Siddhi-Woerter je Tor) -- statt dessen steht in jeder
Sphaere die Tor.Linie und der gemeinfreie klassische I-Ging-Name.

Die Zahlen liefert gene_keys.profil(); diese Datei malt sie nur.
"""
from __future__ import annotations

import html as _html

# Farben je Sequenz: (Fuellung hell, Fuellung dunkel, Linie/Text-Akzent)
_FARBE = {
    "aktiv": ("#8bb07a", "#5f8a4e", "#4a6b3c"),   # gruen  -- Aktivierung
    "venus": ("#cf6a60", "#a5372e", "#7f2a23"),   # rot    -- Venus
    "perle": ("#6a9bd8", "#3d6fb0", "#2c5286"),   # blau   -- Perle
    "stern": ("#8b7dd8", "#5f4fb0", "#463b86"),   # violett-- Sternperle
}

# Heimatsequenz jeder Sphaere -- bestimmt die Farbe im Vollprofil.
_HEIMAT = {
    "Life's Work": "aktiv", "Evolution": "aktiv", "Radiance": "aktiv",
    "Purpose": "aktiv",
    "Attraction": "venus", "IQ": "venus", "EQ": "venus", "SQ": "venus",
    "Core": "venus",
    "Vocation": "perle", "Culture": "perle", "Brand": "perle", "Pearl": "perle",
    "Creativity": "stern", "Relating": "stern", "Stability": "stern",
}

# Dezente Unterzeile je Sphaere -- eigene Worte, keine Rudd-Deutung.
_ROLLE = {
    "Life's Work": "Lebensaufgabe", "Evolution": "Wachstum",
    "Radiance": "Ausstrahlung", "Purpose": "Bestimmung",
    "Attraction": "Anziehung", "IQ": "Verstand", "EQ": "Gefuehl",
    "SQ": "Intuition", "Core": "Kernthema",
    "Vocation": "Berufung", "Culture": "Umfeld", "Brand": "Marke",
    "Pearl": "Perle", "Creativity": "Kreativitaet", "Relating": "Beziehung",
    "Stability": "Stabilitaet",
}

# --- Layouts je Tab. Koordinaten im viewBox 0..1000 x 0..880. ---
_L_FULL = {
    "Life's Work": (500, 110), "Pearl": (500, 232),
    "Core": (402, 322), "Culture": (598, 322),
    "Radiance": (232, 432), "SQ": (500, 432), "Evolution": (768, 432),
    "IQ": (402, 542), "EQ": (598, 542),
    "Attraction": (500, 640), "Purpose": (500, 762),
}
_K_FULL = [
    ("Life's Work", "Pearl", "perle"), ("Pearl", "Core", "perle"),
    ("Pearl", "Culture", "perle"), ("Core", "Culture", "perle"),
    ("Life's Work", "Radiance", "aktiv"), ("Radiance", "Purpose", "aktiv"),
    ("Purpose", "Evolution", "aktiv"), ("Evolution", "Life's Work", "aktiv"),
    ("Core", "SQ", "venus"), ("SQ", "IQ", "venus"), ("SQ", "EQ", "venus"),
    ("IQ", "EQ", "venus"), ("EQ", "Attraction", "venus"),
    ("Attraction", "Purpose", "venus"),
]

_L_AKTIV = {
    "Life's Work": (500, 150), "Radiance": (280, 440),
    "Evolution": (720, 440), "Purpose": (500, 730),
}
_K_AKTIV = [
    ("Life's Work", "Radiance", "aktiv"), ("Radiance", "Purpose", "aktiv"),
    ("Purpose", "Evolution", "aktiv"), ("Evolution", "Life's Work", "aktiv"),
    ("Radiance", "Evolution", "aktiv"),
]

_L_VENUS = {
    "Core": (500, 140), "SQ": (500, 300),
    "IQ": (360, 450), "EQ": (640, 450),
    "Attraction": (500, 600), "Purpose": (500, 760),
}
_K_VENUS = [
    ("Core", "SQ", "venus"), ("SQ", "IQ", "venus"), ("SQ", "EQ", "venus"),
    ("IQ", "EQ", "venus"), ("EQ", "Attraction", "venus"),
    ("Attraction", "Purpose", "venus"),
]

_L_PERLE = {
    "Brand": (500, 170), "Pearl": (500, 420),
    "Vocation": (330, 650), "Culture": (670, 650),
}
_K_PERLE = [
    ("Brand", "Pearl", "perle"), ("Brand", "Vocation", "perle"),
    ("Brand", "Culture", "perle"), ("Pearl", "Vocation", "perle"),
    ("Pearl", "Culture", "perle"), ("Vocation", "Culture", "perle"),
]

_L_STERN = {
    "Brand": (500, 130), "Relating": (760, 300), "Culture": (760, 560),
    "Stability": (500, 730), "Vocation": (240, 560), "Creativity": (240, 300),
    "Pearl": (500, 430),
}
_K_STERN = [
    ("Brand", "Relating", "stern"), ("Relating", "Culture", "stern"),
    ("Culture", "Stability", "stern"), ("Stability", "Vocation", "stern"),
    ("Vocation", "Creativity", "stern"), ("Creativity", "Brand", "stern"),
    ("Pearl", "Brand", "stern"), ("Pearl", "Relating", "stern"),
    ("Pearl", "Culture", "stern"), ("Pearl", "Stability", "stern"),
    ("Pearl", "Vocation", "stern"), ("Pearl", "Creativity", "stern"),
]

_TABS = [
    ("full",  "Vollprofil",   _L_FULL,  _K_FULL,  None),
    ("aktiv", "Aktivierung",  _L_AKTIV, _K_AKTIV, "aktiv"),
    ("venus", "Venus",        _L_VENUS, _K_VENUS, "venus"),
    ("perle", "Perle",        _L_PERLE, _K_PERLE, "perle"),
    ("stern", "Sternperle",   _L_STERN, _K_STERN, "stern"),
]


def _esc(s) -> str:
    return _html.escape(str(s))


def _knoten(sphere: dict, x: float, y: float, farbe_key: str,
            rolle_zeigen: bool) -> str:
    hell, dunkel, akzent = _FARBE[farbe_key]
    tor, linie = sphere["tor"], sphere["linie"]
    name = sphere["sphaere"]
    rolle = _ROLLE.get(name, "")
    rollenzeile = (
        f'<text x="{x}" y="{y+87}" text-anchor="middle" class=sr>'
        f'{_esc(rolle)}</text>') if rolle_zeigen else ""
    return (
        f'<g class=knoten>'
        f'<circle cx="{x}" cy="{y}" r="46" fill="url(#g{farbe_key})" '
        f'stroke="{dunkel}" stroke-width="2"/>'
        f'<text x="{x}" y="{y+2}" text-anchor="middle" '
        f'class=tl>{tor}<tspan class=ln dy="-6">.{linie}</tspan></text>'
        f'<text x="{x}" y="{y+70}" text-anchor="middle" class=sn '
        f'fill="{akzent}">{_esc(name)}</text>'
        + rollenzeile + '</g>')


def _panel(tab_key: str, layout: dict, kanten: list, farbe_fix,
           by_name: dict, aktiv: bool, rolle_zeigen: bool) -> str:
    linien = []
    for a, b, seqfarbe in kanten:
        if a not in layout or b not in layout:
            continue
        fk = farbe_fix or seqfarbe
        x1, y1 = layout[a]
        x2, y2 = layout[b]
        _, dunkel, _ = _FARBE[fk]
        linien.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{dunkel}" stroke-width="3" opacity="0.5"/>')
    knoten = []
    for name, (x, y) in layout.items():
        s = by_name.get(name)
        if not s:
            continue
        fk = farbe_fix or _HEIMAT.get(name, "aktiv")
        knoten.append(_knoten(s, x, y, fk, rolle_zeigen))
    stil = "" if aktiv else "display:none"
    return (
        f'<svg class=mandala data-tab="{tab_key}" style="{stil}" '
        f'viewBox="0 0 1000 880" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="1000" height="880" fill="url(#flower)"/>'
        + "".join(linien) + "".join(knoten) + "</svg>")


def _deutung(pr: dict) -> str:
    """Ausfuehrliche Deutung unter dem Mandala -- je Sphaere ein warmer
    Absatz, gegliedert nach den vier Sequenzen (Aufbau wie das Original)."""
    from . import genekeys_texte as txt

    seqs = ("aktivierungssequenz", "venussequenz",
            "perlensequenz", "sternperle")
    teile = ["<section class=deutung><h2 class=dtitel>Deine Deutung</h2>"]
    for seq in seqs:
        titel, unter = txt.INTROS[seq]
        teile.append(f"<h3 class=seqh>{_esc(titel)}</h3>"
                     f"<p class=seqintro>{_esc(unter)}</p>")
        for s in pr[seq]:
            name = s["sphaere"]
            poet, rolle = txt.SPHAEREN.get(name, ("", ""))
            absatz = txt.TORE.get(s["tor"], "")
            teile.append(
                "<article class=dk>"
                "<div class=dh>"
                f"<span class=dtl>{s['tor']}<span class=dpt>.</span>"
                f"{s['linie']}</span>"
                f"<div><div class=dname>{_esc(name)}</div>"
                f"<div class=dsub>{_esc(poet)} · {_esc(rolle)}</div></div>"
                "</div>"
                + (f"<p class=dp>{_esc(absatz)}</p>" if absatz else "")
                + f"<p class=dhex>Tor {s['tor']} · I Ging: "
                f"{_esc(s['hexagramm'])}</p>"
                "</article>")
    teile.append("</section>")
    return "".join(teile)


def mandala_html(pr: dict, kopf: dict) -> bytes:
    """Baut die Mandala-Profilseite. `kopf` traegt Kopfzeilen + Umschalter."""
    by_name = {}
    for seq in ("aktivierungssequenz", "venussequenz",
                "perlensequenz", "sternperle"):
        for s in pr[seq]:
            by_name[s["sphaere"]] = s

    tabbtns = []
    panels = []
    for i, (key, titel, layout, kanten, farbe_fix) in enumerate(_TABS):
        erste = i == 0
        cls = "tab aktiv" if erste else "tab"
        tabbtns.append(
            f'<button class="{cls}" data-ziel="{key}" '
            f'onclick="gkTab(\'{key}\')">{_esc(titel)}</button>')
        # Im Vollprofil sitzen die Sphaeren dicht -- dort nur der Name,
        # sonst ueberlappt die Rollenzeile den naechsten Kreis.
        panels.append(_panel(key, layout, kanten, farbe_fix, by_name, erste,
                             rolle_zeigen=(key != "full")))

    pg = pr["prime_gifts"]
    grads = "".join(
        f'<radialGradient id="g{k}" cx="38%" cy="34%" r="70%">'
        f'<stop offset="0%" stop-color="{v[0]}"/>'
        f'<stop offset="100%" stop-color="{v[1]}"/></radialGradient>'
        for k, v in _FARBE.items())

    umschalt = ""
    if kopf.get("andere_url"):
        umschalt = (f' &nbsp;·&nbsp; <a href="{_esc(kopf["andere_url"])}">'
                    f'in {_esc(kopf["andere_kalender"])} zeigen</a>')

    roh = (
        "<!doctype html><html lang=de><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>Gene-Keys-Profil</title><style>"
        "*{box-sizing:border-box}"
        "body{font-family:'Cormorant Garamond',Georgia,serif;margin:0;"
        "background:#f4f1ec;color:#3a3730}"
        ".wrap{max-width:60rem;margin:0 auto;padding:1.5rem 1rem 3rem}"
        "h1{font-family:system-ui,sans-serif;font-weight:600;font-size:1.6rem;"
        "text-align:center;margin:.2rem 0;color:#4a4436;letter-spacing:.01em}"
        ".sub{font-family:system-ui,sans-serif;text-align:center;color:#8a8064;"
        "font-size:.9rem;margin-bottom:.2rem}"
        ".gifts{font-family:system-ui,sans-serif;text-align:center;"
        "color:#7a6f52;font-size:.85rem;margin:.1rem 0 1rem}"
        ".gifts b{color:#5a4f36}"
        ".tabs{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center;"
        "margin:1rem 0}"
        ".tab{font-family:system-ui,sans-serif;font-size:.85rem;cursor:pointer;"
        "border:1px solid #cfc6ad;background:#fbf9f3;color:#6a5f42;"
        "padding:.35rem .9rem;border-radius:2rem}"
        ".tab.aktiv{background:#6a5f42;color:#fbf9f3;border-color:#6a5f42}"
        ".buehne{position:relative;background:radial-gradient(circle at 50% 45%,"
        "#fdfcf9,#f0ece1);border:1px solid #e4ddc9;border-radius:1rem;"
        "padding:.5rem;box-shadow:0 2px 14px rgba(90,79,54,.08)}"
        ".mandala{width:100%;height:auto;display:block}"
        ".tl{font-family:system-ui,sans-serif;font-weight:700;font-size:30px;"
        "fill:#fff}"
        ".ln{font-size:17px;fill:#f3ece0}"
        ".sn{font-family:system-ui,sans-serif;font-weight:600;font-size:16px}"
        ".sr{font-family:system-ui,sans-serif;font-size:12px;fill:#9a8f72}"
        "nav{font-family:system-ui,sans-serif;font-size:.9rem;"
        "text-align:center;margin:.4rem 0 1rem}a{color:#7a5c1e}"
        ".deutung{margin-top:2.5rem}"
        ".dtitel{font-family:system-ui,sans-serif;font-size:1.4rem;"
        "text-align:center;color:#4a4436;margin:0 0 1.5rem;"
        "padding-top:1.5rem;border-top:1px solid #e4ddc9}"
        ".seqh{font-family:system-ui,sans-serif;font-size:1.15rem;"
        "color:#6a5f42;margin:2rem 0 .1rem}"
        ".seqintro{font-family:system-ui,sans-serif;font-size:.9rem;"
        "color:#8a8064;margin:0 0 1rem;font-style:italic}"
        ".dk{background:#fdfcf9;border:1px solid #e8e1d0;border-radius:.7rem;"
        "padding:1rem 1.2rem;margin:.8rem 0}"
        ".dh{display:flex;align-items:center;gap:.8rem;margin-bottom:.5rem}"
        ".dtl{font-family:system-ui,sans-serif;font-weight:700;font-size:1.5rem;"
        "color:#4a4436;background:#f0ece1;border-radius:.5rem;"
        "padding:.15rem .6rem;min-width:3.2rem;text-align:center}"
        ".dpt{color:#b7a97e}"
        ".dname{font-family:system-ui,sans-serif;font-weight:600;"
        "font-size:1.05rem;color:#4a4436}"
        ".dsub{font-family:system-ui,sans-serif;font-size:.82rem;color:#9a8f72}"
        ".dp{font-size:1.12rem;line-height:1.6;color:#3a3730;margin:.4rem 0}"
        ".dhex{font-family:system-ui,sans-serif;font-size:.78rem;color:#a89c7e;"
        "margin:.3rem 0 0}"
        "@media print{.tabs{display:none}.mandala{display:block !important;"
        "page-break-after:always}nav{display:none}.dk{break-inside:avoid}}"
        "</style>"
        "<link rel=preconnect href='https://fonts.googleapis.com'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+"
        "Garamond:wght@500;600&display=swap' rel=stylesheet>"
        "</head><body><div class=wrap>"
        "<nav><a href='/'>← neues Profil</a>" + umschalt + "</nav>"
        "<h1>Gene-Keys-Profil</h1>"
        f"<p class=sub>{_esc(kopf['zeile'])}</p>"
        f"<p class=gifts>Profil <b>{_esc(pr['profil_linien'])}</b> &nbsp;·&nbsp; "
        f"Life's Work <b>{pg['lifes_work']}</b> · Evolution <b>{pg['evolution']}"
        f"</b> · Radiance <b>{pg['radiance']}</b> · Purpose <b>{pg['purpose']}"
        f"</b></p>"
        "<div class=tabs>" + "".join(tabbtns) + "</div>"
        "<div class=buehne>"
        f'<svg width="0" height="0"><defs>{grads}'
        '<pattern id="flower" width="120" height="104" '
        'patternUnits="userSpaceOnUse">'
        '<g fill="none" stroke="#e7e0cd" stroke-width="1">'
        '<circle cx="60" cy="52" r="34"/><circle cx="0" cy="52" r="34"/>'
        '<circle cx="120" cy="52" r="34"/><circle cx="30" cy="0" r="34"/>'
        '<circle cx="90" cy="0" r="34"/><circle cx="30" cy="104" r="34"/>'
        '<circle cx="90" cy="104" r="34"/></g></pattern></defs></svg>'
        + "".join(panels) +
        "</div>"
        f"<p class=sub style='margin-top:1rem'>Design-Moment "
        f"{_esc(kopf['design_datum'])} · Sonne 88° vor der Geburt</p>"
        + _deutung(pr) +
        "</div>"
        "<script>function gkTab(z){"
        "document.querySelectorAll('.mandala').forEach(function(m){"
        "m.style.display=(m.dataset.tab===z)?'block':'none';});"
        "document.querySelectorAll('.tab').forEach(function(t){"
        "t.classList.toggle('aktiv',t.dataset.ziel===z);});}</script>"
        "</body></html>")
    return roh.encode("utf-8")
