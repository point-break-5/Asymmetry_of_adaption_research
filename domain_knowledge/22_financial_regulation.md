# Financial Regulation

**5 events · 5 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

**Truth in Lending Act (TILA), 15 U.S.C. §1643 / Regulation Z** — a cardholder's liability for **unauthorised use** of a credit card is capped at **$50**.

**Basel III** — international capital standards agreed by the Basel Committee on Banking Supervision; in the US, capital rules are set by the **FDIC, Federal Reserve and OCC** and modelled on those agreements. The "Basel III Endgame" proposals are the current generation of capital requirements.

**FDIC deposit insurance** — the standard maximum insured amount is **$250,000** per depositor, per insured bank, per ownership category (12 U.S.C. §1821).

**Sources**

- <https://www.fair-debt-collection.com/practice-areas/credit-laws/truth-in-lending-act/>
- <https://www.congress.gov/crs-product/R47855>

## 2. Source instruments referenced

1. Basel III Framework, BCBS (2017 finalization); BIS
2. FDIC, 12 USC §1821; EU Directive 2014/49/EU
3. Truth in Lending Act (TILA), 15 USC §1643; Regulation Z
4. US Bank Secrecy Act; FATF Recommendation 20
5. US Securities Exchange Act 1934; Insider Trading Sanctions Act 1984

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `FRG_01` | Basel III Capital | Basel III Framework, BCBS (2017 finalization); BIS | Banks must maintain a minimum Common Equity Tier 1 (CET1) capital ratio of 4.5% of risk-weighted assets, plus a 2.5% conservation buffer, totaling 7% |
| `FRG_02` | Insider Trading | US Securities Exchange Act 1934; Insider Trading Sanctions Act 1984 | Trading securities based on material non-public information is a criminal offense carrying up to 20 years imprisonment and $5 million fine for individuals. |
| `FRG_03` | Deposit Insurance | FDIC, 12 USC §1821; EU Directive 2014/49/EU | Bank deposits are insured up to $250,000 per depositor per institution (US FDIC) or €100,000 (EU Deposit Guarantee Scheme) in the event of bank failure. |
| `FRG_04` | AML Threshold | US Bank Secrecy Act; FATF Recommendation 20 | Financial institutions must file a Currency Transaction Report (CTR) for any cash transaction exceeding $10,000 and a Suspicious Activity Report (SAR) for suspected money laundering of any amount. |
| `FRG_05` | Credit Card Liability | Truth in Lending Act (TILA), 15 USC §1643; Regulation Z | A cardholder's maximum liability for unauthorized credit card charges is $50; most issuers offer zero-liability policies. |
