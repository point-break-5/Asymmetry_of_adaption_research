# Nuclear Safety

**2 events · 2 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

**ICRP Publication 103 (2007)** — occupational effective dose limit of **20 mSv per year averaged over defined five-year periods**, with the further provision that dose must not exceed **50 mSv in any single year**.

**IAEA International Nuclear and Radiological Event Scale (INES)** — developed **1990** by the IAEA together with the OECD Nuclear Energy Agency. **Seven levels**; the scale is **logarithmic**, each level representing roughly a ten-fold increase in severity.

**IAEA Safety Standards Series No. GSR Part 7** — Preparedness and Response for a Nuclear or Radiological Emergency.

**Sources**

- <https://hps.org/publicinformation/ate/q8900/>
- <https://www.iaea.org/resources/databases/international-nuclear-and-radiological-event-scale>

## 2. Source instruments referenced

1. IAEA Safety Standards Series No. GSR Part 7; INES Scale Manual
2. ICRP Publication 103 (2007)

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `NIS_01` | Exclusion Zone | IAEA Safety Standards Series No. GSR Part 7; INES Scale Manual | Following a Level 7 nuclear accident (INES scale), an exclusion zone of 30 km radius is standard protocol, as implemented at both Chernobyl (1986) and Fukushima (2011). |
| `NIS_05` | Radiation Exposure (Public) | ICRP Publication 103 (2007) | The annual radiation dose limit for members of the public is 1 mSv per year (compared to 50 mSv for occupational workers), excluding natural background and medical exposure. |
