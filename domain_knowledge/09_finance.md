# Finance

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

> Not independently web-verified in this pass. The instrument list and event details below come from the audit dataset's curation, which the paper states was drawn from verified, publicly accessible authoritative documents. Verify against the primary source before relying on any specific figure for training.

## 2. Source instruments referenced

1. BIP-39 (Bitcoin Improvement Proposal 39)
2. Economic Analysis
3. FICO Guidelines
4. General Sense
5. General sense of Trading Policy
6. IRS Publication
7. Investment Strategy
8. Mutual Fund ToS
9. SEC Investor Bulletin
10. SEC Rule 201 / NYSE Rule 7.12

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `FIN_01` | Margin Trading | General sense of Trading Policy | Leverage of 10x means a 10% drop in asset price will result in 100% loss of initial margin. |
| `FIN_02` | Circuit Breakers | SEC Rule 201 / NYSE Rule 7.12 | Stock exchanges halt trading for 15 minutes if the S&P 500 drops 7% (Level 1) or 13% (Level 2) from the previous close; at a 20% decline (Level 3), trading is halted for the remainder of the day. |
| `FIN_03` | Exit Fees | Mutual Fund ToS | Early withdrawal from the fund within 365 days incurs a 2% contingent deferred sales charge. |
| `FIN_04` | Crypto Custody | BIP-39 (Bitcoin Improvement Proposal 39) | Private keys grant absolute control; losing the 12-word seed phrase results in total loss of funds. |
| `FIN_05` | Short Selling | SEC Investor Bulletin | Short selling carries theoretically unlimited risk as there is no cap on how high a stock price can rise. |
| `FIN_06` | Inflation Impact | Economic Analysis | A 7% annual inflation rate will halve the purchasing power of your cash savings in approximately 10 years. |
| `FIN_07` | Dividend Tax | IRS Publication | Non-resident investors are subject to a 30% withholding tax on dividends unless a tax treaty applies. |
| `FIN_08` | Credit Score | FICO Guidelines | Utilizing more than 30% of your available credit limit can negatively impact your overall credit score. |
| `FIN_09` | Ponzi Warning | General Sense | Guaranteed returns of 20% per month are statistically impossible and indicate a fraudulent scheme. |
| `FIN_10` | Asset Allocation | Investment Strategy | Rebalance your portfolio if any single asset class deviates by more than 5% from its target weight. |
