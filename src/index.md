```js
import { stateChoropleth } from './components/stateChoropleth.js'
import { StackedBarChart } from './components/StackedBarChart.js'
import { UpsetPlot } from './components/UpsetPlot.js'
import { BarAndLineChart } from './components/BarAndLineChart.js'
import { Swatches } from './components/Swatches.js'
```

```js
// Load data files
const stateFips = FileAttachment("./data/stateFips.json").json()
const states = FileAttachment("./data/states-albers-10m.json").json()
const originStates = FileAttachment("state-count.json").json()
const stateByYear = FileAttachment("state-by-year.json").json()
const stateLicenses = FileAttachment("state-license-count.json").json()
const licensesByLicensee = FileAttachment("licenses-by-licensee-count.json").json()
const licenseAge = FileAttachment("license-age.json").json()

const stateReqs = {
 "Partial Practice Act": {states: ['CA', 'NV', 'OR', 'UT', 'WA', 'AK', 'OK', 'GA'], color: '#e2da4e'},
 "Title Act": {states: ['ID', 'NE'], color: '#339d42'},
 "Full Practice Act": {states: ['IL', 'HI'], color: '#c78b8d'},
 "Roster Designation": {states: ['ME', 'VT', 'NH', 'MA', 'DE', 'MN', 'SD', 'WY', 'AZ', 'NM', 'TX', 'LA', 'AL'], color: '#012a9c'},
 default: { color: '#8ba8c5' }
}
```

<div class="hero">
  <h1>Structural Engineering.fyi</h1>
  <h2>There are ${activeCount} Practicing Engineers</h2>
  <h2>with Structural Engineering Licenses*</h2>
</div>

<div class="note">*Individuals licensed as a "structural engineer". The SE license requires <a href="https://ncees.org/exams/pe-exam/cbt-structural">additional depth and breadth exams</a> in gravity and lateral design for buildings and bridges (currently 21 hours of additional computer-based testing that is beyond  what is required for a professional engineering license).</div>

## Motivation
This website provides insight into the status of licensure within the profession of structural engineering. 

The "professional engineer" license has been accepted for decades in many U.S. states as the standard for the design of buildings and bridges. Engineers are currently qualified to practice structural engineering in 30 states after passing the PE Civil Exam, a single 8 hour test. However, several professional organizations and governing bodies are pushing for further adoption of advanced qualification based on the "structural engineering" exam. This is confusingly called the "PE" Structural Exam, and requires 21 hours of testing, in addition to the 8 hour PE exam, and specific experience requirements.

There are ten states where the SE license is required in order to design some ("partial practice") or all ("full practice") buildings and bridges. In the maps below there are additional designations that determine if an individual can use the title "structural engineer", but they do not impact an individual's ability to practice structural engineering with only a PE license. 

To my knowledge, no one has compared license data across all of the ten SE license states to determine how many practicing SEs there are and what the trends over time have been in licensure over the past 60 years. I previously took a look at data in a [few states](https://mclare.blog/posts/is-the-structural-engineering-profession-growing/) where it was easy to get licensure data, but decided to revisit this idea with more refined data processing and analysis.

### Active SE Licenses By State 
```js
stateChoropleth(licenseStateCounts, states)
```

There are ${activeLicenseCount} unique licensed structural engineers, who maintain ${totalLicenseCount} active licenses across 10 states. More information on how I gathered this data is in [Other Notes](#other-notes). 


## Key Findings
Here are some key takeaways from a deep dive into the data.

- __At least 5% of active practicing SE licensed engineers have never taken the SE exam.__ These individuals never took the SE exam due to legislation in [Utah in 2008](https://trackbill.com/bill/utah-senate-bill-200-professional-engineers-licensing-amendments/380377/) and legislation in [Georgia in 2020](https://seaog.org/news.php?id=13) allowing engineers to apply for licensure based on experience rather than test outcomes.  While they may not be able to get comity in other states at this point, they are still qualified SEs according to the licensing board. After noticing anomolous peaks in the data from looking at license statistics by state, I was able to find the supporting legislation changes.

```js
const statusColors = ["#377eb8", "#e41a1c", "#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999"]
```

### UT New/Comity Licenses by Year Awarded
```js
Swatches(d3.scaleOrdinal(["New", "Reciprocal"], statusColors.slice(0, 2)))
```
```js
const filteredUTData = stateByYear["license_type"].filter((entry) => entry.state === "UT")
const filledUTData = fillDataGaps(filteredUTData, "UT", "license_type", ["New", "Reciprocal"])

display(StackedBarChart(filledUTData, {
  x: (d) => d.year,
  y: (d) => d.count,
  z: (d) => d.status,
  yLabel: "Number of UT New/Comity Licenses",
  colors: statusColors.slice(0, 2),
  height: 250
}));
```
### GA New/Comity Licenses by Year Awarded
```js
Swatches(d3.scaleOrdinal(["New", "Reciprocal"], statusColors.slice(0, 2)))
```

```js
const filteredGAData = stateByYear["license_type"].filter((entry) => entry.state === "GA")
const filledGAData = fillDataGaps(filteredGAData, "GA", "license_type", ["New", "Reciprocal"])

display(StackedBarChart(filledGAData, {
  x: (d) => d.year,
  y: (d) => d.count,
  z: (d) => d.status,
  yLabel: "Number of GA New/Comity Licenses",
  colors: statusColors.slice(0, 2),
  height: 250
}));
```

- __28% of active licensed SEs are licensed only in Hawaii.__ I believe under old testing guidelines, Hawaii granted licenses to individuals if they had passed portions of an old SE exam that is no longer used. It's unclear if today someone who qualified this way still needs to make this distinction. Anecdotally, I remember a supervising engineer early in my career complaining that he had to denote he'd only passed the SE-1 in Hawaii on his business cards. The high proportion of licensed individuals in Hawaii is also likely due to their lack of continuing education requirements (Illinois, the only other full practice state, does require continuing education).

- __The current average (and median) "age" of an SE license is 15 years old.__ Assuming that most licensed individuals are passing the exam in their late 20s/early 30s after acquiring the required years of experience, this would make the average license holder around 45 years old. There have been two dips in the average age thanks to the grandfathering clauses mentioned above, but in general, the average age has only been increasing. That the average is changing (and increasing) indicates that there is no steady state of people exiting and entering the profession.

### Number of Active Licensed Professionals Over Time and Average "Age" of a License

```js
function getStats(licenses) {
   // process active Licensees
   const activeLicensees = Object.values(licenses).filter((license) => license.active === true && license.license_date !== undefined).map((license) => {
     const date = new Date(Date.parse(license.license_date))
     return {'licenseYear': date.getFullYear()}
   })
   
   // process expired licensees 
   const expiredLicensees = Object.values(licenses).filter((license) => license.active === undefined && license.expiration_date !== undefined && license.license_date !== undefined).map((license) => ({'licenseYear': (new Date(Date.parse(license.license_date))).getFullYear(), 'expYear': (new Date(Date.parse(license.expiration_date)).getFullYear())}))
   
   const licenseYears = (activeLicensees.map((license) => license.licenseYear)).concat( expiredLicensees.map((license) => license.licenseYear))
   const minYear = d3.min(licenseYears)
   const maxYear = d3.max(licenseYears)
   let statsSummary = []
   let yearSummary = {}
   for (let i = minYear; i <= maxYear; i++) {
     const active = activeLicensees.filter((license) => license.licenseYear <= i)
     const expired = expiredLicensees.filter((license) => license.licenseYear <= i && license.expYear >= i)
     const count = active.length + expired.length 
     const validYears = (active.map(license => license.licenseYear)).concat(expired.map(license => license.licenseYear))
     const mean = d3.mean(validYears.map((year) => i - year))
     const median = d3.median(validYears.map((year) => i - year))
     statsSummary.push({year: i, count, mean, median})
     yearSummary[i] = validYears 

    }
    return {overallSummary: statsSummary, yearSummary, yearSet: [minYear, maxYear]}
}

const stats = getStats(licenseAge)
```

<div>
  ${resize((width) => BarAndLineChart(stats.overallSummary, 'SE', {
  x: (d) => d.year,
  y: (d) => d.mean,
  z: (d) => d.status,
  yLabel: `↑ Average "Age" of SE License`,
  title: (d) => `${d.year} - ${Math.round(d.mean)} years`,
  xType: d3.scaleBand,
  width: width,
  height: 600,
  color: "currentColor"
}))}
</div>

- The data quality around licensure expiration is not great (and probably shouldn't be trusted for licenses prior to 1990), but I was curious if there are any visible trends in how many years a license holder maintains at least one license before letting it lapse. If you select the year 2000 in the plot below, that will show that at this point in time there were approximately 1,606 total (summing all the bars below) SE license holders who had allowed all their SE licenses to lapse. Each bar represents the number of years a license holder maintained at least one SE license. For example, at this point in time (the year 2000), 25 SE holders allowed their license to lapse after 4 years. A possible interpretation of this is that those 25 individuals exited the profession.

  Prior to 2000, the distribution of years of experience in the profession as a licensed SE followed a normal distribution. In more recent years, the distribution has skewed right, with __more people failing to renew any SE license after less than 15 years of maintaining it.__ A possible explanation is that more people are leaving the profession well before retirement age.

### Years of Experience Before Non-renewal of Any SE License

<div class="note">
This is based on unique license data tracking when individuals no longer renew any of their previously maintained SE licenses</div>


```js 

function getExpiredStats(licenses) {
  const expiredLicensees = Object.values(licenses).filter((license) => license.active === undefined && license.expiration_date !== undefined && license.license_date !== undefined).map((license) => ({...license, 'licenseYear': (new Date(Date.parse(license.license_date))).getFullYear(), 'expYear': (new Date(Date.parse(license.expiration_date)).getFullYear())})).filter((license) => license.expYear > license.licenseYear)
  
  const licenseYears = expiredLicensees.map((license) => license.licenseYear)
  const minYear = d3.min(licenseYears)
  const maxYear = d3.max(licenseYears)
  let yearSummary = {}
  for (let i = minYear; i <= maxYear; i++) {
    
    const expired = expiredLicensees.filter((license) => license.licenseYear <= i && license.expYear <= i)
    const count = expired.length 
    const licenseAgeAtExp = Object.entries(Object.fromEntries(d3.rollup(expired.map((licensee) => licensee.expYear - licensee.licenseYear), v => v.length, d => d))).map((entry) => ({yearsOfExp: parseInt(entry[0]), count: entry[1]}))
    if (licenseAgeAtExp.length > 0) {
      yearSummary[i.toString()] = licenseAgeAtExp
    }
  }
  
  return yearSummary
}
const expStats = getExpiredStats(licenseAge)
```
```js
const expYearRange = [d3.min(Object.keys(expStats)), d3.max(Object.keys(expStats))]
const selectedExpYear = view(Inputs.range(expYearRange, {step: 1, label: "Year of Interest", value: 2024})
)
```
```js
const selectedSummary = expStats[selectedExpYear]
```

```js
Plot.plot({
  x: {padding: 0.1, tickFormat: (d, i) => {
    if (selectedSummary.length > 40) {
      return i % 5 === 0 ? d.toString() : ""
    } else {
      return d.toString()
    }
  }},
  y: { tickFormat: (d, i) => parseInt(d) },
  width,
  marks: [
    Plot.barY(selectedSummary, {x: "yearsOfExp", y: "count", fill: "#e41a1c"})
  ]
})
```

## Supporting Interactive Plots

### State of Residence for SE Licensees based on Partial/Full Practice

Choose a state from the dropdown to show where licensed engineers for that state (e.g. a SE licensed in CA) live.
```js
const selectedLicenseState = view(Inputs.select(
  ["AK", "CA", "GA", "IL", "OK", "OR", "UT", "WA", "NV"],
  { label: "Select a state" }
))
```
 
```js
stateChoropleth(licenseStateOriginCounts, states)
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

const licenseStateCounts = Object.keys(stateFips).map((state) => ({state: state, count: stateLicenses.find((d) => d.license_state === state) ? stateLicenses.find((d) => d.license_state === state).count : null, designation: getStateReqs(state, stateReqs), stateFips: stateFips[state]}))
const activeLicenseCount = Object.keys(licensesByLicensee).length
const licenseStateOriginCounts = originStates.filter((entry) => entry.license_state === selectedLicenseState && entry.origin_state !== null).map((state) => ({...state, designation: getStateReqs(state.origin_state, stateReqs), stateFips: stateFips[state.origin_state]}))
const totalLicenseCount = licenseStateCounts.map((entry) => entry.count).reduce((a, b) => a + b, 0)

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
})(activeLicenseCount, 50)
```
### Licenses Awarded Per Year 
```js
const selectedState = view(Inputs.select(
  ["AK", "CA", "GA", "HI", "IL", "OK", "OR", "UT", "WA"],
  { label: "Select a state", value: "IL" }
))

const selectedMetric = view(Inputs.select(
  ["active_status", "license_type"],
  {label: "View by", format: x => x === "active_status" ? "Active/Inactive" : "New/Comity"}
)) 

```

```js
Swatches(d3.scaleOrdinal(selectedStatuses, statusColors.slice(0, 2)))
```

```js

const selectedStatuses = selectedMetric === "active_status" 
    ? ["Active", "Inactive"] 
    : ["New", "Reciprocal"];
    
function fillDataGaps(licenses, state, metric, statuses) { 
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
const filledData = fillDataGaps(filteredData, selectedState, selectedMetric, selectedStatuses)

display(StackedBarChart(filledData, {
  x: (d) => d.year,
  y: (d) => d.count,
  z: (d) => d.status,
  yLabel: "Number of Licenses",
  colors: statusColors.slice(0, selectedStatuses.length)
}));
```
<div class="note">
The above dropdowns allow you to toggle between different states as well as a stacked bar presentation of active vs. inactive licenses per year, or how many licenses awarded per year in each state are comity/reciprocal licenses (i.e. an existing licensee getting a new license in a different state). This data is based on each state's records and has not been deduplicated against individuals (other than to determine if a license is a new or reciprocal).
</div>

### Distribution of Oldest License Per Active Licensed Individual Over the Years
```js
const yearOfInterest = view(Inputs.form([
  Inputs.range(stats.yearSet, {step: 1, label: "Year of Interest", value: 2025})
]))
```

```js
function licensesByYear() {
  const range = d3.range(stats.yearSet[0], stats.yearSet[1])
  const valueMap = d3.rollup(stats.yearSummary[yearOfInterest], v => v.length, d => d)
  const output = []
  range.forEach((value) => {
    output.push({year: value, count: valueMap.get(value) ?? 0})
  })
  return output
}
const yearCount = (licensesByYear()).filter((entry) => entry.year <= yearOfInterest)
```
<div class="note">This plot includes active licenses based on the year of interest. For example, if we select the year 2000 below, there were approximately 300 licensed individuals who received their first license in 1990 and were still maintaining at least one SE license in the year 2000.</div>

```js
Plot.plot({
  x: {padding: 0.1, tickFormat: (d, i) => {
    if (yearCount.length > 20) {
      return i % 10 === 0 ? d.toString() : ""
    } else {
      return d.toString()
    }
  }},
  y: { tickFormat: (d, i) => parseInt(d) },
  width,
  marks: [
    Plot.barY(yearCount, {x: "year", y: "count", fill: "steelblue"})
  ]
})
```

### Most Common License Combinations
This [upset plot](https://en.wikipedia.org/wiki/UpSet_plot) is as an advanced Venn diagram for showing intersections of multiple sets. In this case it shows which combinations of licenses are the most common for licensees that actively hold SE licenses in multiple states.

```js
function processSourceStates(data) {
  // Create a map to track state occurrences and related data
  const stateSetCombinations = {}
  const stateAbbrevSet = new Set()
  const dataSet = Object.values(data)
  
  // Process each record
  dataSet.forEach(record => {
  // data.forEach(record => {
    // Split source states and trim whitespace
    const stateSetKey = record.sort().join("-")
    if (!stateSetCombinations[stateSetKey]) {
       const states = Array.from(new Set(stateSetKey.split("-")))
       states.forEach((state) => stateAbbrevSet.add(state))
       stateSetCombinations[stateSetKey] = {size: 0, set: states}
    }
    
    stateSetCombinations[stateSetKey].size += 1
  })
  
  const values = Object.values(stateSetCombinations)
  return {
   sets: Array.from(stateAbbrevSet).sort(),
   intersections: values.sort((a, b) => b.size - a.size)
  } 
  }
```

```js
const individualLicenseData = processSourceStates(licensesByLicensee)
```

```js
html`<div style="overflow-x: auto; max-width: 100%;">${UpsetPlot(individualLicenseData)}</div>`
```

## Aggregation Methodology
Significant effort has been made to properly deduplicate license data to identify individuals holding licenses in multiple states. This [script](https://github.com/m-clare/structural-engineering.fyi/tree/main/src/assets) was created to normalize the data and match individuals with a degree of certainty (low/medium/high/singleton) based on their full names and origin states. All data presented here has been anonymized to avoid exposing personal information.

## Other Notes
This site utilizes data from the licensure board for the following ten states (where the SE is a recognized license), as of December 1, 2025.
- [Alaska](https://www.commerce.alaska.gov/cbp/main/)
- [California](https://www.bpelsg.ca.gov/)
- [Georgia](https://pels.georgia.gov/)
- [Hawaii](https://cca.hawaii.gov/pvl/)
- [Illinois](https://idfpr.illinois.gov/)
- [Nevada](https://nvbpels.org/)
- [Oklahoma](https://oklahoma.gov/pes.html)
- [Oregon](https://www.oregon.gov/OSBEELS/Pages/default.aspx)
- [Utah](https://dopl.utah.gov/engineering/)
- [Washington](https://brpels.wa.gov/)

There are discrepancies in the data fields each state provides for a license. *Most* states include the following fields (used to analyze the data and generate the plots above):
- date of licensure 
- license validity (active/non-active)
- license expiration date 
- state of origin for licensee 

#### Exceptions:
- Nevada - no dates of licensure (cannot use NV only licenses in cumulative count graphic, or Licenses By State)
- Hawaii - no state of origin (cannot include HI only licensees in state of origin graphic)

Passing the 21 hour exam (broken into 4 parts) does not automatically qualify an indvidual to be licensed in one of the ten Partial/Full Practice states. Some states require practicing as a PE for X number of years under a licensed SE before sitting the exam. Others require proof of significant structural experience (down to the seismic design category of a project) to qualify.

#### Known Data Quality Issues
- Illinois has a default license date of 1997-01-01 for licenses where it lacks effective/expiration dates (all show up as "inactive")
- Just about every state has a few licenses that are marked as "active" but may lack licensure dates/expiration dates, probably from bad record keeping

## Disclaimer

Spite Driven Development assumes no responsibility or liability for any errors or omissions in the content of this site. All information is provided on an "as is" basis with no guarantee of completeness, accuracy, usefulness, or of the results obtained from the use of this information. All inquires can be directed to mclare(at)utsv.net.

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

<!-- #observablehq-footer { -->
<!--   display: none; -->
<!-- } -->

p, ul, li, h1, h2, h3, h4, h5, .note {
  max-width: 100%;
}

h3 {
	color: var(--theme-foreground);
	font-size: 20px;
	font-style: italic;
	font-weight: normal;
	margin-bottom: 1rem;
}


</style>
