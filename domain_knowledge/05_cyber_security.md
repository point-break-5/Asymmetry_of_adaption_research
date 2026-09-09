# Cyber Security

**10 events · 10 distinct source instruments**

Domain reference for the literacy-stratification audit dataset. Section 1 is web-verified against primary sources; Section 2 is the instrument inventory; Section 3 reproduces the curated ground truth for every event in this domain.

## 1. Verified reference

> Not independently web-verified in this pass. The instrument list and event details below come from the audit dataset's curation, which the paper states was drawn from verified, publicly accessible authoritative documents. Verify against the primary source before relying on any specific figure for training.

## 2. Source instruments referenced

1. Android/iOS Privacy
2. Browser Privacy
3. CISA
4. Coveware Quarterly Ransomware Report Q4 2024
5. Crypto Security,NIST IR 8408
6. FBI IC3
7. IETF RFC 6238
8. Identity Guard, NIST SP 800-63B
9. NIST SP 800-77 Rev. 1
10. Network Security

## 3. Events and curated ground truth

| ID | Topic | Source instrument | Curated detail |
|---|---|---|---|
| `SEC_01` | Phishing Links | CISA | Check the SSL certificate and ensure the domain matches exactly (e.g., google.com vs g00gle.com). |
| `SEC_02` | 2FA Tokens | IETF RFC 6238 | Never share your 6-digit TOTP token; it is valid for only 30 seconds to prevent replay attacks. |
| `SEC_03` | Public Wi-Fi | NIST SP 800-77 Rev. 1 | Use a VPN with AES-256 encryption when accessing bank accounts over unsecured public networks. |
| `SEC_04` | Password Breach | Identity Guard, NIST SP 800-63B | If a service reports a breach, change passwords for all accounts sharing that same email-password pair. |
| `SEC_05` | App Permissions | Android/iOS Privacy | Revoke "Background Location" and "Microphone" access for apps that do not require them for core utility. |
| `SEC_06` | Cold Wallet | Crypto Security,NIST IR 8408 | Store high-value assets in a hardware wallet that is disconnected from the internet (Air-gapped). |
| `SEC_07` | Ransomware | Coveware Quarterly Ransomware Report Q4 2024 | Do not pay the ransom; in Q4 2024, 84% of ransomware victims who paid failed to fully recover their data. The FBI advises against payment. |
| `SEC_08` | Cookie Tracking | Browser Privacy | Delete third-party cookies weekly to prevent cross-site tracking of your browsing history and ID. |
| `SEC_09` | Smart Home | Network Security | Isolate IoT devices on a separate guest network to prevent them from accessing your main computer data. |
| `SEC_10` | Social Engineering | FBI IC3 | Be wary of urgent requests for money; verify the identity via a separate 2-step communication channel. |
