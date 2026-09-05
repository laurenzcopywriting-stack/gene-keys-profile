/*
 * app.js -- Mandala-Rendering + Formular-Verdrahtung.
 *
 * Portierung von genekeys/genekeys_web.py nach JavaScript: gleiches
 * Layout, gleiche Farben, gleiche Sequenz-Tabs -- hier als eine
 * einzige Seite ohne Server-Rundreise gebaut (Formular und Ergebnis
 * auf derselben HTML-Seite, Ergebnis erscheint per JS-Rendering).
 */

const FARBE = {
  aktiv: ["#8bb07a", "#5f8a4e", "#4a6b3c"],
  venus: ["#cf6a60", "#a5372e", "#7f2a23"],
  perle: ["#6a9bd8", "#3d6fb0", "#2c5286"],
  stern: ["#8b7dd8", "#5f4fb0", "#463b86"],
};

const HEIMAT = {
  "Life's Work": "aktiv", "Evolution": "aktiv", "Radiance": "aktiv", "Purpose": "aktiv",
  "Attraction": "venus", "IQ": "venus", "EQ": "venus", "SQ": "venus", "Core": "venus",
  "Vocation": "perle", "Culture": "perle", "Brand": "perle", "Pearl": "perle",
  "Creativity": "stern", "Relating": "stern", "Stability": "stern",
};

const ROLLE = {
  "Life's Work": "Lebensaufgabe", "Evolution": "Wachstum", "Radiance": "Ausstrahlung",
  "Purpose": "Bestimmung", "Attraction": "Anziehung", "IQ": "Verstand", "EQ": "Gefuehl",
  "SQ": "Intuition", "Core": "Kernthema", "Vocation": "Berufung", "Culture": "Umfeld",
  "Brand": "Marke", "Pearl": "Perle", "Creativity": "Kreativitaet", "Relating": "Beziehung",
  "Stability": "Stabilitaet",
};

const L_FULL = {
  "Life's Work": [500, 110], "Pearl": [500, 232], "Core": [402, 322], "Culture": [598, 322],
  "Radiance": [232, 432], "SQ": [500, 432], "Evolution": [768, 432],
  "IQ": [402, 542], "EQ": [598, 542], "Attraction": [500, 640], "Purpose": [500, 762],
};
const K_FULL = [
  ["Life's Work", "Pearl", "perle"], ["Pearl", "Core", "perle"], ["Pearl", "Culture", "perle"],
  ["Core", "Culture", "perle"], ["Life's Work", "Radiance", "aktiv"], ["Radiance", "Purpose", "aktiv"],
  ["Purpose", "Evolution", "aktiv"], ["Evolution", "Life's Work", "aktiv"],
  ["Core", "SQ", "venus"], ["SQ", "IQ", "venus"], ["SQ", "EQ", "venus"], ["IQ", "EQ", "venus"],
  ["EQ", "Attraction", "venus"], ["Attraction", "Purpose", "venus"],
];

const L_AKTIV = {
  "Life's Work": [500, 150], "Radiance": [280, 440], "Evolution": [720, 440], "Purpose": [500, 730],
};
const K_AKTIV = [
  ["Life's Work", "Radiance", "aktiv"], ["Radiance", "Purpose", "aktiv"],
  ["Purpose", "Evolution", "aktiv"], ["Evolution", "Life's Work", "aktiv"],
  ["Radiance", "Evolution", "aktiv"],
];

const L_VENUS = {
  "Core": [500, 140], "SQ": [500, 300], "IQ": [360, 450], "EQ": [640, 450],
  "Attraction": [500, 600], "Purpose": [500, 760],
};
const K_VENUS = [
  ["Core", "SQ", "venus"], ["SQ", "IQ", "venus"], ["SQ", "EQ", "venus"], ["IQ", "EQ", "venus"],
  ["EQ", "Attraction", "venus"], ["Attraction", "Purpose", "venus"],
];

const L_PERLE = {
  "Brand": [500, 170], "Pearl": [500, 420], "Vocation": [330, 650], "Culture": [670, 650],
};
const K_PERLE = [
  ["Brand", "Pearl", "perle"], ["Brand", "Vocation", "perle"], ["Brand", "Culture", "perle"],
  ["Pearl", "Vocation", "perle"], ["Pearl", "Culture", "perle"], ["Vocation", "Culture", "perle"],
];

const L_STERN = {
  "Brand": [500, 130], "Relating": [760, 300], "Culture": [760, 560], "Stability": [500, 730],
  "Vocation": [240, 560], "Creativity": [240, 300], "Pearl": [500, 430],
};
const K_STERN = [
  ["Brand", "Relating", "stern"], ["Relating", "Culture", "stern"], ["Culture", "Stability", "stern"],
  ["Stability", "Vocation", "stern"], ["Vocation", "Creativity", "stern"], ["Creativity", "Brand", "stern"],
  ["Pearl", "Brand", "stern"], ["Pearl", "Relating", "stern"], ["Pearl", "Culture", "stern"],
  ["Pearl", "Stability", "stern"], ["Pearl", "Vocation", "stern"], ["Pearl", "Creativity", "stern"],
];

const TABS = [
  ["full", "Vollprofil", L_FULL, K_FULL, null],
  ["aktiv", "Aktivierung", L_AKTIV, K_AKTIV, "aktiv"],
  ["venus", "Venus", L_VENUS, K_VENUS, "venus"],
  ["perle", "Perle", L_PERLE, K_PERLE, "perle"],
  ["stern", "Sternperle", L_STERN, K_STERN, "stern"],
];

function esc(s) {
  const d = document.createElement("div");
  d.textContent = String(s);
  return d.innerHTML;
}

function knoten(s, x, y, farbeKey, rolleZeigen) {
  const [, dunkel, akzent] = FARBE[farbeKey];
  const name = s.sphaere;
  const rolle = ROLLE[name] || "";
  const rollenzeile = rolleZeigen
    ? `<text x="${x}" y="${y + 87}" text-anchor="middle" class="sr">${esc(rolle)}</text>`
    : "";
  return `<g class="knoten">` +
    `<circle cx="${x}" cy="${y}" r="46" fill="url(#g${farbeKey})" stroke="${dunkel}" stroke-width="2"/>` +
    `<text x="${x}" y="${y + 2}" text-anchor="middle" class="tl">${s.tor}<tspan class="ln" dy="-6">.${s.linie}</tspan></text>` +
    `<text x="${x}" y="${y + 70}" text-anchor="middle" class="sn" fill="${akzent}">${esc(name)}</text>` +
    rollenzeile + `</g>`;
}

function panel(tabKey, layout, kanten, farbeFix, byName, aktiv, rolleZeigen) {
  const linien = kanten.map(([a, b, seqfarbe]) => {
    if (!layout[a] || !layout[b]) return "";
    const fk = farbeFix || seqfarbe;
    const [x1, y1] = layout[a], [x2, y2] = layout[b];
    const [, dunkel] = FARBE[fk];
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${dunkel}" stroke-width="3" opacity="0.5"/>`;
  }).join("");
  const kn = Object.entries(layout).map(([name, [x, y]]) => {
    const s = byName[name];
    if (!s) return "";
    const fk = farbeFix || HEIMAT[name] || "aktiv";
    return knoten(s, x, y, fk, rolleZeigen);
  }).join("");
  const stil = aktiv ? "" : "display:none";
  return `<svg class="mandala" data-tab="${tabKey}" style="${stil}" viewBox="0 0 1000 880" xmlns="http://www.w3.org/2000/svg">` +
    `<rect x="0" y="0" width="1000" height="880" fill="url(#flower)"/>${linien}${kn}</svg>`;
}

function deutung(pr) {
  const seqs = ["aktivierungssequenz", "venussequenz", "perlensequenz", "sternperle"];
  let html = `<section class="deutung"><h2 class="dtitel">Deine Deutung</h2>`;
  for (const seqKey of seqs) {
    const [titel, unter] = INTROS[seqKey];
    html += `<h3 class="seqh">${esc(titel)}</h3><p class="seqintro">${esc(unter)}</p>`;
    for (const s of pr[seqKey]) {
      const [poet, rolle] = SPHAEREN[s.sphaere] || ["", ""];
      const absatz = TORE[String(s.tor)] || "";
      html += `<article class="dk"><div class="dh">` +
        `<span class="dtl">${s.tor}<span class="dpt">.</span>${s.linie}</span>` +
        `<div><div class="dname">${esc(s.sphaere)}</div>` +
        `<div class="dsub">${esc(poet)} &middot; ${esc(rolle)}</div></div></div>` +
        (absatz ? `<p class="dp">${esc(absatz)}</p>` : "") +
        `<p class="dhex">Tor ${s.tor} &middot; I Ging: ${esc(s.hexagramm)}</p></article>`;
    }
  }
  return html + `</section>`;
}

function mandalaHtml(pr, kopf) {
  const byName = {};
  for (const seq of ["aktivierungssequenz", "venussequenz", "perlensequenz", "sternperle"]) {
    for (const s of pr[seq]) byName[s.sphaere] = s;
  }

  let tabbtns = "", panels = "";
  TABS.forEach(([key, titel, layout, kanten, farbeFix], i) => {
    const erste = i === 0;
    tabbtns += `<button class="tab${erste ? " aktiv" : ""}" data-ziel="${key}">${esc(titel)}</button>`;
    panels += panel(key, layout, kanten, farbeFix, byName, erste, key !== "full");
  });

  const pg = pr.primeGifts;
  const grads = Object.entries(FARBE).map(([k, v]) =>
    `<radialGradient id="g${k}" cx="38%" cy="34%" r="70%">` +
    `<stop offset="0%" stop-color="${v[0]}"/><stop offset="100%" stop-color="${v[1]}"/></radialGradient>`
  ).join("");

  return `
    <p class="sub">${kopf.zeile}</p>
    <p class="gifts">Profil <b>${esc(pr.profilLinien)}</b> &nbsp;&middot;&nbsp;
      Life's Work <b>${pg.lifesWork}</b> &middot; Evolution <b>${pg.evolution}</b> &middot;
      Radiance <b>${pg.radiance}</b> &middot; Purpose <b>${pg.purpose}</b></p>
    <div class="tabs">${tabbtns}</div>
    <div class="buehne">
      <svg width="0" height="0"><defs>${grads}
        <pattern id="flower" width="120" height="104" patternUnits="userSpaceOnUse">
          <g fill="none" stroke="#e7e0cd" stroke-width="1">
            <circle cx="60" cy="52" r="34"/><circle cx="0" cy="52" r="34"/>
            <circle cx="120" cy="52" r="34"/><circle cx="30" cy="0" r="34"/>
            <circle cx="90" cy="0" r="34"/><circle cx="30" cy="104" r="34"/>
            <circle cx="90" cy="104" r="34"/></g></pattern></defs></svg>
      ${panels}
    </div>
    <p class="sub" style="margin-top:1rem">Design-Moment ${kopf.designDatum} &middot; Sonne 88&deg; vor der Geburt</p>
    ${deutung(pr)}`;
}

function bindeTabs(wurzel) {
  wurzel.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      const ziel = btn.dataset.ziel;
      wurzel.querySelectorAll(".mandala").forEach(m => {
        m.style.display = m.dataset.tab === ziel ? "block" : "none";
      });
      wurzel.querySelectorAll(".tab").forEach(t => t.classList.toggle("aktiv", t === btn));
    });
  });
}
