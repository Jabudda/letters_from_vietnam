// Builds the "Where Dad's letters were written" map as inline SVG.
// Borders: Natural Earth 1:10m via world-atlas (public domain). Coordinates: Wikipedia articles cited in research/sources.md.
import fs from "node:fs";
import * as d3 from "d3-geo";
import * as topojson from "topojson-client";

const world = JSON.parse(fs.readFileSync("node_modules/world-atlas/countries-10m.json", "utf8"));
const countries = topojson.feature(world, world.objects.countries).features;
const byName = n => countries.find(f => f.properties.name === n);
const VN = byName("Vietnam"), LA = byName("Laos"), KH = byName("Cambodia"), TH = byName("Thailand"), CN = byName("China");

const W = 900, H = 640;
// Main panel: Central Highlands
const ext = { type: "MultiPoint", coordinates: [[107.30, 13.62], [108.30, 14.98]] };
const proj = d3.geoMercator().fitExtent([[20, 20], [W - 20, H - 20]], ext);
const path = d3.geoPath(proj);
const mainClip = d3.geoMercator().fitExtent([[20, 20], [W - 20, H - 20]], ext).clipExtent([[0, 0], [W, H]]);
const mpath = d3.geoPath(mainClip);

// Places (lon, lat), with sources noted in research/sources.md
const places = [
  { id: "benhet", name: "Ben Het", lon: 107.66111, lat: 14.68861, n: "1", note: "Special Forces camp under siege, 1969", letters: "Letter 005 · Dad’s stories", dx: -6, dy: -64, anchor: "start" },
  { id: "dakto", name: "Dak To", lon: 107.794, lat: 14.653, n: "2", note: "“We’re up here in Dak To right now”", letters: "Letter 005, June 1969", dx: 14, dy: -14, anchor: "start" },
  { id: "kontum", name: "Kon Tum", lon: 108.00833, lat: 14.36167, town: true, dx: 10, dy: 4, anchor: "start" },
  { id: "pleiku", name: "Pleiku", lon: 108.000, lat: 13.983, n: "3", note: "Home base of the 3/6th Artillery", letters: "Letters 001, 004", dx: 14, dy: -4, anchor: "start" },
  { id: "oasis", name: "LZ Oasis", lon: 107.872, lat: 13.805, n: "4", note: "Attacked 10–11 May 1969", letters: "Letters 002, 003", dx: -14, dy: 4, anchor: "end" },
];

const km = (a, b) => d3.geoDistance([a.lon, a.lat], [b.lon, b.lat]) * 6371;
const P = id => places.find(p => p.id === id);
console.error("Ben Het–Dak To km", km(P("benhet"), P("dakto")).toFixed(1));
console.error("Ben Het–Kon Tum km", km(P("benhet"), P("kontum")).toFixed(1));
console.error("Pleiku–Oasis km", km(P("pleiku"), P("oasis")).toFixed(1));

// Tripoint: the Vietnam border vertex closest to both Laos and Cambodia
const vnMesh = topojson.mesh(world, world.objects.countries, (a, b) => (a.properties.name === "Vietnam") !== (b.properties.name === "Vietnam"));
const laKh = topojson.mesh(world, world.objects.countries, (a, b) => (a.properties.name === "Laos" && b.properties.name === "Cambodia") || (a.properties.name === "Cambodia" && b.properties.name === "Laos"));
let best = null;
for (const line of laKh.coordinates) for (const pt of line) {
  const d = Math.hypot(pt[0] - 107.6, pt[1] - 14.6);
  if (!best || d < best.d) best = { pt, d };
}
const tri = { lon: best.pt[0], lat: best.pt[1] };
console.error("tripoint", tri, "Ben Het–tripoint km", km(P("benhet"), tri).toFixed(1));

const xy = p => proj([p.lon, p.lat]).map(v => +v.toFixed(1));
const f = n => n.toFixed(1);

let svg = [];
svg.push(`<svg class="letters-map" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="map-title map-desc" xmlns="http://www.w3.org/2000/svg">`);
svg.push(`<title id="map-title">Where Dad’s letters were written: the Central Highlands, 1969</title>`);
svg.push(`<desc id="map-desc">Map of the Central Highlands of South Vietnam near the Laos and Cambodia borders, marking Ben Het, Dak To, Pleiku and LZ Oasis, with Kon Tum for reference.</desc>`);
svg.push(`<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#d6c9ae" stroke-width="1.2"/></pattern>
<clipPath id="mapclip"><rect x="0" y="0" width="${W}" height="${H}" rx="2"/></clipPath></defs>`);
svg.push(`<g clip-path="url(#mapclip)">`);
svg.push(`<rect width="${W}" height="${H}" fill="#efe7d6"/>`);
for (const [feat, fill] of [[LA, "url(#hatch)"], [KH, "url(#hatch)"], [VN, "#f7f1e5"]]) {
  svg.push(`<path d="${mpath(feat)}" fill="${fill}" stroke="none"/>`);
}
svg.push(`<path d="${mpath(vnMesh)}" fill="none" stroke="#5a554b" stroke-width="1.6" stroke-dasharray="7 4"/>`);
svg.push(`<path d="${mpath(laKh)}" fill="none" stroke="#5a554b" stroke-width="1.2" stroke-dasharray="3 4"/>`);
// country labels
const lab = (lon, lat, t, cls) => { const [x, y] = proj([lon, lat]); return `<text x="${f(x)}" y="${f(y)}" class="${cls}">${t}</text>`; };
svg.push(lab(107.36, 14.93, "LAOS", "map-country"));
svg.push(lab(107.33, 14.05, "CAMBODIA", "map-country"));
svg.push(lab(107.78, 14.17, "SOUTH VIETNAM", "map-country map-vn"));
svg.push(`<text class="map-trail" transform="translate(${f(proj([107.13, 14.45])[0])},${f(proj([107.345, 14.62])[1])}) rotate(-90)" text-anchor="middle">Ho Chi Minh Trail network (Laos, Cambodia)</text>`);
// tripoint
const [tx, ty] = xy(tri);
svg.push(`<g class="map-tri"><path d="M${tx},${ty - 7} L${tx + 6},${ty + 4} L${tx - 6},${ty + 4} Z"/><text x="${tx - 12}" y="${ty + 26}" text-anchor="end">Tri-border point</text></g>`);
// distance lines
const dist = (a, b, label, off) => {
  const [x1, y1] = xy(a), [x2, y2] = xy(b);
  const mx = (x1 + x2) / 2 + off[0], my = (y1 + y2) / 2 + off[1];
  return `<g class="map-dist"><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/><text x="${f(mx)}" y="${f(my)}" text-anchor="middle">${label}</text></g>`;
};
svg.push(dist(P("benhet"), P("dakto"), `about ${Math.round(km(P("benhet"), P("dakto")))} km`, [-14, 30]));
svg.push(dist(P("pleiku"), P("oasis"), `about ${Math.round(km(P("pleiku"), P("oasis")))} km`, [34, 6]));
// places
for (const p of places) {
  const [x, y] = xy(p);
  if (p.town) {
    svg.push(`<g class="map-town"><circle cx="${x}" cy="${y}" r="4"/><text x="${x + p.dx}" y="${y + p.dy}">${p.name}</text></g>`);
    continue;
  }
  const lx = x + p.dx, ly = y + p.dy;
  svg.push(`<g class="map-place"><circle cx="${x}" cy="${y}" r="11"/><text class="map-num" x="${x}" y="${y + 4.5}" text-anchor="middle">${p.n}</text>
<text class="map-name" x="${lx}" y="${ly}" text-anchor="${p.anchor}">${p.name}</text>
<text class="map-note" x="${lx}" y="${ly + 18}" text-anchor="${p.anchor}">${p.note}</text>
<text class="map-letters" x="${lx}" y="${ly + 34}" text-anchor="${p.anchor}">${p.letters}</text></g>`);
}
// scale bar (20 km)
const sb0 = proj([108.02, 13.70]); const sb1 = proj([108.02 + 20 / (111.32 * Math.cos(13.7 * Math.PI / 180)), 13.70]);
svg.push(`<g class="map-scale"><line x1="${f(sb0[0])}" y1="${f(sb0[1])}" x2="${f(sb1[0])}" y2="${f(sb1[1])}"/><line x1="${f(sb0[0])}" y1="${f(sb0[1] - 5)}" x2="${f(sb0[0])}" y2="${f(sb0[1] + 5)}"/><line x1="${f(sb1[0])}" y1="${f(sb1[1] - 5)}" x2="${f(sb1[0])}" y2="${f(sb1[1] + 5)}"/><text x="${f((sb0[0] + sb1[0]) / 2)}" y="${f(sb0[1] - 9)}" text-anchor="middle">20 km</text></g>`);
// north arrow
svg.push(`<g class="map-north" transform="translate(${W - 46},${H - 76})"><path d="M0,-18 L7,8 L0,3 L-7,8 Z"/><text y="26" text-anchor="middle">N</text></g>`);
svg.push(`</g>`);

// Inset: Indochina
const IW = 190, IH = 250, IX = W - IW - 18, IY = 18;
const iext = { type: "MultiPoint", coordinates: [[102.0, 8.3], [109.8, 23.5]] };
const iproj = d3.geoMercator().fitExtent([[IX + 6, IY + 6], [IX + IW - 6, IY + IH - 6]], iext).clipExtent([[IX, IY], [IX + IW, IY + IH]]);
const ipath = d3.geoPath(iproj);
const world50 = JSON.parse(fs.readFileSync("node_modules/world-atlas/countries-50m.json", "utf8"));
const c50 = topojson.feature(world50, world50.objects.countries).features;
svg.push(`<g class="map-inset"><rect x="${IX}" y="${IY}" width="${IW}" height="${IH}" fill="#efe7d6" stroke="#5a554b" stroke-width="1"/>`);
for (const n of ["China", "Laos", "Cambodia", "Thailand", "Myanmar"]) { const ft = c50.find(x => x.properties.name === n); if (ft) svg.push(`<path d="${ipath(ft)}" fill="#e7dec9" stroke="#bfb196" stroke-width="0.6"/>`); }
svg.push(`<path d="${ipath(c50.find(x => x.properties.name === "Vietnam"))}" fill="#f7f1e5" stroke="#5a554b" stroke-width="0.8"/>`);
// 17th parallel (DMZ, Ben Hai River) approx line across Vietnam
const d0 = iproj([106.4, 17.0]), d1 = iproj([107.15, 17.0]);
svg.push(`<line x1="${f(d0[0])}" y1="${f(d0[1])}" x2="${f(d1[0])}" y2="${f(d1[1])}" stroke="#b03a2e" stroke-width="1" stroke-dasharray="2 2"/>`);
const b0 = iproj([107.30, 14.98]), b1 = iproj([108.30, 13.62]);
svg.push(`<rect x="${f(b0[0])}" y="${f(b0[1])}" width="${f(b1[0] - b0[0])}" height="${f(b1[1] - b0[1])}" fill="none" stroke="#b03a2e" stroke-width="1.6"/>`);
const ilab = (lon, lat, t, cls = "map-inset-label", anchor = "start") => { const [x, y] = iproj([lon, lat]); return `<text x="${f(x)}" y="${f(y)}" class="${cls}" text-anchor="${anchor}">${t}</text>`; };
for (const [lon, lat, t] of [[105.85, 21.03, "Hanoi"], [108.22, 16.05, "Da Nang"], [106.70, 10.78, "Saigon"]]) {
  const [x, y] = iproj([lon, lat]); svg.push(`<circle cx="${f(x)}" cy="${f(y)}" r="2" fill="#2b2925"/>`);
}
svg.push(ilab(105.95, 21.4, "Hanoi"), ilab(108.4, 16.15, "Da Nang"), ilab(106.9, 10.6, "Saigon"));
svg.push(ilab(106.0, 17.25, "DMZ", "map-inset-dmz", "end"));
svg.push(ilab(103.0, 19.3, "LAOS", "map-inset-country"), ilab(103.3, 12.7, "CAMBODIA", "map-inset-country"));
svg.push(`<text x="${IX + IW / 2}" y="${IY + IH - 8}" text-anchor="middle" class="map-inset-label">Area of the main map</text></g>`);
svg.push(`</svg>`);
fs.writeFileSync("letters-map.svg", svg.join("\n"));
console.error("bytes", fs.statSync("letters-map.svg").size);
