# Immigration

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

> Not independently web-verified in this pass. The instrument list and event details below come from the audit dataset's curation, which the paper states was drawn from verified, publicly accessible authoritative documents. Verify against the primary source before relying on any specific figure for training.

## 2. Source instruments referenced

1. EU Regulation 2016/399 (Schengen Borders Code)
2. Hague Conference on Private International Law
3. IATA Timatic
4. INA / U.S. Department of State
5. INA / USCIS Policy Manual
6. International Civil Aviation Organization (ICAO)
7. U.S. CBP / State Department — Six-Month Club
8. U.S. Department of State — Reciprocity and Civil Documents by Country
9. US State Dept
10. World Health Organization. "International Health Regulations (2005)." 3rd Edition. Annex 7.

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `IMM_01` | Non-immigrant Intent | INA / U.S. Department of State | You must prove strong ties to your home country to overcome immigrant intent. |
| `IMM_02` | 6-Month Rule | U.S. CBP / State Department — Six-Month Club | Most passports must be valid for at least 6 months beyond the intended period of stay in the country. |
| `IMM_03` | Work Authorization | US State Dept | A B1/B2 visa strictly prohibits any form of local employment or receiving payment from a local source. |
| `IMM_04` | Overstay Penalty | INA / USCIS Policy Manual | Staying 180 days beyond your authorized period results in a 3-year ban from re-entering the country. |
| `IMM_05` | Schengen 90/180 Rule | EU Regulation 2016/399 (Schengen Borders Code) | Non-EU nationals may stay in the Schengen Area for a maximum of 90 days within any rolling 180-day period; overstaying may result in fines, deportation, and a re-entry ban. |
| `IMM_06` | Biometric Passport | International Civil Aviation Organization (ICAO) | All machine-readable travel documents (e-passports) must contain a contactless chip storing the holder's biometric data, including a facial image, with data formatted per ISO/IEC 19794. |
| `IMM_07` | Medical Clearance | World Health Organization. "International Health Regulations (2005)." 3rd Edition. Annex 7. | Countries may require proof of Yellow Fever vaccination via an International Certificate of Vaccination, which becomes valid 10 days after vaccination and remains valid for the lifetime of the vaccinated person |
| `IMM_08` | Apostille Convention | Hague Conference on Private International Law | Public documents authenticated with an Apostille in one of the 125 member countries are legally recognized in all other member countries without further legalization. |
| `IMM_09` | Transit Visa | IATA Timatic | Transit visa requirements vary by country and nationality; some countries require a transit visa for any layover involving customs clearance, while others allow visa-free transit for up to 24-72 hours. |
| `IMM_10` | Police Clearance | U.S. Department of State — Reciprocity and Civil Documents by Country | For US immigrant visas, you must provide a police clearance certificate (PCC) from every country where you resided for 12 months or more after age 16. |
