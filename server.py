"""Gene-Keys-Profil -- eigenstaendiger Server.

Drei Routen, sonst nichts:

  GET /                    das Eingabeformular (web/genekeys.html)
  GET /genekeys-daten?...  das Profil als JSON
  GET /genekeys-mandala?.. das Profil als Rad + ausfuehrliche Deutung

Parameter fuer die beiden letzten: datum=TT.MM.JJJJ, zeit=HH:MM,
zone=<IANA-Zeitzonenname, Vorgabe Europe/Berlin>.

Start: python server.py [--port 8000]
"""
from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from genekeys import gene_keys, genekeys_web, zeit


class ApiFehler(ValueError):
    pass


def _eingabe_lesen(p: dict) -> tuple[float, dict]:
    try:
        tag, monat, jahr = (int(x) for x in p["datum"].split("."))
        stunde, minute = (int(x) for x in p["zeit"].split(":"))
    except (KeyError, ValueError):
        raise ApiFehler("datum als TT.MM.JJJJ und zeit als HH:MM angeben")
    zone = p.get("zone", "Europe/Berlin")
    try:
        jd = zeit.lokal_zu_jd_ut(jahr, monat, tag, stunde, minute, zone=zone)
    except ValueError as e:
        raise ApiFehler(str(e))
    m = {"tag": tag, "monat": monat, "jahr": jahr, "stunde": stunde,
         "minute": minute, "zone": zone}
    return jd, m


def genekeys_berechnen(p: dict) -> dict:
    jd, m = _eingabe_lesen(p)
    pr = gene_keys.profil(jd)
    return {"eingabe": {"datum": f"{m['tag']:02d}.{m['monat']:02d}.{m['jahr']}",
                        "zeit": f"{m['stunde']:02d}:{m['minute']:02d}",
                        "zone": m["zone"]}, **pr}


def genekeys_mandala_html(p: dict) -> bytes:
    jd, m = _eingabe_lesen(p)
    pr = gene_keys.profil(jd)
    d_jahr, d_monat, d_tag, _ = _gregorianisch_aus_jd(pr["design_jd"])
    kopf = {
        "zeile": (f"{m['tag']:02d}.{m['monat']:02d}.{m['jahr']} · "
                 f"{m['stunde']:02d}:{m['minute']:02d} · {m['zone']}"),
        "design_datum": f"{int(d_tag):02d}.{int(d_monat):02d}.{int(d_jahr)}",
    }
    return genekeys_web.mandala_html(pr, kopf)


def _gregorianisch_aus_jd(jd: float) -> tuple[int, int, int, float]:
    """Gregorianisches Kalenderdatum (Jahr, Monat, Tag, Stunde) aus JD."""
    import math
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


class Handler(BaseHTTPRequestHandler):
    def _antworten(self, status: int, daten: dict) -> None:
        roh = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def _html(self, status: int, roh: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def do_GET(self) -> None:
        url = urlparse(self.path)
        p = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                datei = os.path.join(os.path.dirname(__file__), "web",
                                     "genekeys.html")
                with open(datei, "rb") as f:
                    self._html(200, f.read())
            elif url.path == "/genekeys-daten":
                self._antworten(200, genekeys_berechnen(p))
            elif url.path == "/genekeys-mandala":
                self._html(200, genekeys_mandala_html(p))
            elif url.path == "/gesund":
                self._antworten(200, {"status": "ok"})
            else:
                self._antworten(404, {"fehler": "unbekannter Pfad"})
        except ApiFehler as e:
            self._antworten(400, {"fehler": str(e)})
        except Exception as e:  # noqa: BLE001 -- letzte Sicherung fuer den Handler
            self._antworten(500, {"fehler": f"interner Fehler: {e}"})

    def log_message(self, format, *args):  # ruhiger Log, eine Zeile je Anfrage
        print(f"{self.address_string()} - {format % args}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="gene-keys-profile")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Gene-Keys-Profil laeuft auf http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
