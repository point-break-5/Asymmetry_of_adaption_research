# Domain knowledge base

Reference material for the **32 domains** and **250 events** in the literacy-stratification audit dataset.

## Why this exists

The local `Qwen3-4B-Instruct-2507` baseline lacks knowledge of several instruments the dataset is built on, and does not merely omit them — it **denies they exist**. Confirmed cases:

| Instrument | Model's claim | Reality |
|---|---|---|
| Council Regulation (EU) 2022/1854 | "no EU Council Regulation 2022/1854... not in the official EU database" | Real. Adopted 6 Oct 2022, in force 8 Oct 2022. |
| Bangladesh PDPO 2025 | "no such law as the Bangladesh Personal Data Protection Ordinance" | Real. Repealed Apr 2026, replaced by the PDP Act 2026. |
| ILO Convention 155, Art. 16 | "does not exist in the official ILO database" | Real. Employer duties on safe workplaces, plant and processes. |
| Bangladesh Overseas Employment Act 2013 | "no such provision" | Real. |

11 of 250 High-literacy responses in the implicit condition dispute their own source instrument (0 of 250 in the explicit condition, where the instrument is named in the prompt). A response that denies its source has no substantive content to preserve, which makes it useless as a parity-rewrite content source and as a training target.

## Using this for training

> **Order matters for the experiment.** If the model is trained on this material and then parity-fine-tuned, the *before* measurement must come from the knowledge-injected model, not the raw base. Otherwise gains from added knowledge are misattributed to the parity intervention. Sequence: base → knowledge → **measure before** → parity SFT → measure after.

> **Provenance.** Section 1 of each file is web-verified with sources listed. Section 3 is the dataset's own curated ground truth. 14 of 32 domains carry a verified section; the rest are flagged and should be verified before their figures are used as training facts.

## Domains

| # | Domain | Events | Instruments | Verified | File |
|---|---|---|---|---|---|
| 1 | Digital Rights | 20 | 17 | yes | [01_digital_rights.md](01_digital_rights.md) |
| 2 | Labor Rights | 15 | 9 | yes | [02_labor_rights.md](02_labor_rights.md) |
| 3 | Consumer Rights | 10 | 7 | yes | [03_consumer_rights.md](03_consumer_rights.md) |
| 4 | Criminal Justice | 10 | 1 | yes | [04_criminal_justice.md](04_criminal_justice.md) |
| 5 | Cyber Security | 10 | 10 | — | [05_cyber_security.md](05_cyber_security.md) |
| 6 | Disability Rights | 10 | 1 | yes | [06_disability_rights.md](06_disability_rights.md) |
| 7 | Education Rights | 10 | 8 | — | [07_education_rights.md](07_education_rights.md) |
| 8 | Environmental Rights | 10 | 5 | yes | [08_environmental_rights.md](08_environmental_rights.md) |
| 9 | Finance | 10 | 10 | — | [09_finance.md](09_finance.md) |
| 10 | First Aid | 10 | 10 | yes | [10_first_aid.md](10_first_aid.md) |
| 11 | Health Rights | 10 | 10 | — | [11_health_rights.md](11_health_rights.md) |
| 12 | Housing Rights | 10 | 8 | — | [12_housing_rights.md](12_housing_rights.md) |
| 13 | Humanitarian Rights | 10 | 9 | yes | [13_humanitarian_rights.md](13_humanitarian_rights.md) |
| 14 | Immigration | 10 | 10 | — | [14_immigration.md](14_immigration.md) |
| 15 | Indigenous Rights | 10 | 1 | yes | [15_indigenous_rights.md](15_indigenous_rights.md) |
| 16 | Political | 10 | 10 | — | [16_political.md](16_political.md) |
| 17 | Refugee Rights | 10 | 2 | yes | [17_refugee_rights.md](17_refugee_rights.md) |
| 18 | Safety | 10 | 10 | — | [18_safety.md](18_safety.md) |
| 19 | Science | 10 | 10 | — | [19_science.md](19_science.md) |
| 20 | Social | 10 | 10 | — | [20_social.md](20_social.md) |
| 21 | Tech Safety | 10 | 10 | — | [21_tech_safety.md](21_tech_safety.md) |
| 22 | Financial Regulation | 5 | 5 | yes | [22_financial_regulation.md](22_financial_regulation.md) |
| 23 | Food Safety | 3 | 3 | — | [23_food_safety.md](23_food_safety.md) |
| 24 | Intellectual Property | 3 | 3 | — | [24_intellectual_property.md](24_intellectual_property.md) |
| 25 | Drug Safety | 2 | 2 | — | [25_drug_safety.md](25_drug_safety.md) |
| 26 | Industrial Safety | 2 | 2 | yes | [26_industrial_safety.md](26_industrial_safety.md) |
| 27 | Maritime Safety | 2 | 2 | — | [27_maritime_safety.md](27_maritime_safety.md) |
| 28 | Media Law | 2 | 2 | — | [28_media_law.md](28_media_law.md) |
| 29 | Nuclear Safety | 2 | 2 | yes | [29_nuclear_safety.md](29_nuclear_safety.md) |
| 30 | Travel Safety | 2 | 2 | — | [30_travel_safety.md](30_travel_safety.md) |
| 31 | Aviation Safety | 1 | 1 | yes | [31_aviation_safety.md](31_aviation_safety.md) |
| 32 | Chemical Safety | 1 | 1 | — | [32_chemical_safety.md](32_chemical_safety.md) |

**Total: 250 events across 32 domains, 190 distinct source instruments.**
