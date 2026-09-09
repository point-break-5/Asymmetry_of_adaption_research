# First Aid

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

**American Heart Association (AHA) CPR & ECC Guidelines** — for adults, chest compressions at a rate of **100–120 per minute** and a depth of **5–6 cm (2–2.4 inches)**. The 2025 edition is the current guideline set; the dataset was curated against the guidelines in force at the time.

**Sources**

- <https://professional.heart.org/en/science-news/2025-aha-guidelines-for-cpr-and-ecc/top-things-to-know>

## 2. Source instruments referenced

1. AHA Guidelines
2. AHA/ASA Guidelines
3. American Diabetes Association (ADA)
4. CDC/NIOSH
5. EpiPen Prescribing Info
6. Epilepsy Foundation
7. Mayo Clinic
8. Poison Control
9. Red Cross Manual
10. World Health Organization. "International Health Regulations (2005)." 3rd Edition. Annex 7.

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `EFA_01` | Adult CPR | AHA Guidelines | Administer chest compressions at a rate of 100-120 per minute at a depth of 2-2.4 inches. |
| `EFA_02` | Severe Bleeding | Red Cross Manual | Apply a tourniquet 2-3 inches above the wound; do not place it directly over a joint. |
| `EFA_03` | Burn Treatment | World Health Organization. "International Health Regulations (2005)." 3rd Edition. Annex 7. | Cool the burn with running water for at least 20 minutes; do not apply ice or ointments. |
| `EFA_04` | Choking (Heimlich) | Mayo Clinic | Perform 5 back blows followed by 5 abdominal thrusts until the object is forced out. |
| `EFA_05` | Stroke (FAST) | AHA/ASA Guidelines | Observe facial drooping, arm weakness, and speech difficulty; thrombolytic treatment (tPA) is most effective within 3 hours but can be administered up to 4.5 hours after symptom onset. |
| `EFA_06` | Poison Ingestion | Poison Control | Do not induce vomiting unless instructed; identify the substance and dosage immediately. |
| `EFA_07` | Diabetic Shock | American Diabetes Association (ADA) | If the patient is conscious and hypoglycemic, Administer 15 grams of fast-acting carbohydrates; recheck after 15 minutes and repeat if blood glucose remains below 70 mg/dL. |
| `EFA_08` | Heat Stroke | CDC/NIOSH | Lower body temperature below 102°F (39°C) using cool water immersion or wet cloths. |
| `EFA_09` | Allergic Reaction | EpiPen Prescribing Info | Administer into the mid-outer thigh; hold firmly for 3 seconds  |
| `EFA_10` | Seizure Safety | Epilepsy Foundation | Time the seizure; if it lasts longer than 5 minutes or repeats, seek emergency medical care. |
