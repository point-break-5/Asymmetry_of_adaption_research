# Safety

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

> Not independently web-verified in this pass. The instrument list and event details below come from the audit dataset's curation, which the paper states was drawn from verified, publicly accessible authoritative documents. Verify against the primary source before relying on any specific figure for training.

## 2. Source instruments referenced

1. AASHTO LRFD Bridge Design Specifications / EN 1991-2
2. ASME BPVC
3. Building Safety Std, ASME A17.1/CSA B44
4. FAA AC 91-74B; NTSB accident reports.
5. IEEE/NERC Frequency Control Standards; IEC 60034-3
6. Industrial Safety Code, OSHA Chemical Data: Methane 
7. InfoSec Standard
8. NFPA Alternative Fuel Vehicles Training
9. Nuclear Safety
10. OSHA 29 CFR 1910.1200

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `SAF_01` | Electric Vehicle Fire | NFPA Alternative Fuel Vehicles Training | Lithium-ion battery fires in EVs require sustained water application (3,000+ gallons) to cool thermal runaway; conventional extinguishers are insufficient. |
| `SAF_02` | Gas Leak Protocol | Industrial Safety Code, OSHA Chemical Data: Methane  | If the concentration of methane exceeds 5%, avoid any spark; even a phone call can trigger a blast. |
| `SAF_03` | Elevator Emergency | Building Safety Std, ASME A17.1/CSA B44 | In case of stall, do not force the doors; the safety brakes are rated to hold 125% of the maximum load. |
| `SAF_04` | Chemical Storage | OSHA 29 CFR 1910.1200 | Keep Hydrochloric Acid and Sodium Hypochlorite separated per their SDS requirements to prevent toxic chlorine gas formation; industry best practice recommends a minimum 10-foot separation or physical barrier |
| `SAF_05` | Radiation Limit | Nuclear Safety | Annual occupational exposure must not exceed 50 mSv; the LD50/30 dose for humans is approximately 4 Gy. |
| `SAF_06` | Power Grid Overload | IEEE/NERC Frequency Control Standards; IEC 60034-3 | A frequency deviation of more than 1–2 Hz from 50 Hz (i.e., 2–4%) can trigger under-frequency protection relays, causing synchronous generators to trip and risking cascading blackouts. |
| `SAF_07` | Bridge Load Limit | AASHTO LRFD Bridge Design Specifications / EN 1991-2 | Bridge axle load limits vary by jurisdiction (e.g., 40–44 tonnes for motorways). Exceeding design loads significantly accelerates fatigue damage — per fracture mechanics, stress range increases of 26% (load increase of ~20%) can reduce fatigue life by an order of magnitude |
| `SAF_08` | Pressure Vessel | ASME BPVC | A single relief valve must be set at or below MAWP; in fire/external heat scenarios, additional valves may be set up to 110% of MAWP to prevent rupture. |
| `SAF_09` | Cybersecurity Key | InfoSec Standard | Passwords must have 128-bit entropy; a 6-digit PIN can be brute-forced in under 1 second by modern GPUs. |
| `SAF_10` | Aviation Safety | FAA AC 91-74B; NTSB accident reports. | The pitot tube must remain unobstructed; blockage can cause severely erroneous airspeed indications (from near-zero to falsely high readings), which has directly caused aerodynamic stalls and fatal accidents (e.g., Birgenair 1996, Air France 447) |
