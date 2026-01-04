import * as d3 from "npm:d3";

export function UpsetPlot(data) {
  const height = 600;
  const margin = { top: 20, right: 20, bottom: 320, left: 40 };
  const dotSize = 10;
  const dotSpacing = 30;
  const barWidth = 25;
  const barSpacing = 10;
  const width =
    data.intersections.length * (barWidth + barSpacing) + margin.left;
  const chartHeight = height - margin.top - margin.bottom;
  const svg = d3.create("svg").attr("width", width).attr("height", height);
  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);
  const barScale = d3
    .scaleLinear()
    .domain([0, d3.max(data.intersections, (d) => d.size)])
    .range([0, chartHeight - 50]);

  const bars = g
    .selectAll(".bar")
    .data(data.intersections)
    .enter()
    .append("g")
    .attr("class", "bar")
    .attr(
      "transform",
      (_, i) => `translate(${i * (barWidth + barSpacing)}, 0)`
    );

  bars
    .append("rect")
    .attr("x", 0)
    .attr("y", (d) => chartHeight - barScale(d.size))
    .attr("width", barWidth)
    .attr("height", (d) => barScale(d.size))
    .attr("fill", "steelblue");

  // Bar labels
  bars
    .append("text")
    .attr("x", barWidth / 2)
    .attr("y", (d) => chartHeight - barScale(d.size) - 5)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .text((d) => d.size);

  // Dot matrix
  data.intersections.forEach((intersection, i) => {
    const dotGroup = g
      .append("g")
      .attr("class", "dot-column")
      .attr("transform", `translate(${i * (barWidth + barSpacing)}, 0)`);

    // Active dots for connecting lines
    const activeDots = data.sets
      .map((set, index) => ({
        set,
        index,
        isActive: intersection.set.includes(set),
      }))
      .filter((dot) => dot.isActive);

    // Add connecting lines between active dots
    activeDots.slice(0, -1).forEach((dot, index) => {
      const nextDot = activeDots[index + 1];
      dotGroup
        .append("line")
        .attr("x1", barWidth / 2)
        .attr("y1", chartHeight + 30 + dot.index * dotSpacing)
        .attr("x2", barWidth / 2)
        .attr("y2", chartHeight + 30 + nextDot.index * dotSpacing)
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1);
    });

    // Add dots
    data.sets.forEach((set, j) => {
      const isActive = intersection.set.includes(set);
      dotGroup
        .append("circle")
        .attr("cx", barWidth / 2)
        .attr("cy", chartHeight + 30 + j * dotSpacing)
        .attr("r", dotSize)
        .attr("fill", isActive ? "steelblue" : "#e2e8f0");
    });
  });

  data.sets.forEach((set, i) => {
    g.append("text")
      .attr("x", -10)
      .attr("y", chartHeight + 30 + i * dotSpacing)
      .attr("text-anchor", "end")
      .attr("alignment-baseline", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", "500")
      .attr("color", "#000")
      .text(set);
  });
  return Object.assign(svg.node(), { value: null });
}

export default UpsetPlot;
