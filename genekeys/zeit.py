"""Lokale Uhrzeit + IANA-Zeitzone -> julianisches Datum in UT.

Gene Keys ist eigentlich auf das buergerliche (gregorianische) Datum
definiert -- das bleibt die Vorgabe. Wer aber mit der AstroChing-
Konvention rechnet (Datum julianisch statt gregorianisch gedeutet, seit
1900 ein Versatz von genau 13 Tagen: 16.03.2006 julianisch =
29.03.2006 gregorianisch), kann kalender="julianisch" waehlen.
"""
from __future__ import annotations

import math
from datetime import datetime
from zoneinfo import ZoneInfo


def julianisches_datum(jahr: int, monat: int, tag: int, stunde: float = 0.0,
                       kalender: str = "gregorianisch") -> float:
    """Julianisches Datum (JD) aus einem Kalenderdatum in Weltzeit.

    Standardformel (Fliegel & van Flandern / Meeus), gemeinfrei.
    kalender: "gregorianisch" (Standard) oder "julianisch" (AstroChing).
    """
    if monat <= 2:
        jahr, monat = jahr - 1, monat + 12
    if kalender == "gregorianisch":
        a = jahr // 100
        b = 2 - a + a // 4
    elif kalender == "julianisch":
        b = 0
    else:
        raise ValueError(f"unbekannter Kalender: {kalender!r}")
    return (int(365.25 * (jahr + 4716)) + int(30.6001 * (monat + 1))
            + tag + b - 1524.5 + stunde / 24.0)


def gregorianisch_aus_jd(jd: float) -> tuple[int, int, int, float]:
    """Gregorianisches Kalenderdatum (Jahr, Monat, Tag, Stunde) aus einem JD."""
    z = math.floor(jd + 0.5)
    f = jd + 0.5 - z
    if z >= 2299161:
        a = math.floor((z - 1867216.25) / 36524.25)
        A = z + 1 + a - a // 4
    else:
        A = z
    B = A + 1524
    C = math.floor((B - 122.1) / 365.25)
    D = math.floor(365.25 * C)
    E = math.floor((B - D) / 30.6001)
    tag = B - D - math.floor(30.6001 * E)
    monat = E - 1 if E < 14 else E - 13
    jahr = C - 4716 if monat > 2 else C - 4715
    return int(jahr), int(monat), int(tag), f * 24.0


def lokal_zu_jd_ut(jahr: int, monat: int, tag: int, stunde: int,
                   minute: int = 0, zone: str = "Europe/Berlin",
                   kalender: str = "gregorianisch") -> float:
    """Lokale Uhrzeit an einem Datum -> julianisches Datum in UT.

    zone -- IANA-Zeitzonenname, z. B. "Europe/Berlin", "America/New_York".
    kalender -- "gregorianisch" oder "julianisch" (siehe Moduldoku).

    Bei julianischer Deutung wird das DATUM ins Gregorianische geschoben,
    die UHRZEIT bleibt die eingetragene Uhrzeit am verschobenen Datum.

    Der Zeitzonen-Versatz richtet sich dabei nach dem EINGETRAGENEN Datum,
    nicht nach dem verschobenen: 16.03.2006 14:14 julianisch traegt die
    Winterzeit des 16. Maerz (MEZ), obwohl der gerechnete 29.03.2006
    bereits in der Sommerzeit liegt. Andersherum laege man eine Stunde
    daneben -- beim schnellen Mond reicht das fuer eine falsche Linie.
    """
    jd_mitternacht = julianisches_datum(jahr, monat, tag, 0.0, kalender)
    gj, gm, gt, _ = gregorianisch_aus_jd(jd_mitternacht)
    try:
        versatz = datetime(jahr, monat, tag, stunde, minute,
                           tzinfo=ZoneInfo(zone)).utcoffset()
    except ValueError:
        # Eingetragenes Datum gibt es gregorianisch nicht (z. B. 29.02. in
        # einem nur julianischen Schaltjahr) -- dann der Versatz des
        # verschobenen Datums.
        try:
            versatz = datetime(gj, gm, gt, stunde, minute,
                               tzinfo=ZoneInfo(zone)).utcoffset()
        except ValueError as e:
            raise ValueError(f"Datum/Zeit ungueltig: {e}")
    try:
        utc = datetime(gj, gm, gt, stunde, minute) - versatz
    except ValueError as e:
        raise ValueError(f"Datum/Zeit ungueltig: {e}")
    stunde_dezimal = (utc.hour + utc.minute / 60.0
                      + (utc.second + utc.microsecond / 1e6) / 3600.0)
    return julianisches_datum(utc.year, utc.month, utc.day, stunde_dezimal)
