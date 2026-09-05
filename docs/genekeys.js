/*
 * genekeys.js -- das Rad, der Design-Zeitpunkt-Solver, der Sphaeren-Plan.
 *
 * 1:1-Portierung der Logik aus genekeys/gene_keys.py (Python-Version
 * dieses Projekts) nach JavaScript, damit sie im Browser ohne Server
 * laufen kann. Nur die Ephemeride darunter ist anders (siehe
 * ephemeris.js) -- Rad, Formeln und Sphaeren-Plan sind identisch.
 */

const BASIS = 302.0;
const TOR_BREITE = 360.0 / 64;
const LINIE_BREITE = TOR_BREITE / 6;

const WHEEL = [
  41, 19, 13, 49, 30, 55, 37, 63, 22, 36,
  25, 17, 21, 51, 42, 3, 27, 24, 2, 23,
  8, 20, 16, 35, 45, 12, 15, 52, 39, 53,
  62, 56, 31, 33, 7, 4, 29, 59, 40, 64,
  47, 6, 46, 18, 48, 57, 32, 50, 28, 44,
  1, 43, 14, 34, 9, 5, 26, 11, 10, 58,
  38, 54, 61, 60,
];

function torLinie(laenge) {
  const versatz = ((laenge - BASIS) % 360 + 360) % 360;
  const schlitz = Math.floor(versatz / LINIE_BREITE); // 0..383
  const tor = WHEEL[Math.floor(schlitz / 6)];
  const linie = (schlitz % 6) + 1;
  return { tor, linie };
}

function sonneLaenge(jd) {
  return planetLaenge(jd, "sonne");
}

function deltaGrad(jd, ziel) {
  return ((sonneLaenge(jd) - ziel + 180) % 360 + 360) % 360 - 180;
}

function designJd(jdGeburt) {
  const ziel = ((sonneLaenge(jdGeburt) - 88.0) % 360 + 360) % 360;
  let jd = jdGeburt;
  let davor = deltaGrad(jd, ziel);
  const ende = jdGeburt - 100.0;
  while (jd > ende) {
    jd -= 1.0;
    const jetzt = deltaGrad(jd, ziel);
    if ((jetzt > 0) !== (davor > 0) && Math.abs(jetzt - davor) < 90.0) {
      let lo = jd, hi = jd + 1.0;
      for (let i = 0; i < 60; i++) {
        const mitte = (lo + hi) / 2.0;
        if ((deltaGrad(mitte, ziel) > 0) === (deltaGrad(lo, ziel) > 0)) {
          lo = mitte;
        } else {
          hi = mitte;
        }
      }
      return (lo + hi) / 2.0;
    }
    davor = jetzt;
  }
  throw new Error("Design-Moment nicht gefunden");
}

const AKTIVIERUNG = [
  ["Life's Work", "P", "sonne"],
  ["Evolution", "P", "erde"],
  ["Radiance", "D", "sonne"],
  ["Purpose", "D", "erde"],
];
const VENUS = [
  ["Attraction", "D", "mond"],
  ["IQ", "P", "venus"],
  ["EQ", "P", "mars"],
  ["SQ", "D", "venus"],
  ["Core", "D", "mars"],
];
const PERLE = [
  ["Vocation", "D", "mars"],
  ["Culture", "D", "jupiter"],
  ["Brand", "P", "sonne"],
  ["Pearl", "P", "jupiter"],
];
const STERN = [
  ["Creativity", "D", "uranus"],
  ["Relating", "P", "merkur"],
  ["Stability", "D", "saturn"],
];

function laengeVon(jd, koerper) {
  if (koerper === "erde") {
    return (planetLaenge(jd, "sonne") + 180) % 360;
  }
  return planetLaenge(jd, koerper);
}

function sphaere(name, zeit, koerper, jdP, jdD, namen) {
  const jd = zeit === "P" ? jdP : jdD;
  const laenge = laengeVon(jd, koerper);
  const { tor, linie } = torLinie(laenge);
  return {
    sphaere: name,
    seite: zeit === "P" ? "Persoenlichkeit" : "Design",
    koerper, laenge: Math.round(laenge * 10000) / 10000,
    tor, linie, profil: `${tor}.${linie}`,
    hexagramm: namen[tor],
  };
}

function genekeysProfil(jdGeburt, namen) {
  const jdP = jdGeburt;
  const jdD = designJd(jdGeburt);
  const bau = plan => plan.map(([n, z, k]) => sphaere(n, z, k, jdP, jdD, namen));

  const aktiv = bau(AKTIVIERUNG);
  const venus = bau(VENUS);
  const perle = bau(PERLE);
  const stern = bau(STERN);

  const pSonne = aktiv[0].linie;
  const dSonne = aktiv[2].linie;

  return {
    designJd: jdD,
    profilLinien: `${pSonne}/${dSonne}`,
    aktivierungssequenz: aktiv,
    venussequenz: venus,
    perlensequenz: perle,
    sternperle: stern,
    primeGifts: {
      lifesWork: aktiv[0].profil, evolution: aktiv[1].profil,
      radiance: aktiv[2].profil, purpose: aktiv[3].profil,
    },
  };
}

// -------------------------------------------------- Datum -> Julianisches Datum
//
// Lokale Uhrzeit in einer IANA-Zeitzone -> UT-Millisekunden, per
// Intl.DateTimeFormat-Rueckrechnung (der uebliche Weg, weil das native
// Date-Objekt keine "baue mir eine Zeit in Zone X"-Funktion hat).
function lokalZuUtcMillis(jahr, monat, tag, stunde, minute, zone) {
  // Zieldigits als UTC-Zahlwert -- fester Bezugspunkt, NIE veraendert.
  const zielAlsUtcDigits = Date.UTC(jahr, monat - 1, tag, stunde, minute);
  let kandidat = zielAlsUtcDigits;
  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
  for (let i = 0; i < 3; i++) {
    const teile = fmt.formatToParts(new Date(kandidat));
    const hole = t => parseInt(teile.find(p => p.type === t).value, 10);
    const gelesenAlsUtc = Date.UTC(hole("year"), hole("month") - 1, hole("day"),
                                   hole("hour"), hole("minute"), hole("second"));
    // Zonenversatz beim aktuellen Kandidaten (ms). Der naechste Kandidat
    // wird IMMER vom festen Ziel aus neu berechnet -- sonst akkumuliert
    // sich der Versatz Runde um Runde (der eigentliche Fehler hier war
    // genau das: += statt Neuberechnung ab dem festen Bezugspunkt).
    const versatz = gelesenAlsUtc - kandidat;
    const naechster = zielAlsUtcDigits - versatz;
    if (naechster === kandidat) break;
    kandidat = naechster;
  }
  return kandidat;
}

function julianischesDatumAusUnix(millisUtc) {
  return millisUtc / 86400000 + 2440587.5;
}

// Julianisches Datum aus Kalenderdigits, mit Kalenderwahl (gemeinfreie
// Fliegel/van-Flandern-Formel, gleiche Konvention wie genekeys/zeit.py).
// kalender: "gregorianisch" (Standard) oder "julianisch" (AstroChing,
// seit 1900 ein Versatz von 13 Tagen zum buergerlichen Datum).
function julianischesDatumFormel(jahr, monat, tag, stundeDezimal, kalender) {
  if (monat <= 2) { jahr -= 1; monat += 12; }
  let b;
  if (kalender === "julianisch") {
    b = 0;
  } else {
    const a = Math.floor(jahr / 100);
    b = 2 - a + Math.floor(a / 4);
  }
  return (Math.floor(365.25 * (jahr + 4716)) + Math.floor(30.6001 * (monat + 1))
    + tag + b - 1524.5 + stundeDezimal / 24.0);
}

// Geburts-JD (UT) aus lokalem Datum/Uhrzeit/Zone/Kalender -- mirror von
// zeit.lokal_zu_jd_ut(): bei julianischer Deutung wird das DATUM zuerst
// ins Gregorianische geschoben, die Zeitzone gilt fuer den verschobenen
// (gregorianischen) Moment, weil nur dafuer echte DST-Regeln existieren.
function geburtsJdBerechnen(jahr, monat, tag, stunde, minute, zone, kalender) {
  const jdMitternacht = julianischesDatumFormel(jahr, monat, tag, 0.0, kalender);
  const g = gregorianischAusJd(jdMitternacht);
  const millis = lokalZuUtcMillis(g.jahr, g.monat, g.tag, stunde, minute, zone);
  const d = new Date(millis);
  const stundeUtDezimal = d.getUTCHours() + d.getUTCMinutes() / 60
    + (d.getUTCSeconds() + d.getUTCMilliseconds() / 1000) / 3600;
  return julianischesDatumFormel(d.getUTCFullYear(), d.getUTCMonth() + 1,
    d.getUTCDate(), stundeUtDezimal, "gregorianisch");
}

function gregorianischAusJd(jd) {
  const z = Math.floor(jd + 0.5);
  const f = jd + 0.5 - z;
  let A;
  if (z >= 2299161) {
    const a = Math.floor((z - 1867216.25) / 36524.25);
    A = z + 1 + a - Math.floor(a / 4);
  } else {
    A = z;
  }
  const B = A + 1524;
  const C = Math.floor((B - 122.1) / 365.25);
  const D = Math.floor(365.25 * C);
  const E = Math.floor((B - D) / 30.6001);
  const tag = B - D - Math.floor(30.6001 * E);
  const monat = E < 14 ? E - 1 : E - 13;
  const jahr = monat > 2 ? C - 4716 : C - 4715;
  return { jahr, monat, tag };
}
