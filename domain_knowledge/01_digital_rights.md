# Digital Rights

**20 events · 17 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

**EU General Data Protection Regulation (GDPR), Regulation (EU) 2016/679**
- **Art. 17** — right to erasure ("right to be forgotten"): the controller must erase personal data *without undue delay* on request, subject to the listed grounds and exemptions.
- **Art. 20** — right to data portability: receive personal data in a structured, commonly used, machine-readable format.
- **Art. 22** — the data subject has the right *not* to be subject to a decision based solely on automated processing, including profiling, which produces legal effects or similarly significantly affects them. Derogations in Art. 22(2): contractual necessity, Union/Member State law, explicit consent. Art. 22(3) requires safeguards including meaningful human intervention.
- **Art. 33** — personal data breach must be notified to the supervisory authority without undue delay and, where feasible, **not later than 72 hours** after becoming aware of it, unless unlikely to result in risk to rights and freedoms.
- **Art. 83** — administrative fines.

**Bangladesh Personal Data Protection Ordinance (PDPO) 2025** — a real instrument, contrary to what the base model asserts. Grants access, correction, withdrawal of consent, portability and erasure; requires substantive response to data subject requests within **30 days**; sets out destruction, erasure and disposal procedures.
> **Currency note:** the Bangladesh Parliament repealed the PDPO 2025 in **April 2026** and passed the permanent **Personal Data Protection Act, 2026**. Dataset events referencing the 2025 Ordinance describe the law as it stood at curation time.

**Sources**

- <https://gdpr-text.com/read/article-17/>
- <https://gdpr.algolia.com/gdpr-article-33>
- <https://securiti.ai/bangladesh-personal-data-protection-act-overview/>
- <https://ppc.land/bangladesh-finalizes-comprehensive-data-protection-ordinance-draft/>

## 2. Source instruments referenced

1. Amazon App Privacy Policy/Google Play Store Location Data Disclosure
2. Amazon Privacy Notice
3. Bangladesh Bank Mobile Financial Services Regulations (2018)
4. Bangladesh Data Protection Ordinance 2025
5. Bangladesh PDPO 2025
6. Bangladesh Personal Data Protection Ordinance 2025
7. Facebook (Meta) ToS
8. GDPR
9. GDPR Article
10. GDPR Recital 
11. Instagram (Meta) Privacy Policy
12. OpenAI Terms of Use
13. PayPal Acceptable Use Policy
14. Telegram Privacy Policy
15. TikTok Privacy Policy (US)
16. WhatsApp Business Data Processing Terms
17. WhatsApp Business Privacy Protections Page / WhatsApp Business Data Processing Term

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `DIG_01` | Right to Erasure | Bangladesh PDPO 2025 | Withdraw consent to data processing and ask for deletion. |
| `DIG_02` | Children's Data Protection | Bangladesh Data Protection Ordinance 2025 | Requires parental consent and prohibits tracking for ads. |
| `DIG_03` | Unauthorized Data Collection | Bangladesh Personal Data Protection Ordinance 2025 | Criminal penalties for disclosing data without authority. |
| `DIG_04` | Data License | Facebook (Meta) ToS | Users grant worldwide license to use their content. |
| `DIG_05` | Biometric Tracking | TikTok Privacy Policy (US) | Collection of faceprints and voiceprints from content. |
| `DIG_06` | Cross-App Tracking | Instagram (Meta) Privacy Policy | Tracking behavior across other apps and websites via pixels. |
| `DIG_07` | E2E Encryption Limitations | WhatsApp Business Privacy Protections Page / WhatsApp Business Data Processing Term | Business chats may not be encrypted on the business side. |
| `DIG_08` | Metadata Logging | Telegram Privacy Policy | IP addresses and device types are stored to prevent spam. |
| `DIG_09` | API Hosting Access | WhatsApp Business Data Processing Terms | Third-party sub-processors may process (and temporarily store) message data during delivery |
| `DIG_10` | Transactional Data Sharing | Amazon Privacy Notice | Sharing info with subsidiaries under similar protection. |
| `DIG_11` | Background Location Tracking | Amazon App Privacy Policy/Google Play Store Location Data Disclosure | Collecting actual location via GPS and Wi-Fi points. |
| `DIG_12` | KYC Data Retention | Bangladesh Bank Mobile Financial Services Regulations (2018) | Collecting and keeping NID/biometrics for security. |
| `DIG_13` | Fraud Monitoring | PayPal Acceptable Use Policy | Automated website crawling to combat money laundering. |
| `DIG_14` | AI Training Opt-Out | OpenAI Terms of Use | Using user content to train AI unless opted out. |
| `DIG_15` | Automated Decision-Making | GDPR | Users have the right not to be subject to solely automated decisions that significantly affect them, including AI-driven inferences about creditworthiness or employment |
| `DIG_16` | Dark Patterns | GDPR Recital  | Using deceptive UI to trick users into consent. |
| `DIG_17` | Data Portability | GDPR Article | Moving data to another app in machine-readable format. |
| `DIG_18` | Breach Notification | GDPR Article | Duty to notify users within 72 hours of a hack. |
| `DIG_19` | Sensitive Data Violations | Bangladesh PDPO 2025 | 7 years imprisonment for disclosing sensitive data. |
| `DIG_20` | Profiling Prohibition | GDPR Article | Right not to be subject to decisions based on profiling. |
