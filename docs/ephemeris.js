/*
 * Ephemeris.js -- geozentrische Ekliptiklaengen im Browser, ohne Server.
 *
 * WOZU DAS HIER
 *
 * Die GitHub-Pages-Version dieser Seite hat keinen Python-Server und
 * keine Skyfield/DE421-Ephemeride zur Verfuegung -- alles laeuft im
 * Browser. Dieses Modul rechnet darum mit der klassischen Methode von
 * Paul Schlyter ("How to compute planetary positions",
 * https://stjarnhimlen.se/comp/ppcomp.html, gemeinfrei, seit Jahrzehnten
 * frei genutzte Formelsammlung): feste Kepler-Bahnelemente je Planet plus
 * ein paar Stoerungsterme fuer Mond, Jupiter, Saturn, Uranus.
 *
 * GENAUIGKEIT
 *
 * Damit erreichte Laengen liegen typischerweise innerhalb einer
 * Bogenminute (Mond, innere Planeten) bis wenigen Bogenminuten
 * (Jupiter/Saturn/Uranus) der wahren Position -- weit innerhalb der
 * 0,9375-Grad-Breite einer Gene-Keys-Linie. Das ist NICHT dieselbe
 * Praezision wie die Skyfield/DE421-Rechnung der Python-Version dieses
 * Projekts; in sehr seltenen Faellen, in denen eine Sphaere exakt auf
 * einer Liniengrenze liegt, kann das Ergebnis abweichen.
 */

const GRAD = Math.PI / 180;

function normGrad(g) {
  g = g % 360;
  return g < 0 ? g + 360 : g;
}

function sind(x) { return Math.sin(x * GRAD); }
function cosd(x) { return Math.cos(x * GRAD); }
function atan2d(y, x) { return normGrad(Math.atan2(y, x) / GRAD); }

// Tage seit Schlyters Epoche (1999-12-31.0 UT) aus einem Julianischen Datum.
function tageSeitEpoche(jdUt) {
  return jdUt - 2451543.5;
}

function loeseKepler(mGrad, e) {
  let E = mGrad + (e / GRAD) * sind(mGrad) * (1.0 + e * cosd(mGrad));
  for (let i = 0; i < 8; i++) {
    const dM = mGrad - (E - (e / GRAD) * sind(E));
    const dE = dM / (1 - e * cosd(E));
    E += dE;
    if (Math.abs(dE) < 1e-7) break;
  }
  return E;
}

// Bahnelemente -> heliozentrische Ekliptik-Rechtwinkelkoordinaten (AU).
function bahnpunkt(el) {
  const E = loeseKepler(el.M, el.e);
  const xv = el.a * (cosd(E) - el.e);
  const yv = el.a * Math.sqrt(1 - el.e * el.e) * sind(E);
  const v = atan2d(yv, xv);
  const r = Math.sqrt(xv * xv + yv * yv);
  const vw = v + el.w;
  const xh = r * (cosd(el.N) * cosd(vw) - sind(el.N) * sind(vw) * cosd(el.i));
  const yh = r * (sind(el.N) * cosd(vw) + cosd(el.N) * sind(vw) * cosd(el.i));
  const zh = r * (sind(vw) * sind(el.i));
  return { x: xh, y: yh, z: zh, r: r };
}

function sonnenElemente(d) {
  return {
    N: 0.0, i: 0.0,
    w: normGrad(282.9404 + 4.70935e-5 * d),
    a: 1.000000,
    e: 0.016709 - 1.151e-9 * d,
    M: normGrad(356.0470 + 0.9856002585 * d),
  };
}

// Sonnen-Position (geozentrisch = -heliozentrische Erdposition).
function sonnePosition(d) {
  const el = sonnenElemente(d);
  const p = bahnpunkt(el); // liefert direkt die geozentrische Position der Sonne
  return { laenge: atan2d(p.y, p.x), x: p.x, y: p.y, z: p.z };
}

function erdeHeliozentrisch(d) {
  const s = sonnePosition(d);
  return { x: -s.x, y: -s.y, z: -s.z };
}

function mondPosition(d) {
  const N = normGrad(125.1228 - 0.0529538083 * d);
  const i = 5.1454;
  const w = normGrad(318.0634 + 0.1643573223 * d);
  const a = 60.2666;
  const e = 0.054900;
  const M = normGrad(115.3654 + 13.0649929509 * d);

  const E = loeseKepler(M, e);
  const xv = a * (cosd(E) - e);
  const yv = a * Math.sqrt(1 - e * e) * sind(E);
  const v = atan2d(yv, xv);
  const r = Math.sqrt(xv * xv + yv * yv);
  const vw = v + w;
  const xh = r * (cosd(N) * cosd(vw) - sind(N) * sind(vw) * cosd(i));
  const yh = r * (sind(N) * cosd(vw) + cosd(N) * sind(vw) * cosd(i));
  const zh = r * (sind(vw) * sind(i));

  let lonecl = atan2d(yh, xh);
  let latecl = atan2d(zh, Math.sqrt(xh * xh + yh * yh));

  const sunEl = sonnenElemente(d);
  const Ms = sunEl.M;
  const Lm = normGrad(N + w + M);
  const Ls = normGrad(sunEl.w + Ms);
  const Dd = normGrad(Lm - Ls);
  const F = normGrad(Lm - N);

  lonecl = normGrad(lonecl
    - 1.274 * sind(M - 2 * Dd)
    + 0.658 * sind(2 * Dd)
    - 0.186 * sind(Ms)
    - 0.059 * sind(2 * M - 2 * Dd)
    - 0.057 * sind(M - 2 * Dd + Ms)
    + 0.053 * sind(M + 2 * Dd)
    + 0.046 * sind(2 * Dd - Ms)
    + 0.041 * sind(M - Ms)
    - 0.035 * sind(Dd)
    - 0.031 * sind(M + Ms)
    - 0.015 * sind(2 * F - 2 * Dd)
    + 0.011 * sind(M - 4 * Dd));

  return { laenge: lonecl, breite: latecl };
}

const ELEMENTE = {
  merkur: d => ({
    N: normGrad(48.3313 + 3.24587e-5 * d), i: 7.0047 + 5.00e-8 * d,
    w: normGrad(29.1241 + 1.01444e-5 * d), a: 0.387098,
    e: 0.205635 + 5.59e-10 * d, M: normGrad(168.6562 + 4.0923344368 * d),
  }),
  venus: d => ({
    N: normGrad(76.6799 + 2.46590e-5 * d), i: 3.3946 + 2.75e-8 * d,
    w: normGrad(54.8910 + 1.38374e-5 * d), a: 0.723330,
    e: 0.006773 - 1.302e-9 * d, M: normGrad(48.0052 + 1.6021302244 * d),
  }),
  mars: d => ({
    N: normGrad(49.5574 + 2.11081e-5 * d), i: 1.8497 - 1.78e-8 * d,
    w: normGrad(286.5016 + 2.92961e-5 * d), a: 1.523688,
    e: 0.093405 + 2.516e-9 * d, M: normGrad(18.6021 + 0.5240207766 * d),
  }),
  jupiter: d => ({
    N: normGrad(100.4542 + 2.76854e-5 * d), i: 1.3030 - 1.557e-7 * d,
    w: normGrad(273.8777 + 1.64505e-5 * d), a: 5.20256,
    e: 0.048498 + 4.469e-9 * d, M: normGrad(19.8950 + 0.0830853001 * d),
  }),
  saturn: d => ({
    N: normGrad(113.6634 + 2.38980e-5 * d), i: 2.4886 - 1.081e-7 * d,
    w: normGrad(339.3939 + 2.97661e-5 * d), a: 9.55475,
    e: 0.055546 - 9.499e-9 * d, M: normGrad(316.9670 + 0.0334442282 * d),
  }),
  uranus: d => ({
    N: normGrad(74.0005 + 1.3978e-5 * d), i: 0.7733 + 1.9e-8 * d,
    w: normGrad(96.6612 + 3.0565e-5 * d), a: 19.18171 - 1.55e-8 * d,
    e: 0.047318 + 7.45e-9 * d, M: normGrad(142.5905 + 0.011725806 * d),
  }),
};

// Gegenseitige Stoerungen (Schlyter) -- vor allem fuer Jupiter/Saturn
// relevant, die sich sonst um bis zu ~1 Grad verschieben koennten.
function stoerungen(name, d, laenge, breite) {
  const Mj = ELEMENTE.jupiter(d).M;
  const Ms = ELEMENTE.saturn(d).M;
  const Mu = ELEMENTE.uranus(d).M;
  if (name === "jupiter") {
    laenge += -0.332 * sind(2 * Mj - 5 * Ms - 67.6)
      - 0.056 * sind(2 * Mj - 2 * Ms + 21)
      + 0.042 * sind(3 * Mj - 5 * Ms + 21)
      - 0.036 * sind(Mj - 2 * Ms)
      + 0.022 * cosd(Mj - Ms)
      + 0.023 * sind(2 * Mj - 3 * Ms + 52)
      - 0.016 * sind(Mj - 5 * Ms - 69);
  } else if (name === "saturn") {
    laenge += 0.812 * sind(2 * Mj - 5 * Ms - 67.6)
      - 0.229 * cosd(2 * Mj - 4 * Ms - 2)
      + 0.119 * sind(Mj - 2 * Ms - 3)
      + 0.046 * sind(2 * Mj - 6 * Ms - 69)
      + 0.014 * sind(Mj - 3 * Ms + 32);
    breite += -0.020 * cosd(2 * Mj - 4 * Ms - 2)
      + 0.018 * sind(2 * Mj - 6 * Ms - 49);
  } else if (name === "uranus") {
    laenge += 0.040 * sind(Ms - 2 * Mu + 6)
      + 0.035 * sind(Ms - 3 * Mu + 33)
      - 0.015 * sind(Mj - Mu + 20);
  }
  return { laenge: normGrad(laenge), breite };
}

function planetPosition(name, d) {
  const el = ELEMENTE[name](d);
  const helio = bahnpunkt(el);
  const erde = erdeHeliozentrisch(d);
  const xg = helio.x - erde.x, yg = helio.y - erde.y, zg = helio.z - erde.z;
  let laenge = atan2d(yg, xg);
  let breite = atan2d(zg, Math.sqrt(xg * xg + yg * yg));
  ({ laenge, breite } = stoerungen(name, d, laenge, breite));
  return { laenge, breite };
}

// Oeffentliche Schnittstelle: Ekliptiklaenge (Grad) eines Koerpers zu
// einem Julianischen Datum (UT). Passend zu kern.planet_laenge() der
// Python-Version, damit gene_keys.js dieselbe Form erwartet.
function planetLaenge(jdUt, name) {
  const d = tageSeitEpoche(jdUt);
  if (name === "sonne") return sonnePosition(d).laenge;
  if (name === "mond") return mondPosition(d).laenge;
  return planetPosition(name, d).laenge;
}
