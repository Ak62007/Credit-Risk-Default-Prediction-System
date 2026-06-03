# Column Glossary

Brief, plain-language meaning of each column in the LendingClub dataset.
For the technical types and validation rules, see `tests/test_schema.py`.

## Loan terms (what the loan itself looks like)

| Column | Meaning |
|--------|---------|
| `loan_amnt` | The loan amount the borrower requested. In dollars. |
| `funded_amnt` | The amount LendingClub actually funded. Usually equals `loan_amnt`; can be less if LC funded only part of the request. |
| `funded_amnt_inv` | The portion of `funded_amnt` that came from individual investors (vs. LC's own balance sheet). High correlation with `funded_amnt`. |
| `term` | Loan duration. Always either "36 months" or "60 months". |
| `int_rate` | Annual interest rate (APR), as a percentage (e.g., 12.5 means 12.5%). Set by LendingClub based on their risk assessment. |
| `installment` | The fixed monthly payment the borrower owes. Mathematically derived from `loan_amnt`, `int_rate`, and `term`. |
| `purpose` | Borrower's stated reason for the loan — e.g., debt consolidation, credit card refinancing, home improvement, small business, medical. ~14 distinct values. |
| `title` | The borrower's free-text loan title (e.g., "Pay off credit card"). High-cardinality. |
| `desc` | Borrower's free-text description (legacy column, mostly null in later years). |
| `disbursement_method` | How the loan was paid out — "Cash" (sent to the borrower) or "DirectPay" (sent directly to their creditors). |
| `initial_list_status` | The loan's initial listing status — "w" (whole loan, sold whole to one investor) or "f" (fractional, sold in pieces). Internal LC operational detail. |

## LendingClub's own credit assessment (the "gray area" columns)

These reflect LC's internal credit decision. Useful features but partly circular — if you use them, your model becomes partly a proxy for LC's existing model.

| Column | Meaning |
|--------|---------|
| `grade` | LC's overall risk grade. A (lowest risk) through G (highest risk). |
| `sub_grade` | Finer-grained risk grade. A1 (best) through G5 (worst). 35 levels total. |

## Borrower profile (who the borrower is)

| Column | Meaning |
|--------|---------|
| `annual_inc` | Borrower's self-reported annual income, in dollars. |
| `emp_title` | Borrower's self-reported job title (free text). Very high cardinality. |
| `emp_length` | How long the borrower has been employed. 11 buckets: "< 1 year", "1 year", ..., "9 years", "10+ years". |
| `home_ownership` | Living situation: MORTGAGE, RENT, OWN, OTHER, ANY, NONE. Mortgage holders default least; renters default most. |
| `verification_status` | Whether LC verified the income claim — Verified, Source Verified, or Not Verified. Counterintuitively, verified borrowers default more (LC verifies riskier applicants more closely). |
| `addr_state` | Borrower's US state (two-letter code). Geographic signal. |
| `zip_code` | Partial zip code — first 3 digits + "xx" (e.g., "100xx"). Coarse geographic signal. |
| `application_type` | "Individual" (one borrower) or "Joint App" (two borrowers). After our 2007-2016 filter, only val and test have any joint apps; train has zero. |

## Credit bureau snapshot — FICO and the basics

These come from a credit pull at loan application time.

| Column | Meaning |
|--------|---------|
| `fico_range_low` | Lower bound of the borrower's FICO score range at application. FICO is reported in 5-point bands. |
| `fico_range_high` | Upper bound of the FICO range. Always `fico_range_low + 4`. |
| `earliest_cr_line` | Date of the borrower's first-ever credit account. Used to compute credit history age. String like "Jan-1985". |
| `open_acc` | Number of open credit lines (any type — credit cards, loans, mortgages, etc.) on the credit report. |
| `total_acc` | Total number of credit lines ever opened, including closed ones. |
| `revol_bal` | Total balance currently owed on revolving credit (mostly credit cards), in dollars. |
| `revol_util` | Revolving credit utilization — what % of available revolving credit the borrower is using (e.g., 30% means using $3k of a $10k limit). High values signal stress. |
| `dti` | Debt-to-income ratio. Total monthly debt payments / monthly income, as a percentage. Higher = more financially stressed. Capped/sentinel values exist around 9999. |

## Credit bureau — derogatory marks and delinquencies

Records of past trouble. Mostly null when the borrower has no history of trouble.

| Column | Meaning |
|--------|---------|
| `delinq_2yrs` | Number of times the borrower was 30+ days late on any payment in the last 2 years. |
| `inq_last_6mths` | Number of "hard" credit inquiries in the last 6 months. High values = borrower has been shopping for credit aggressively. |
| `mths_since_last_delinq` | Months since the borrower's last 30+ day delinquency. Null = never delinquent (informative missingness). |
| `mths_since_last_record` | Months since the last derogatory public record (bankruptcy, lien, judgment). Null = no public records. |
| `mths_since_last_major_derog` | Months since the last major derogatory event (90+ days late). Null = never. |
| `pub_rec` | Number of derogatory public records (bankruptcies, tax liens, civil judgments). |
| `pub_rec_bankruptcies` | Subset of `pub_rec`: number of bankruptcy filings specifically. |
| `tax_liens` | Number of tax liens against the borrower. |
| `collections_12_mths_ex_med` | Number of collection accounts in the last 12 months, excluding medical collections (medical are usually treated separately). |
| `chargeoff_within_12_mths` | Number of charge-offs in the last 12 months. |
| `acc_now_delinq` | Number of accounts currently delinquent. Application-time snapshot per LC docs. |
| `delinq_amnt` | Dollar amount currently past due across delinquent accounts. |

## Credit bureau — extended metrics

Detailed account-level statistics from the credit bureau. Many of these are intercorrelated and capture related concepts.

### Account counts and structure
| Column | Meaning |
|--------|---------|
| `num_sats` | Number of satisfactory (paid as agreed) accounts. |
| `num_actv_bc_tl` | Number of active bankcard (credit card) accounts. |
| `num_actv_rev_tl` | Number of active revolving accounts (credit cards + lines of credit). |
| `num_bc_sats` | Number of satisfactory bankcard accounts. |
| `num_bc_tl` | Total number of bankcard accounts (active + closed). |
| `num_il_tl` | Number of installment loans (auto, mortgage, student, etc.). |
| `num_op_rev_tl` | Number of open revolving accounts. |
| `num_rev_accts` | Total revolving accounts. |
| `num_rev_tl_bal_gt_0` | Number of revolving accounts with a non-zero balance (i.e., actively used). |
| `num_tl_op_past_12m` | Number of accounts opened in the last 12 months. |
| `num_accts_ever_120_pd` | Lifetime count of accounts that were ever 120+ days past due. |
| `num_tl_120dpd_2m` | Number of accounts currently 120+ days past due (2-month window). |
| `num_tl_30dpd` | Number of accounts currently 30+ days past due. |
| `num_tl_90g_dpd_24m` | Number of accounts 90+ days past due in the last 24 months. |
| `mort_acc` | Number of mortgage accounts. |
| `acc_open_past_24mths` | Number of credit accounts opened in the last 24 months. |

### Account age / recency
| Column | Meaning |
|--------|---------|
| `mo_sin_old_il_acct` | Months since the borrower's oldest installment account was opened. |
| `mo_sin_old_rev_tl_op` | Months since the oldest revolving account was opened. |
| `mo_sin_rcnt_rev_tl_op` | Months since the most recent revolving account was opened. |
| `mo_sin_rcnt_tl` | Months since the most recent account of any kind was opened. |
| `mths_since_recent_bc` | Months since the most recent bankcard was opened. |
| `mths_since_recent_bc_dlq` | Months since the most recent bankcard delinquency. |
| `mths_since_recent_inq` | Months since the most recent credit inquiry. |
| `mths_since_recent_revol_delinq` | Months since the most recent revolving-account delinquency. |

### Balances and credit limits
| Column | Meaning |
|--------|---------|
| `tot_coll_amt` | Total amount currently in collections, across all accounts. |
| `tot_cur_bal` | Total current balance on all accounts combined. |
| `tot_hi_cred_lim` | Total high credit limit across all accounts (sum of credit limits). |
| `total_rev_hi_lim` | Total high credit limit on revolving accounts only. |
| `total_bal_ex_mort` | Total balance on all accounts excluding mortgage. |
| `total_bc_limit` | Total credit limit across bankcards. |
| `total_il_high_credit_limit` | Total high credit limit on installment loans. |
| `bc_open_to_buy` | Available credit on bankcards (limit minus current balance). Lower = more constrained. |
| `bc_util` | Bankcard utilization — % of bankcard credit being used. Like `revol_util` but bankcard-specific. |
| `avg_cur_bal` | Average current balance across all accounts. |

### Utilization / quality metrics
| Column | Meaning |
|--------|---------|
| `pct_tl_nvr_dlq` | % of the borrower's accounts that have never been delinquent. Higher = cleaner history. |
| `percent_bc_gt_75` | % of bankcards with utilization above 75%. Borrowers maxing out cards. |

## Operational / metadata

| Column | Meaning |
|--------|---------|
| `policy_code` | Internal LC product code. Almost always 1 — constant in our data, no signal. Drop. |
| `issue_d` | The date the loan was issued. Used for temporal splitting and to compute credit age. Not a feature itself. |

## Domain glossary

Quick reference for terms used above:

- **Revolving credit** — Credit where the balance varies and you can re-borrow up to a limit (credit cards, HELOCs). Contrast with installment.
- **Installment credit** — Fixed payments over a fixed term (auto loans, mortgages, personal loans). Contrast with revolving.
- **Bankcard** — A credit card. Subset of revolving credit.
- **Charge-off** — When a creditor writes off the debt as uncollectable. Usually after 180 days of non-payment.
- **Delinquency** — Being late on a payment. 30/60/90/120 days late are common thresholds.
- **Derogatory mark** — Any negative event on a credit report (delinquency, charge-off, bankruptcy, collection).
- **FICO score** — Credit score, range 300-850. Higher is better.
- **DTI (debt-to-income)** — Monthly debt payments divided by monthly income, as a percent.
- **Utilization** — % of available credit being used. High utilization is a stress signal.
- **Hard inquiry** — A credit pull triggered by applying for credit. Multiple recent hard inquiries are a mild negative.