import * as d3 from "npm:d3";

export function StackedBarChart(
  data,
  {
    x = (d) => d.year, // x-axis accessor
    y = (d) => d.count, // y-axis value accessor (count or licenses)
    z = (d) => d.status, // stack key accessor (status or state)
    xLabel = "Year",
    yLabel = "Count",
    width = 1200,
    height = 500,
    marginTop = 10,
    marginRight = 10,
    marginBottom = 20,
    marginLeft = 40,
    colors = d3.schemeSpectral,
  } = {}
) {
  // Extract the stack keys (statuses or states)
  const stackKeys = d3.union(data.map(z));

  const series = d3
    .stack()
    .keys(stackKeys)
    .value(([, D], key) => {
      const item = D.get(key);
      return item ? y(item) : 0; // Call y() function on the item
    })(d3.index(data, x, z));
  const keyOrder = series.map((d) => d.key);

  const xScale = d3
    .scaleBand()
    .domain(Array.from(d3.union(data.map(x))).sort((a, b) => a - b))
    .range([marginLeft, width - marginRight])
    .padding(0.1);
  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(series, (d) => d3.max(d, (d) => d[1]))])
    .rangeRound([height - marginBottom, marginTop]);
  const color = d3
    .scaleOrdinal()
    .domain(keyOrder)
    .range(colors.slice(0, series.length))
    .unknown("#ccc");

  const formatValue = (val) => (isNaN(val) ? "N/A" : val.toLocaleString("en"));

  // Create the SVG container.
  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto;");
  // Append a group for each series, and a rect for each element in the series.
  svg
    .append("g")
    .selectAll()
    .data(series)
    .join("g")
    .attr("fill", (d) => color(d.key))
    .selectAll("rect")
    .data((D) => D.map((d) => ((d.key = D.key), d)))
    .join("rect")
    .attr("x", (d) => xScale(d.data[0]))
    .attr("y", (d) => yScale(d[1]))
    .attr("height", (d) => yScale(d[0]) - yScale(d[1]))
    .attr("width", xScale.bandwidth())
    .append("title")
    .text((d) => {
      const item = d.data[1].get(d.key);
      return `${d.data[0]} ${d.key}\n${formatValue(y(item))}`;
    });
  // Append the horizontal axis.

  const xAxis = d3
    .axisBottom(xScale)
    .tickValues(
      d3
        .ticks(...d3.extent(xScale.domain()), width / 40)
        .filter((v) => xScale(v) !== undefined)
    )
    .tickSizeOuter(0);
  svg
    .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(xAxis);

  // Append the vertical axis.
  svg
    .append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(d3.axisLeft(yScale).ticks(null, "s"))
    .call((g) => g.selectAll(".domain").remove());
  // Return the chart with the color scale as a property(for the legend).
  return Object.assign(svg.node(), { scales: { color } });
}
