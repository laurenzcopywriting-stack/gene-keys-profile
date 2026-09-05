"""Planeten-Ekliptiklaengen -- ausschliesslich mit permissiv lizenzierten
Bibliotheken (Skyfield/MIT, DE421/gemeinfrei). Kein Swiss Ephemeris.

Auf das Minimum gekuerzt, das das Gene-Keys-Profil braucht: die scheinbare
geozentrische Ekliptiklaenge eines Planeten zu einem Zeitpunkt. Herausgeloest
aus einer groesseren Astrologie-Engine, die noch Haeuser, Aspekte, Fixsterne
usw. rechnet -- das alles ist hier bewusst nicht mitgekommen.
"""
from __future__ import annotations

import os

from skyfield.api import load, load_file
from skyfield.framelib import ecliptic_frame
from skyfield_data import get_skyfield_data_path

_eph = None
_ts = None


def _laden():
    """Laedt Ephemeride und Zeitskala. Standard: DE421 (1899-2053), im
    skyfield-data-Paket enthalten -- keine eigene .bsp-Datei noetig."""
    global _eph, _ts
    if _eph is None:
        pfad = os.path.join(get_skyfield_data_path(), "de421.bsp")
        _eph = load_file(pfad)
        _ts = load.timescale(builtin=True)
    return _eph, _ts


def _norm(grad: float) -> float:
    return grad % 360.0


# Je Objekt eine Kandidatenliste, falls eine Ephemeride nur das Baryzentrum
# statt des Planetenkoerpers fuehrt (bei den hier genutzten Planeten macht
# das keinen praktischen Unterschied).
PLANETEN = {
    "sonne": ("sun",), "mond": ("moon",), "merkur": ("mercury",),
    "venus": ("venus",), "mars": ("mars", "mars barycenter"),
    "jupiter": ("jupiter barycenter",), "saturn": ("saturn barycenter",),
    "uranus": ("uranus barycenter",),
}


def _ziel(eph, name: str):
    for schluessel in PLANETEN[name]:
        try:
            return eph[schluessel]
        except KeyError:
            continue
    raise KeyError(f"Ephemeride enthaelt kein Ziel fuer {name!r}")


def planet_laenge(jd_ut: float, name: str) -> tuple[float, float]:
    """Scheinbare geozentrische Laenge und Breite eines Planeten in Grad."""
    eph, ts = _laden()
    t = ts.ut1_jd(jd_ut)
    lat, lon, _ = (eph["earth"].at(t).observe(_ziel(eph, name))
                   .apparent().frame_latlon(ecliptic_frame))
    return _norm(lon.degrees), lat.degrees
