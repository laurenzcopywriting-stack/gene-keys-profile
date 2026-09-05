"""Das Gene-Keys-Profil (Hologenetisches Profil) -- eigene Berechnung.

WOZU DAS HIER

Gene Keys (Richard Rudd) und Human Design (Ra Uru Hu) legen dieselben 64
I-Ging-Hexagramme als "Tore" auf die Ekliptik. Ein Profil besteht aus
Sphaeren; jede Sphaere ist die Stellung eines bestimmten Planeten,
ausgedrueckt als Tor.Linie (z. B. 36.4 = Tor 36, Linie 4).

Zwei Zeitpunkte spielen mit:

  * Persoenlichkeit (bewusst)  -- der Geburtsmoment selbst.
  * Design (unbewusst)         -- der Moment, in dem die Sonne genau
                                  88 Bogengrad VOR der Geburt stand,
                                  rund 88 Tage frueher.

GERECHNET, NICHT UEBERNOMMEN

Diese Datei rechnet nur die Zahlen: aus den Ephemeriden die
Ekliptiklaenge jedes Planeten, daraus Tor und Linie ueber das feste
Rave-Mandala (Tor 41 beginnt bei 2 Grad Wassermann = 302 Grad, jedes Tor
5.625 Grad, jede Linie 0.9375 Grad). Die Tor-Namen sind die klassischen,
gemeinfreien I-Ging-Hexagrammnamen -- NICHT die geschuetzte
Schatten/Gabe/Siddhi-Sprache von Gene Keys. Wer die Rudd-Deutung will,
schlaegt sie mit der Tor-Nummer dort nach.

Belegt an einem realen Profil (16.03.2006 14:14 Kronach, gregorianisch):
Life's Work 36.4, Evolution 6.4, Radiance 11.6, Purpose 12.6 -- alle vier
kommen mit diesem Rad und dieser Linienformel exakt heraus.
"""
from __future__ import annotations

from . import kern

# --------------------------------------------------------------- Das Rad
#
# Reihenfolge der Tore, wie sie mit STEIGENDER Ekliptiklaenge auftreten,
# beginnend bei 302 Grad (2 Grad Wassermann). WHEEL[i] ist das Tor im
# i-ten 5.625-Grad-Segment ab 302 Grad. Feste Permutation aller 64 Tore
# aus dem Human-Design-Mandala.
BASIS = 302.0                 # Grad: Beginn von Tor 41
TOR_BREITE = 360.0 / 64       # 5.625 Grad je Tor
LINIE_BREITE = TOR_BREITE / 6 # 0.9375 Grad je Linie

WHEEL = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36,
    25, 17, 21, 51, 42,  3, 27, 24,  2, 23,
     8, 20, 16, 35, 45, 12, 15, 52, 39, 53,
    62, 56, 31, 33,  7,  4, 29, 59, 40, 64,
    47,  6, 46, 18, 48, 57, 32, 50, 28, 44,
     1, 43, 14, 34,  9,  5, 26, 11, 10, 58,
    38, 54, 61, 60,
]

# Klassische I-Ging-Hexagrammnamen (King-Wen, gemeinfrei). Tor-Nummer =
# Hexagramm-Nummer = Gene-Key-Nummer.
NAMEN = {
    1: "Das Schoepferische", 2: "Das Empfangende", 3: "Die Anfangsschwierigkeit",
    4: "Die Jugendtorheit", 5: "Das Warten", 6: "Der Streit", 7: "Das Heer",
    8: "Das Zusammenhalten", 9: "Des Kleinen Zaehmungskraft", 10: "Das Auftreten",
    11: "Der Friede", 12: "Die Stockung", 13: "Gemeinschaft mit Menschen",
    14: "Der Besitz von Grossem", 15: "Die Bescheidenheit", 16: "Die Begeisterung",
    17: "Die Nachfolge", 18: "Die Arbeit am Verdorbenen", 19: "Die Annaeherung",
    20: "Die Betrachtung", 21: "Das Durchbeissen", 22: "Die Anmut",
    23: "Die Zersplitterung", 24: "Die Wiederkehr", 25: "Die Unschuld",
    26: "Des Grossen Zaehmungskraft", 27: "Die Ernaehrung", 28: "Des Grossen Uebergewicht",
    29: "Das Abgruendige", 30: "Das Haftende", 31: "Die Einwirkung", 32: "Die Dauer",
    33: "Der Rueckzug", 34: "Des Grossen Macht", 35: "Der Fortschritt",
    36: "Die Verfinsterung des Lichts", 37: "Die Sippe", 38: "Der Gegensatz",
    39: "Das Hemmnis", 40: "Die Befreiung", 41: "Die Minderung", 42: "Die Mehrung",
    43: "Der Durchbruch", 44: "Das Entgegenkommen", 45: "Die Sammlung",
    46: "Das Empordringen", 47: "Die Bedraengnis", 48: "Der Brunnen",
    49: "Die Umwaelzung", 50: "Der Tiegel", 51: "Das Erregende", 52: "Das Stillehalten",
    53: "Die Entwicklung", 54: "Das heiratende Maedchen", 55: "Die Fuelle",
    56: "Der Wanderer", 57: "Das Sanfte", 58: "Das Heitere", 59: "Die Aufloesung",
    60: "Die Beschraenkung", 61: "Innere Wahrheit", 62: "Des Kleinen Uebergewicht",
    63: "Nach der Vollendung", 64: "Vor der Vollendung",
}


def tor_linie(laenge: float) -> tuple[int, int]:
    """Ekliptiklaenge (Grad) -> (Tor 1..64, Linie 1..6)."""
    versatz = (laenge - BASIS) % 360.0
    schlitz = int(versatz / LINIE_BREITE)      # 0..383
    tor = WHEEL[schlitz // 6]
    linie = schlitz % 6 + 1
    return tor, linie


# ------------------------------------------------------------ Design-Zeit
#
# Der Design-Moment liegt dort, wo die Sonne genau 88 Grad VOR ihrer
# Geburtslaenge stand. Die Sonne braucht dafuer rund 88-89 Tage. Wir
# suchen rueckwaerts in Tagesschritten den Vorzeichenwechsel und
# verfeinern per Bisektion.

def _sonne(jd: float) -> float:
    return kern.planet_laenge(jd, "sonne")[0]


def _delta(jd: float, ziel: float) -> float:
    """Vorzeichenbehafteter Abstand der Sonne zu ziel, -180..180 Grad."""
    return (_sonne(jd) - ziel + 180.0) % 360.0 - 180.0


def design_jd(jd_geburt: float) -> float:
    """Julianisches Datum des Design-Moments (Sonne 88 Grad zurueck)."""
    ziel = (_sonne(jd_geburt) - 88.0) % 360.0
    jd = jd_geburt
    davor = _delta(jd, ziel)
    ende = jd_geburt - 100.0
    while jd > ende:
        jd -= 1.0
        jetzt = _delta(jd, ziel)
        if (jetzt > 0) != (davor > 0) and abs(jetzt - davor) < 90.0:
            lo, hi = jd, jd + 1.0
            for _ in range(60):
                mitte = (lo + hi) / 2.0
                if (_delta(mitte, ziel) > 0) == (_delta(lo, ziel) > 0):
                    lo = mitte
                else:
                    hi = mitte
            return (lo + hi) / 2.0
        davor = jetzt
    raise ValueError("Design-Moment nicht gefunden")


# --------------------------------------------------------- Sphaeren-Plan
#
# Jede Sphaere ist ein (Zeit, Koerper). Zeit: "P" = Persoenlichkeit
# (Geburt), "D" = Design. Koerper "erde" = Sonne + 180 Grad (die Erde
# steht der geozentrischen Sonne gegenueber). Die Reihenfolge folgt den
# vier Sequenzen des Golden Path.

_AKTIVIERUNG = [
    ("Life's Work", "P", "sonne"),
    ("Evolution",   "P", "erde"),
    ("Radiance",    "D", "sonne"),
    ("Purpose",     "D", "erde"),
]
_VENUS = [
    ("Attraction",  "D", "mond"),
    ("IQ",          "P", "venus"),
    ("EQ",          "P", "mars"),
    ("SQ",          "D", "venus"),
    ("Core",        "D", "mars"),
]
_PERLE = [
    ("Vocation",    "D", "mars"),     # selber Punkt wie Core
    ("Culture",     "D", "jupiter"),
    ("Brand",       "P", "sonne"),    # selber Punkt wie Life's Work
    ("Pearl",       "P", "jupiter"),
]
_STERN = [
    ("Creativity",  "D", "uranus"),
    ("Relating",    "P", "merkur"),
    ("Stability",   "D", "saturn"),
]


def _laenge(jd: float, koerper: str) -> float:
    if koerper == "erde":
        return (kern.planet_laenge(jd, "sonne")[0] + 180.0) % 360.0
    return kern.planet_laenge(jd, koerper)[0]


def _sphaere(name: str, zeit: str, koerper: str,
             jd_p: float, jd_d: float) -> dict:
    jd = jd_p if zeit == "P" else jd_d
    laenge = _laenge(jd, koerper)
    tor, linie = tor_linie(laenge)
    return {
        "sphaere": name,
        "seite": "Persoenlichkeit" if zeit == "P" else "Design",
        "koerper": koerper,
        "laenge": round(laenge, 4),
        "tor": tor,
        "linie": linie,
        "profil": f"{tor}.{linie}",
        "hexagramm": NAMEN[tor],
    }


def profil(jd_geburt: float) -> dict:
    """Vollstaendiges Gene-Keys-Profil zu einem Geburts-JD (UT)."""
    jd_p = jd_geburt
    jd_d = design_jd(jd_geburt)

    def bau(plan):
        return [_sphaere(n, z, k, jd_p, jd_d) for (n, z, k) in plan]

    aktiv = bau(_AKTIVIERUNG)
    venus = bau(_VENUS)
    perle = bau(_PERLE)
    stern = bau(_STERN)

    # Das Profil im Human-Design-Sinn: Linie der Persoenlichkeits-Sonne
    # ueber der Linie der Design-Sonne (z. B. 4/6).
    p_sonne = aktiv[0]["linie"]
    d_sonne = aktiv[2]["linie"]

    return {
        "system": "Gene Keys / Golden Path",
        "design_jd": round(jd_d, 6),
        "profil_linien": f"{p_sonne}/{d_sonne}",
        "aktivierungssequenz": aktiv,
        "venussequenz": venus,
        "perlensequenz": perle,
        "sternperle": stern,
        "prime_gifts": {
            "lifes_work": aktiv[0]["profil"],
            "evolution": aktiv[1]["profil"],
            "radiance": aktiv[2]["profil"],
            "purpose": aktiv[3]["profil"],
        },
    }
