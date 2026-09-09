# Tech Safety

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

> Not independently web-verified in this pass. The instrument list and event details below come from the audit dataset's curation, which the paper states was drawn from verified, publicly accessible authoritative documents. Verify against the primary source before relying on any specific figure for training.

## 2. Source instruments referenced

1. Automotive Safety
2. Battery Care Guide
3. CDC/NIOSH
4. Cyber Security 
5. Electrical Safety 
6. FDA — Microwave Oven Radiation Safety
7. IEC Standard 60529
8. NEC (National Electrical Code) NFPA 70
9. OSHA Safety
10. U.S. Department of Energy

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `TEC_01` | Power Load | Electrical Safety  | Do not exceed the watt rating printed on the extension cord; typical household cords are rated 1625W (13A at 125V). Overloading can cause overheating and fire. |
| `TEC_02` | Battery Storage | Battery Care Guide | Lithium-ion batteries must be stored at 40-60% charge if unused for more than 30 days. |
| `TEC_03` | IP Rating | IEC Standard 60529 | An IP67 rating means the device is protected against immersion in 1 meter of water for 30 minutes. |
| `TEC_04` | Router Security | Cyber Security  | Change default WPA2 passwords to at least 12 characters including symbols to prevent brute-force. |
| `TEC_05` | Laser Safety | OSHA Safety | Class 3B lasers (5-500mW) can cause eye injury faster than the 0.25-second human blink reflex, making protective eyewear mandatory. |
| `TEC_06` | Chemical Mix | CDC/NIOSH | Never mix bleach with ammonia-based cleaners; the reaction produces toxic chloramine gas. |
| `TEC_07` | Grounding | NEC (National Electrical Code) NFPA 70 | Ensure all 3-prong plugs are connected to properly grounded outlets; ungrounded equipment poses risk of electric shock at household voltages (120V in the US, 230V in most other countries). |
| `TEC_08` | HVAC Filter | U.S. Department of Energy | Replace HVAC air filters every 1-3 months (standard filters) or 6-12 months (HEPA); clogged filters reduce airflow efficiency and increase energy consumption by up to 15%. |
| `TEC_09` | Microwave Safety | FDA — Microwave Oven Radiation Safety | Never heat sealed or airtight containers in a microwave; trapped steam builds pressure rapidly and can cause the container to burst, resulting in severe burns. |
| `TEC_10` | Tool Torque | Automotive Safety | Lug nuts must be tightened to 80-100 lb-ft of torque; under-tightening can lead to wheel detachment. |
