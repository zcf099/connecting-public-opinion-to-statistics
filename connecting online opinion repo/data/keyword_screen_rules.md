# Keyword Screening Rules (Final)

> **Screening Summary**
>
> - **Independent double coding:** Two coders independently labeled all 145 dictionary keywords (`keep` vs. `drop`, plus rule code `R1`–`R3` when dropped) using `keyword_screen_codes.csv` before viewing the confirmatory regression results. Nine disagreements were adjudicated jointly.
> - **Agreement and outcome:** Observed agreement = 136/145 (93.8%), Cohen's κ = 0.754. Exactly 20 keywords were removed (125 retained). No domain exceeded its 30% removal cap, so no post-hoc restoration was required.
> - **Final decisions:** Recorded in `data/keyword_screen_codes.csv`.

Companion protocol to *Connecting Online Opinions with Urban Statistics* (WWW '27 Short Papers).

## 1. Purpose

The primary analysis retains all 145 keywords from the original domain dictionary. This keyword screen provides an invariance/robustness check: after removing off-topic terms and single-city proper nouns, does the finding that archived scores track included keyword composition more closely than within-keyword tone still hold?

Screening decides only whether an existing keyword is kept (`keep`) or dropped (`drop`); it neither re-assigns domains nor adds new keywords.

## 2. Unit and Basis of Judgment

1. The coding unit is a `(domain, keyword)` pair evaluated in the context of its assigned domain.
2. Judgments reflect the dominant everyday usage of the term on U.S. city subreddits (since the underlying comment texts were not preserved alongside the archived city-keyword array).
3. When uncertain, retain (`keep`).

## 3. Removal Criteria (`R1`–`R3`)

Drop a keyword if any criterion below holds, and record the rule code:

- **R1 — City-specific proper name:** The term exclusively names an agency, line, system, public figure, or location tied to a single city (e.g., `marta` for Atlanta transit, `nypd` for the New York Police Department, `cuomo` for New York's former governor).
- **R2 — Dominant meaning is off-topic:** The term's predominant sense on city subreddits is unrelated to its assigned domain (apply only when an off-topic sense clearly predominates).
- **R3 — Dominant meaning belongs to another domain:** The term's predominant sense fits one of the other 11 domains better (drop from the misassigned domain without moving it).

## 4. Non-Removal Criteria

Do **not** remove a keyword merely because:

1. It carries inherent positive or negative sentiment (baseline sentiment $\beta_k$ is absorbed by the keyword baseline and is precisely what *composition* measures).
2. Singular/plural forms or near-synonyms co-exist in the dictionary.
3. It is retained in few cities without being a city-specific proper name (retaining-city counts and examples in the coding sheet are solely to help spot proper names).
4. Its score appears counterintuitive or its empirical effect direction is known or suspected.

## 5. Coding Workflow

1. Freeze these written rules prior to coding.
2. Two coders label all 145 rows independently (`coder_A`, `coder_B`) without discussion or viewing each other's sheet, setting `keep` or `drop`, rule `R1`/`R2`/`R3` when dropped, and an optional short rationale.
3. Zero-observation terms (`concert`, `fraud`, absent in all 38 sample cities) are still coded normally and do not affect estimates.
4. Ignore per-domain caps during independent labeling; caps are enforced at merge time.

## 6. Post-Coding Adjudication and Per-Domain Caps

1. Compute inter-coder agreement (Cohen's κ) and flag disagreements.
2. Adjudicate disagreements jointly and record the consensus rationale in `note`.
3. Enforce the 30% per-domain removal cap ($\lfloor 0.30 \times K_g \rfloor$; table below). If a domain ever exceeded its cap, keywords would be restored in fixed order: first coder disagreements, then highest retaining-city count. (In practice, no domain exceeded its cap.)
4. Freeze `data/keyword_screen_rules.md` and `data/keyword_screen_codes.csv` before executing the screened confirmatory analysis, logging their SHA-256 digests in `run_log.json`.

| Domain | Listed Keywords ($K_g$) | Max Removable ($\lfloor 0.30 K_g \rfloor$) | Actually Removed |
|---|---:|---:|---:|
| Public Transportation | 22 | 6 | 4 |
| Driving and Traffic | 11 | 3 | 1 |
| Economy and Income | 13 | 3 | 1 |
| Education | 5 | 1 | 0 |
| Culture and Art | 7 | 2 | 0 |
| Race/Immigration Discourse | 13 | 3 | 2 |
| Recreation | 14 | 4 | 1 |
| Social Problem | 20 | 6 | 3 |
| Governing | 15 | 4 | 4 |
| Policing | 8 | 2 | 1 |
| Neighborhood | 5 | 1 | 1 |
| City Development | 12 | 3 | 2 |
| **Total** | **145** | — | **20** |
