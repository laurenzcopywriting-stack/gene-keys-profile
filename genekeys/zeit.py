"""Lokale Uhrzeit + IANA-Zeitzone -> julianisches Datum in UT.

Gene Keys rechnet immer mit dem buergerlichen (gregorianischen) Datum --
anders als manche Astrologie-Systeme gibt es hier keine Kalendervarianten
zu unterscheiden. Darum bewusst schlank gehalten: keine Kalenderauswahl,
kein Ortsnachschlag -- nur Datum, Uhrzeit und Zeitzonenname.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def julianisches_datum(jahr: int, monat: int, tag: int, stunde: float = 0.0) -> float:
    """Julianisches Datum (JD) aus einem gregorianischen Datum in Weltzeit.

    Standardformel (Fliegel & van Flandern / Meeus), gemeinfrei.
    """
    if monat <= 2:
        jahr, monat = jahr - 1, monat + 12
    a = jahr // 100
    b = 2 - a + a // 4
    return (int(365.25 * (jahr + 4716)) + int(30.6001 * (monat + 1))
            + tag + b - 1524.5 + stunde / 24.0)


def lokal_zu_jd_ut(jahr: int, monat: int, tag: int, stunde: int,
                   minute: int = 0, zone: str = "Europe/Berlin") -> float:
    """Lokale Uhrzeit an einem Datum -> julianisches Datum in UT.

    zone -- IANA-Zeitzonenname, z. B. "Europe/Berlin", "America/New_York".
    """
    try:
        lokal = datetime(jahr, monat, tag, stunde, minute, tzinfo=ZoneInfo(zone))
    except ValueError as e:
        raise ValueError(f"Datum/Zeit ungueltig: {e}")
    utc = lokal.astimezone(ZoneInfo("UTC"))
    stunde_dezimal = (utc.hour + utc.minute / 60.0
                      + (utc.second + utc.microsecond / 1e6) / 3600.0)
    return julianisches_datum(utc.year, utc.month, utc.day, stunde_dezimal)
