import * as Plot from "npm:@observablehq/plot";
import * as topojson from "npm:topojson-client";
import * as d3 from "npm:d3";

const palette = new Map([
  ["Partial Practice Act", "#e2da4e"],
  ["Title Act", "#339d42"],
  ["Roster Designation", "#012a9c"],
  ["Full Practice Act", "#c78b8d"],
  ["No Restrictions", "#8ba8c5"],
]);

export function stateChoropleth(licenseCounts, geo, { width, height } = {}) {
  const states = topojson.feature(geo, geo.objects.states);

  const stateColorMap = new Map(
    licenseCounts.map((entry) => [
      entry.stateFips,
      palette.get(entry.designation),
    ])
  );

  const stateCountMap = new Map(
    licenseCounts.map((entry) => [entry.stateFips, entry.count])
  );

  return Plot.plot({
    width: width ?? 975,
    height: height ?? 610,
    projection: "identity",
    color: {
      type: "categorical",
      domain: Array.from(palette.keys()),
      range: Array.from(palette.values()),
      legend: true,
    },
    marks: [
      Plot.geo(
        states,
        Plot.centroid({
          fill: (d) => stateColorMap.get(d.id),
        })
      ),
      Plot.geo(states, { stroke: "white" }),
      Plot.text(
        states,
        Plot.centroid({
          text: (d) => stateCountMap.get(d.id),
          fill: "white",
          stroke: "#00008b",
          fontWeight: "bold",
          fontSize: "1rem",
          strokeWidth: 2,
        })
      ),
    ],
  });
}
