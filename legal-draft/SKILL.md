---
name: legal-draft
description: Draft or update legal text from General Legal's attorney-drafted CC0 templates (bundled), or write a short notice or disclaimer backed by a project's own terms. Use for "/legal-draft", "write a disclaimer", "add a notice", "do we need a disclaimer for X", terms of service or terms of use, privacy policy, cookie notice or banner text, DPA, MSA, NDA (mutual or one-way), HIPAA BAA, advisor agreement, offer letter, "contract template", "legal page", upload or copyright notices, DMCA, trademark or "not affiliated" lines, "illustrative example" labels, sign-up agreement lines, consent checkboxes, email footers, "not legal/medical/financial advice" lines, and AI-generated-content disclosures. Also use before changing any existing legal page, so its clause numbers and facts stay right. Not legal advice; it lists what a lawyer or the owner must decide.
---

# legal-draft

Legal text that says only what is true, in words a customer can read.
Full documents start from General Legal's templates (CC0, bundled in
`templates/`). Short notices start from the project's own terms.

This is drafting help, not legal advice. Every answer ends with the
decisions that belong to the owner, and the ones worth a lawyer's hour.

## 1. Find what already exists

Before writing anything, search the project:

- its legal pages (`terms`, `privacy`, `cookies`, `legal` in routes, pages
  and docs) and any notes about them in `AGENTS.md` / `CLAUDE.md`;
- the clause that already covers the need (a "your content" clause, an
  acceptable-use list, a trademark clause);
- the module that names the legal entity, its state and contact email.
  Never type the entity name from memory.

A short notice must point at a clause that exists. If none does, the job
is a clause first (step 3), then the notice.

## 2. Pick the kind of work

| The ask                                                                          | Do                                                           |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| A whole document (terms, privacy policy, cookie notice, NDA, MSA, DPA, BAA, ...) | Step 3 with a template from `references/catalog.md`          |
| A new rule inside an existing document                                           | Step 3, writing one clause, appended                         |
| A line in the product, an email or a page (disclaimer, notice, consent)         | Step 4 with `references/notices.md`                          |
| "Do we need X?"                                                                  | Answer who is responsible and why, then offer the smallest fix |

## 3. Documents and clauses

1. Open `references/catalog.md`, pick the template, then read its
   `templates/<name>/README.md` (when present) and `template.md` in full.
2. Fill every `<mark>`. A mark is either a blank (`[Company]`, `[DATE]`)
   or a whole optional passage (an AI-training paragraph, a cookie banner
   description). For each passage decide keep or cut from facts, never by
   default. Remove the `<mark>` tags from the result.
3. **Say only what the code does.** Providers, cookies, data collected,
   retention, deletion, where data is stored: read each one from the code
   or config and name the file you read it from in your report. A template
   sentence about something the product does not do is cut, not kept "just
   in case".
4. **Decisions are the owner's.** List them instead of choosing:
   governing law and venue (templates default to California or Delaware;
   use the entity's own state only when the owner confirms it), arbitration
   and the class-action waiver, the liability cap, minimum age, refund
   terms, the effective date.
5. **Published clause numbers never move.** Readers and other pages link
   to them (`/terms#clause-6`). Append a new clause at the end, or add a
   sub-clause; never renumber a live document. Give each clause an anchor.
6. Write for customers: short sentences, "you" and "we", no capital-letter
   blocks except where the law asks for conspicuous text (warranty
   disclaimers and liability limits keep theirs).
7. A new provider, cookie or kind of data is a change to the privacy and
   cookie pages in the same change as the code.

## 4. Short notices and disclaimers

Read `references/notices.md` for the patterns. The rules:

- **One or two plain sentences, at the moment it matters**: beside the
  upload button, under the sign-up button, in the email footer. Not a
  site-wide banner.
- **Say what to do, not what is forbidden.** "Only upload pictures and
  videos you own or have permission to show." beats "Uploading copyrighted
  material is prohibited." Nothing alarming, nothing a newcomer reads as a
  warning about the product itself.
- **Link the clause that backs it.** Open the link in a new tab when the
  reader is mid-task (an upload, a form), so following it loses nothing.
- **No checkbox unless something legally needs an affirmative act**: the
  agreement at sign-up (clickwrap), marketing consent where opt-in is
  required, sensitive-data consent. A checkbox on every upload is friction
  with no added protection over a visible line.
- A notice never adds a duty the terms do not already state.

## 5. Report

End every answer with:

- the text, and exactly where it goes (file, component, clause number);
- the facts you read and where from;
- **owner decisions** still open;
- **worth a lawyer's review**: arbitration and class waivers, HIPAA
  (BAA), employment documents, cross-border transfers, anything a
  customer's money or health depends on;
- any gap the templates do not cover (see the catalog's "Not in the
  templates").

## Gotchas

- The Terms of Use template governs a *website*. A paid subscription
  product needs subscription, billing, cancellation and service terms on
  top; the MSA template has the business-to-business versions.
- The templates are US-first. The GDPR privacy policy and the global DPA
  add the EU, UK and Swiss layers; the rest do not.
- The state-privacy-law lists are as of the template's date (see
  `templates/UPSTREAM.md`). Check for newer state laws before publishing.
- General Legal asks that adaptations keep its credit footnote; CC0 does
  not require it. Ask the owner once per project and record the answer in
  the project's notes. A code comment naming the source is the minimum.
- For a Word file, draft in markdown here, then use the docx skill.

## Updating the templates

`templates/UPSTREAM.md` pins the upstream commit. To refresh, clone or pull
`https://github.com/General-Legal/legal-templates` into its own directory,
copy each `templates/<name>/{README.md,template.md}` over the bundled
ones, diff, and update the pin. Never run the upstream scripts.
