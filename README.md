# Gene-Keys-Profil

**Live: https://laurenzcopywriting-stack.github.io/gene-keys-profile/**
(laeuft komplett im Browser, keine Installation noetig)

Eine eigenstaendige, kleine Web-App, die das Gene-Keys- / Human-Design-
Hologenetische-Profil aus Geburtsdatum, -uhrzeit und Zeitzone berechnet und
als Rad ("Mandala") mit ausfuehrlicher Deutung darstellt.

Es gibt zwei Varianten in diesem Repo:

- **`docs/`** -- die Live-Version oben: reines JavaScript, laeuft direkt im
  Browser via GitHub Pages. Nutzt eine oeffentlich dokumentierte
  Naeherungsformel fuer Planetenpositionen (Schlyter-Methode, siehe
  `docs/ephemeris.js`) -- auf einige Bogenminuten genau.
- **`server.py` + `genekeys/`** -- die praezise Python-Version mit
  Skyfield/DE421 (Bogensekunden-Genauigkeit), zum lokalen Selbstbetrieb.
  Beide Varianten liefern an den getesteten Referenzdaten identische
  Tor.Linie-Werte.

## Was das ist

Gene Keys (Richard Rudd) und Human Design (Ra Uru Hu) legen dieselben 64
I-Ging-Hexagramme als "Tore" auf die Ekliptik. Ein Profil besteht aus
Sphaeren (Life's Work, Evolution, Radiance, Purpose, ...); jede Sphaere ist
die Stellung eines bestimmten Planeten zum Geburtsmoment oder zum
"Design"-Moment (Sonne 88 Grad vor der Geburt), ausgedrueckt als Tor.Linie.

## Wie es gerechnet wird

- **Ephemeride:** [Skyfield](https://rhodesmill.org/skyfield/) (MIT-Lizenz)
  mit der DE421-Planetenephemeride der NASA/JPL (gemeinfrei), ueber das
  `skyfield-data`-Paket bezogen -- keine Ephemeride-Datei im Repo noetig.
- **Das Rad:** feste 64-Tore-Anordnung (Rave-Mandala), Tor 41 beginnt bei
  2 Grad Wassermann, jedes Tor 5,625 Grad, jede Linie 0,9375 Grad.
- **Design-Zeitpunkt:** rueckwaerts gesucht per Bisektion, dort wo die
  Sonne exakt 88 Grad vor ihrer Geburtslaenge stand.
- **Sphaeren-Planeten:** Life's Work/Brand=Sonne, Evolution=Erde
  (Sonne+180 Grad), Radiance=Design-Sonne, Purpose=Design-Erde,
  Attraction=Design-Mond, IQ=Venus, EQ=Mars, SQ=Design-Venus,
  Core/Vocation=Design-Mars, Culture=Design-Jupiter, Pearl=Jupiter,
  Creativity=Design-Uranus, Relating=Merkur, Stability=Design-Saturn.

Alle Zahlen sind an einem realen, oeffentlich nachrechenbaren Profil belegt
(siehe `genekeys/gene_keys.py`).

## Was NICHT uebernommen ist

Die Tor-Namen sind die klassischen, **gemeinfreien** King-Wen-I-Ging-Namen
(z. B. "Das Schoepferische", "Die Verfinsterung des Lichts") -- **nicht**
die urheberrechtlich geschuetzte Schatten/Gabe/Siddhi-Sprache von Richard
Rudds Gene-Keys-Buch. Wer diese Deutung sucht, schlaegt sie mit der
Tor-Nummer im Original nach. Die hier gezeigten Deutungstexte sind eigene
Formulierungen auf Basis der klassischen I-Ging-Bildsprache.

Diese App ist eine **eigenstaendige Auskopplung** aus einer groesseren
Astrologie-Engine -- absichtlich ohne Zugriff auf deren andere Rechner
(Radix-Chart, Weltlinien, Transite usw.). Sie tut genau eine Sache.

## Installation & Start

```bash
pip install -r requirements.txt
python server.py
```

Dann `http://127.0.0.1:8000` im Browser oeffnen. Optional `--port` und
`--host` angeben.

## Aufbau

```
server.py                  HTTP-Server, drei Routen (/, /genekeys-daten, /genekeys-mandala)
genekeys/
  kern.py                  Planeten-Ekliptiklaenge via Skyfield/DE421
  gene_keys.py              Rad, Design-Zeitpunkt-Solver, Sphaeren-Plan
  genekeys_texte.py          64 Deutungstexte + Sphaeren-Beschreibungen
  genekeys_web.py            Mandala-Rendering (SVG) + Deutungsseite (HTML)
  zeit.py                    lokale Zeit + IANA-Zeitzone -> julianisches Datum
web/genekeys.html          Eingabeformular
```

## Lizenz

Der Code steht unter der MIT-Lizenz (siehe `LICENSE`). Die verwendeten
I-Ging-Hexagrammnamen sind jahrhundertealtes Gemeingut. Skyfield ist
MIT-lizenziert, die DE421-Ephemeride ist ein gemeinfreies NASA/JPL-Produkt.
