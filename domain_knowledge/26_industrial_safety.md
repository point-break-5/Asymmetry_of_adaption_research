# Industrial Safety

**2 events · 2 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

**OSHA 29 CFR 1910.147 — The Control of Hazardous Energy (Lockout/Tagout).** Covers servicing and maintenance where unexpected energisation, start-up, or release of stored energy could injure employees. Requires a documented energy control programme, employee training, and use of lockout devices — tagout only where lockout is not practicable.

**OSHA 29 CFR 1910.146 — Permit-Required Confined Spaces.** Energy isolation under 1910.147 is frequently a prerequisite before permit-space entry. NIOSH publishes the companion criteria for confined-space work.

**Sources**

- <https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147>
- <https://www.osha.gov/enforcement/directives/std-01-05-019>

## 2. Source instruments referenced

1. OSHA 29 CFR 1910.146; NIOSH Criteria for Confined Spaces
2. OSHA 29 CFR 1910.147

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `NIS_02` | Confined Space Entry | OSHA 29 CFR 1910.146; NIOSH Criteria for Confined Spaces | Atmospheric oxygen between 19.5% and 23.5% before entry into a confined space; below 16% causes impaired judgment, below 6% causes death within minutes. |
| `NIS_03` | Lockout/Tagout | OSHA 29 CFR 1910.147 | All energy sources must be isolated and locked out before maintenance on industrial machinery; failure to follow LOTO procedures accounts for approximately 10% of serious workplace injuries. |
