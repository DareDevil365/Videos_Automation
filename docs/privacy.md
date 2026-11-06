# Privacy Policy for Yt Automation

**Effective Date:** November 6, 2026

---

## 1. Overview

**Yt Automation** is a private, personal software tool designed, developed, and maintained by its single owner (**DareDevil365**). The application automates the generation of short-form educational and entertainment videos and manages their upload and performance evaluation on the owner's personal YouTube channel. 

This application is strictly for personal use by a single authorized user (the owner). It is not available to the public, does not operate as a Software-as-a-Service (SaaS), does not accept external accounts, and is never used to process data belonging to any third-party individuals or end-users.

---

## 2. Google and YouTube Data Accessed

To facilitate automated publishing and performance tracking, Yt Automation requests OAuth 2.0 authorization from Google with the following specific scopes:

* **`https://www.googleapis.com/auth/youtube.upload`** (`youtube.upload`): Allows the application to upload generated video files, set publication metadata (titles, descriptions, tags, synthetic media declarations, category selections), and apply privacy settings (public, private, or scheduled).
* **`https://www.googleapis.com/auth/youtube.readonly`** (`youtube.readonly`): Allows the application to verify the authenticated YouTube channel's identity, confirm channel IDs, and inspect video processing statuses.
* **`https://www.googleapis.com/auth/yt-analytics.readonly`** (`yt-analytics.readonly`): Allows the application to retrieve aggregated view counts, watch duration, audience retention percentages, likes, comments, and subscriber changes for the owner's published videos.

All access is restricted strictly to the owner's personal Google/YouTube account. The application does not request, access, or store user profiles, contacts, emails, search histories, location data, or any other sensitive personal scopes.

---

## 3. How Data Is Used

Data accessed through Google APIs is used exclusively for the following operational tasks:
1. **Video Publishing**: Uploading rendered video files directly to the owner's YouTube channel without manual drag-and-drop actions.
2. **Channel Performance Analytics**: Reading historical video engagement metrics to evaluate which topics and formats perform best, enabling data-informed refinements to creative scripting templates.
3. **Identity Verification**: Ensuring that upload operations are directed only to the designated channel profile configured in local settings.

Under no circumstances is any data accessed via Google APIs used for advertising, marketing profiling, consumer tracking, or resale.

---

## 4. Storage, Security, and Local Processing

Security and privacy are maintained through strict local-only data boundaries:
* **Local Storage**: All OAuth 2.0 access credentials, refresh tokens, and client identifiers are stored locally on the owner's personal computer in secure, permission-restricted directories.
* **No Remote Servers or Cloud Databases**: Yt Automation operates entirely on the local host. No authorization tokens, video content, or channel analytics are transmitted to, hosted on, or processed by external remote servers, cloud databases, or third-party web backends.
* **Encryption & Transit Security**: All communication with Google APIs takes place exclusively over secure, encrypted HTTPS connections using official Google API client libraries.

---

## 5. Information Sharing and Disclosure

Yt Automation maintains a zero-sharing policy:
* **No Third-Party Sharing**: We do not share, sell, lease, transfer, or distribute any Google API data, channel information, or user credentials to third-party vendors, data brokers, advertisers, or partners.
* **No Public Exposure**: No authentication details or channel tokens are ever committed to public repositories, embedded in client-side code, or exposed via public endpoints.

---

## 6. Google API Services User Data Policy Compliance

> **Yt Automation's use and transfer of information received from Google APIs adheres to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.**

Specifically:
- Human agents or employees cannot read the owner's private Google user data.
- Data is not used or transferred to serve advertisements, including personalized, re-targeted, or interest-based advertising.
- Data is not transferred to any third party except as strictly necessary to fulfill the local software's automated video publishing purpose, comply with applicable laws, or protect the owner's rights.

---

## 7. Data Retention, Revocation, and Deletion

* **Local Deletion**: The owner can permanently delete all local tokens, credentials, and cached analytics at any time by deleting the local credentials files (e.g., `client_secret.json`, `token.json`, or the `data/pipeline/credentials/` directory).
* **Revoking Access via Google**: Access granted to Yt Automation can be immediately and permanently revoked at any time through Google Account security settings at:  
  [https://myaccount.google.com/permissions](https://myaccount.google.com/permissions)

Revoking access instantly invalidates all issued OAuth refresh tokens and halts all API interactions.

---

## 8. Contact Information

If you have any questions, concerns, or requests regarding this Privacy Policy or the operational practices of Yt Automation, please contact:

* **Name**: Yasharth (DareDevil365)
* **Email**: [ultron7008@gmail.com](mailto:ultron7008@gmail.com)
* **Repository**: [https://github.com/DareDevil365/Videos_Automation](https://github.com/DareDevil365/Videos_Automation)

