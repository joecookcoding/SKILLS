# Template catalog

All under `templates/<name>/template.md`, from General Legal (CC0 1.0,
`templates/LICENSE`). A `README.md` beside a template, where present,
describes its purpose and key provisions. Sizes are approximate; read the
larger ones in parts.

| Template (`templates/…`)        | Use it for                                                                                           | Decisions it forces                                                                                     | Size  |
| ------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----- |
| `terms-of-use/`                 | The rules for using a website or app: accounts, licence, restrictions, liability, disputes           | Governing law and venue, arbitration (with a 30-day opt-out), liability cap, minimum age, state notices | 25 KB |
| `privacy-policy-us/`            | A privacy policy for a US-only audience, with the state-law (CCPA/CPRA and others) sections          | What is collected and why, AI-training use (optional passage), sensitive data, retention, contact       | 38 KB |
| `privacy-policy-gdpr/`          | The same, plus GDPR and UK GDPR: lawful bases, transfers, EU/UK rights                               | All of the above, plus lawful basis per use, transfer mechanism, EU/UK representative                   | 53 KB |
| `cookie-notice/`                | What cookies and trackers a site sets, and how to manage them                                        | The real cookie list, whether a consent banner exists, analytics/recording tools named (or cut)         | 11 KB |
| `dpa-us/`                       | A processor-friendly data processing addendum for business customers, US personal data               | Subprocessor list (annex), security measures, breach notice window, the agreement it attaches to        | 34 KB |
| `dpa-global/`                   | The same for the US, EU/EEA, UK and Switzerland (with transfer terms)                                | All of the above, plus the transfer mechanism                                                           | 54 KB |
| `master-services-agreement/`    | A business-to-business agreement for a software platform or integration services                     | Fees and user tiers, term and renewal, SLA, liability cap, governing law (Delaware by default)          | 56 KB |
| `mutual-nda/`                   | Two parties sharing confidential information while exploring a deal                                 | Purpose, term, governing law                                                                            | 23 KB |
| `one-way-nda/`                  | Only one side discloses (a contractor, a prospective partner seeing your plans)                      | Purpose, term, governing law                                                                            | 12 KB |
| `business-associate-agreement/` | HIPAA: a vendor that handles protected health information for a covered entity                      | Which services are HIPAA-eligible, the customer's obligations. Lawyer review strongly advised          | 19 KB |
| `advisor-agreement/`            | An advisor's services, equity, IP assignment, confidentiality                                        | Services, dates, equity amount and vesting                                                              | 12 KB |
| `employee-offer-letter/`        | An offer letter for a California exempt employee (with arbitration)                                  | Salary, pay schedule, manager, start date; only California exempt roles as written                     | 17 KB |

## Not in the templates

Write these from the project's facts and the requirements below, mark the
result as needing review, and say so in the report.

- **Copyright complaints (US DMCA).** No template has a notice-and-takedown
  section. To use the safe harbour for files customers store (17 U.S.C.
  §512(c)), a service designates an agent with the US Copyright Office
  (online, a small fee, renewed every three years), publishes how to send a
  notice, removes material when a valid notice arrives, and has a policy
  for ending repeat infringers' accounts. The clause and the registration
  are owner decisions. The notice elements are in `notices.md`.
- **Subscription terms** for a paid product: billing, renewal,
  cancellation, refunds, plan changes. Take the business versions from the
  MSA, and write the consumer versions from how billing actually works.
- **Acceptable use policy** as its own page. The Terms of Use restrictions
  cover the basics; a product hosting customer content usually needs its
  own list (unlawful content, content without rights, security probing,
  overloading the service).
- **Children's privacy (COPPA).** The templates assume adults (18+).
  Anything aimed at children under 13 needs its own work and a lawyer.
- **Subprocessor page.** The DPAs refer to a list; the list itself is a
  page or annex built from the real providers.
- **Short notices and disclaimers:** see `notices.md`.
