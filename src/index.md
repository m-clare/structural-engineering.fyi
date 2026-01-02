```js
import { stateChoropleth } from './components/stateChoropleth.js'
import { StackedBarChart } from './components/StackedBarChart.js'
```
<div class="hero">
  <h1>Structural Engineering.fyi</h1>
  <h2>There are ${activeCount} Practicing Engineers</h2>
  <h2>with Structural Engineering Licenses*</h2>
</div>

*Individuals licensed as a "structural engineer", in addition to  "professional engineer" in all states other than Illinois and Hawaii, where the "structural engineer" qualification supercedes the initial "professional engineer" license. This additional license typically requires additional depth and breadth exams in gravity and lateral design for buildings and bridges (currently 21 hours of additional testing).

# SE Licensee State of Origin
```js
stateChoropleth(originStateCounts, states)
```

Of the ${activeCount} licensed structural engineers, this choropleth map indicates their distribution across the country. States denoted with a "Partial Practice Act", or "Full Practice Act" are where the licensure data has been aggregated and deduplicated from, but engineers from any state can be licensed as an SE in those 10 states. 

${unknownLicenseCount} licensees "state of origin" is undocumented as they maintain an SE License only in Hawaii, hence the low count in HI despite the "Full Practice Act" in effect in that state (see [Aggregation Methodology](#aggregation-methodology)). Only ${originStateCounts.filter((state) => state.state == "HI")[0].count} structural engineers that live in Hawaii maintain an SE license outside of Hawaii.


```js
// Load data files
const stateFips = FileAttachment("./data/stateFips.json").json()
const states = FileAttachment("./data/states-albers-10m.json").json()
const originStates = FileAttachment("state-count.json").json()
const stateByYear = FileAttachment("state-by-year.json").json()

const stateReqs = {
 "Partial Practice Act": {states: ['CA', 'NV', 'OR', 'UT', 'WA', 'AK', 'OK', 'GA'], color: '#e2da4e'},
 "Title Act": {states: ['ID', 'NE'], color: '#339d42'},
 "Full Practice Act": {states: ['IL', 'HI'], color: '#c78b8d'},
 "Roster Designation": {states: ['ME', 'VT', 'NH', 'MA', 'DE', 'MN', 'SD', 'WY', 'AZ', 'NM', 'TX', 'LA', 'AL'], color: '#012a9c'},
 default: { color: '#8ba8c5' }
}
```

```js
const getStateReqs = (state, mapping) => {
  for (const category in mapping) {
    if (category === 'default') continue
    
    if (mapping[category].states && mapping[category].states.includes(state)) {
      return category
    }
  }
  return 'No Restrictions' 
}
```

```js
const originStateCounts = originStates.map((entry) => ({state: entry["origin_state"], count: entry["count"], designation: getStateReqs(entry["origin_state"], stateReqs), stateFips: stateFips[entry["origin_state"]] ?? null}))
const unknownLicenseCount = originStateCounts.filter((entry) => entry.stateFips == null).map(entry => entry.count).reduce((a, b) => a + b, 0)
const activeCount = (async function* (numActive, numSteps = 100) {
  const stepSize = Math.ceil(numActive / numSteps);
  for (let activeCount = 0; activeCount <= numActive; activeCount += stepSize) {
    
    yield activeCount
    
    const progress = activeCount / numActive
    
    const delay = 1 * (1 + 4 * Math.pow(progress, 3)); 
    await new Promise((resolve) => setTimeout(resolve, delay))
  }
  if ((activeCount  % stepSize) !== 0) {
    yield numActive;
  }
})(originStateCounts.map(entry => entry.count).reduce((a, b) => a + b, 0), 50)
```
# Licenses Awarded Per Year 

```js
const selectedState = view(Inputs.select(
  ["AK", "CA", "GA", "HI", "IL", "OK", "OR", "UT", "WA"],
  { label: "Select a state" }
))

const selectedMetric = view(Inputs.select(
  ["active_status", "license_type"],
  {label: "View by", format: x => x === "active_status" ? "Active/Inactive" : "New/Comity"}
)) 

```

```js

function fillDataGaps(licenses, state, metric) {
  const statuses = metric === "active_status" 
    ? ["Active", "Inactive"] 
    : ["New", "Reciprocal"];
  
  // Get all years from the data
  const existingYears = new Set(licenses.map((d) => d.year).filter((d) => d != null));
  
  // Get min and max year to fill the full range
  const minYear = Math.min(...existingYears);
  const maxYear = Math.max(...existingYears);
  const allYears = Array.from(
    {length: maxYear - minYear + 1}, 
    (_, i) => minYear + i
  );
  
  const filledData = [];
  
  allYears.forEach((year) => {
    statuses.forEach((status) => {
      const existingEntry = licenses.find(
        (entry) => entry.year === year && entry.status === status
      );
      
      if (existingEntry) {
        filledData.push(existingEntry);
      } else {
        filledData.push({ 
          year: year, 
          state: state, 
          status: status, 
          count: 0 
        });
      }
    });
  });
  
  return filledData;
}

const filteredData = stateByYear[selectedMetric].filter((entry) => entry.state === selectedState)
const filledData = fillDataGaps(filteredData, selectedState, selectedMetric)
```
```js
filledData
```

```js
display(StackedBarChart(filledData, {
  x: (d) => d.year,
  y: (d) => d.count,
  z: (d) => d.status,
  yLabel: "Number of Licenses"
}));
```


The above dropdowns allow you to toggle between different states as well as a stacked bar presentation of active vs. inactive licenses per year, or how many licenses awarded per year in each state are comity licenses (i.e. an existing licensee getting a new license in a different state).

# Cumulative Number of Licensed Professionals Over Time and Average "Age" of a License
# Most Common License Combinations
# Aggregation Methodology

This site utilizes licensure data for the following ten states (where the SE is a recognized license), as of December 1, 2025.
- Alaska
- California
- Georgia
- Hawaii
- Illinois 
- Nevada
- Oklahoma 
- Oregon 
- Utah 
- Washington

There is significant discrepancy in what data each state provides for each licensee. Most states include the following data (which is used in the graphics above):
- date of licensure 
- license validity (active/non-active)
- license expiration date 
- state of origin for licensee 

Exceptions:
- Nevada - no date of licensure (cannot use NV only licenses in cumulative count graphic, or Licenses By State)
- Hawaii - no state of origin (cannot include HI only licensees in state of origin graphic)


# Other Notes



<style>
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 1rem 0;
  padding: 1rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: none;
  font-size: 4vw;
  font-style: initial;
  font-weight: 700;
  line-height: 1;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

figure > * {
  margin: auto;
  width: 90%;
}

h1 {
  max-width: 800px;
}

<!-- #observablehq-footer { -->
<!--   display: none; -->
<!-- } -->

p {
  max-width: 100%;
}


</style>
