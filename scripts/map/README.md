# Home-page map

`make_map.mjs` draws the "Where the letters were written" map as SVG. The output is pasted into `site/templates/index.html` (section `#map`).

```sh
cd scripts/map
npm install          # world-atlas (Natural Earth borders, public domain), d3-geo, topojson-client
node make_map.mjs    # writes letters-map.svg and prints the measured distances
```

Place coordinates come from the Wikipedia articles listed in `research/sources.md` (Cited in: map). Fire Support Base Black Hawk is placed from the 1969 grid reference BR034535 in the 1/92nd Artillery operational report, converted with the `mgrs` Python package (approximate). Borders are today's, from Natural Earth 1:10m, simplified.
