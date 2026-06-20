# day-1
This dataset contains the full LendingClub data available from their site. There are separate files for accepted and rejected loans. The accepted loans also include the FICO scores, which can only be downloaded when you are signed in to LendingClub and download the data.

- from what i have seen the data is about loans. The is the loans data from leadingclub.
- from what i see there are two .csv files one for accepted loans and one for rejected loans.
- both are of around 1.5 gb
- both i think has data from 2007 -> 2018.

#### Known Issues / Caveats
Some columns likely contain post-default information (e.g. payments made, recoveries) that would not be available at loan origination time. These must be identified and excluded during feature engineering to prevent leakage.

# day-2
Started doing some EDA(on the accepted loans):
- data has 151 columns and 2260701 rows
- I checked the loan status column which just tells the current status of the loans, This will be our label.
- This columns takes multiple values. I made some decisions while label creation. Those are as followings:
    1. 'Current', 'In Grace Period', 'Late (16-30 days)' has been dropped.
    2. 'Fully Paid' and 'Does not meet the credit policy. Status:Fully Paid' are set to 0 else are 1.
    3. Class Distribution: 0 -> 78.765025 %, 1 -> 21.234975 %

# day-4

## 1. Target Variable

**Column:** `loan_status`  
**Task:** Binary classification — predict whether a loan will default at origination time.

### Label Mapping

| Original Status | Label | Reasoning |
|----------------|-------|-----------|
| `Fully Paid` | 0 | Clean repayment — definitively good loan |
| `Does not meet the credit policy. Status:Fully Paid` | 0 | Paid back despite policy exception — treated as good |
| `Charged Off` | 1 | Lender wrote off the debt — definitively bad loan |
| `Default` | 1 | Borrower violated loan terms — bad loan (only 40 rows) |
| `Late (31-120 days)` | 1 | Seriously delinquent — high likelihood of charge-off |
| `Does not meet the credit policy. Status:Charged Off` | 1 | Charged off despite policy exception |
| `Current` | **DROPPED** | Loan still active — outcome unknown, cannot label |
| `In Grace Period` | **DROPPED** | Outcome uncertain — just missed one payment |
| `Late (16-30 days)` | **DROPPED** | Outcome uncertain — too early to classify |

> **Decision Note:** `Late (31-120 days)` is labeled as 1 (default). This assumes serious delinquency leads to charge-off. Some of these loans may eventually be repaid — this is an acknowledged simplification.

### Class Distribution (after filtering)

| Class | Count | Percentage |
|-------|-------|------------|
| 0 — Good Loan | ~1,072,000 | ~79% |
| 1 — Default | ~284,000 | ~21% |

> **Moderate class imbalance.** The dataset has roughly a 4:1 ratio of good loans to defaults. This must be addressed during modeling using class weights, oversampling, or threshold tuning.

---

## 2. Temporal Split Strategy

| Split | Period | Purpose |
|-------|--------|---------|
| Train | 2007 – 2015 | Model learning |
| Validation | 2016 | Hyperparameter tuning |
| Test | 2017 – 2018 | Final evaluation |

Temporal splits are used instead of random splits because **loan default rates change over time** (e.g., the 2008 financial crisis, tightening of credit policy). Random splitting would leak future information into training and produce optimistic evaluation metrics that don't reflect real-world performance.

---

## 3. Leakage Analysis

> This is the most critical section. Data leakage occurs when a feature contains information that would not be available at loan origination time (i.e., when a credit decision is made). Using such features produces a model that performs well in testing but fails in production.

### 3.1 Confirmed Leakage — DROP These Columns

#### Post-Origination Payment Activity
These columns accumulate after the loan starts running. They are completely unknown at decision time.

| Column | Description | Why It Leaks |
|--------|-------------|--------------|
| `total_pymnt` | Total payments received to date | Accumulates after loan starts |
| `total_pymnt_inv` | Investor portion of total payments | Same as above |
| `total_rec_prncp` | Principal received to date | Post-origination |
| `total_rec_int` | Interest received to date | Post-origination |
| `total_rec_late_fee` | Late fees received to date | Only exists if borrower is already late |
| `recoveries` | Post charge-off gross recovery | Only exists after default |
| `collection_recovery_fee` | Fee charged when sent to collections | Only exists after default |
| `last_pymnt_d` | Date of last payment | Doesn't exist at origination |
| `last_pymnt_amnt` | Amount of last payment | Post-origination |
| `next_pymnt_d` | Next scheduled payment date | Post-origination |
| `out_prncp` | Remaining outstanding principal | Changes over loan lifetime |
| `out_prncp_inv` | Investor portion of outstanding principal | Same as above |

#### Post-Origination Credit Pulls
| Column | Description | Why It Leaks |
|--------|-------------|--------------|
| `last_credit_pull_d` | Most recent date LC pulled credit | Pulled during loan lifecycle |
| `last_fico_range_high` | Borrower's most recent FICO (high) | Post-origination FICO, not at application |
| `last_fico_range_low` | Borrower's most recent FICO (low) | Same as above |

#### Hardship Plan Columns
Hardship plans are only created after a borrower is already struggling. All of these are pure leakage.

`hardship_flag`, `hardship_type`, `hardship_reason`, `hardship_status`, `hardship_start_date`, `hardship_end_date`, `hardship_amount`, `hardship_length`, `hardship_dpd`, `hardship_loan_status`, `payment_plan_start_date`, `deferral_term`, `orig_projected_additional_accrued_interest`, `hardship_payoff_balance_amount`, `hardship_last_payment_amount`

#### Debt Settlement Columns
Settlement only occurs after a loan has already charged off.

`debt_settlement_flag`, `debt_settlement_flag_date`, `settlement_status`, `settlement_date`, `settlement_amount`, `settlement_percentage`, `settlement_term`

---

### 3.2 Drop — Identifiers and Non-Predictive Columns

| Column | Reason |
|--------|--------|
| `id` | Unique loan ID — random, no predictive signal |
| `member_id` | Unique borrower ID — 100% null in this dataset |
| `url` | LC listing URL — no signal |
| `loan_status` | This IS the target — cannot be a feature |
| `pymnt_plan` | Payment plan indicator — set after borrower struggles |

---

### 3.3 Gray Area — Use with Caution

| Column | Concern |
|--------|---------|
| `grade` | LC's own loan grade — essentially their default prediction. Using it may make your model a proxy of LC's existing model rather than an independent predictor. Keep but document. |
| `sub_grade` | Same concern as `grade` |
| `int_rate` | Set by LC based on risk assessment. Highly correlated with grade. Not technically leakage but carries the same concern. |
| `installment` | Mathematically derived from `loan_amnt` + `int_rate` + `term`. Redundant but not leakage. |
| `funded_amnt` | May differ from `loan_amnt` — keep but note correlation |
| `funded_amnt_inv` | Highly correlated with `funded_amnt` — likely redundant |
| `acc_now_delinq` | Reflects current delinquency state — may change over loan lifetime |
| `delinq_amnt` | Current past-due amount — same concern |

---

### 3.4 Safe to Use — Available at Loan Origination

#### Borrower Profile
`annual_inc`, `emp_length`, `emp_title`, `home_ownership`, `addr_state`, `zip_code`, `verification_status`, `application_type`

#### Loan Terms
`loan_amnt`, `term`, `purpose`, `title`, `desc`

#### Credit Bureau Snapshot (captured at application time)
`fico_range_high`, `fico_range_low`, `earliest_cr_line`, `open_acc`, `pub_rec`, `revol_bal`, `revol_util`, `total_acc`, `dti`, `delinq_2yrs`, `inq_last_6mths`, `mths_since_last_delinq`, `mths_since_last_record`, `collections_12_mths_ex_med`, `pub_rec_bankruptcies`, `tax_liens`, `chargeoff_within_12_mths`

#### Extended Credit Features
All `num_*`, `mo_sin_*`, `mths_since_*`, `open_*`, `bc_*`, `il_*` columns — these are credit bureau snapshots at application time.

#### Joint Application Features
`annual_inc_joint`, `dti_joint`, `verification_status_joint`, all `sec_app_*` columns

#### Temporal Metadata
`issue_d` — useful for temporal analysis and train/val/test splitting. **Do not use as a model feature.**

---

## 4. Known Issues and Caveats

1. **Mixed dtypes warning:** Several columns have mixed types due to inconsistent data entry across years. Always load with `low_memory=False`.

2. **Missing values:** Many columns have extremely high missingness (>90%). These will require decisions on imputation vs. dropping during feature engineering.

3. **Data drift:** LendingClub tightened credit policy over time. Default rates and feature distributions shift across years. This is a feature of the dataset to be aware of, not a bug.

4. **FICO at origination vs. last FICO:** `fico_range_high/low` is captured at origination (safe). `last_fico_range_high/low` is post-origination (leakage). Do not confuse these.

5. **Grade/subgrade circularity:** LendingClub assigns grades partly based on the same features you are modeling. Including grade in your features creates a partially circular model.

6. **`Late (31-120 days)` labeling assumption:** These rows are labeled as defaults (1) under the assumption they will charge off. This may slightly inflate the default rate.

---
*This document should be updated after each major EDA finding.*

# day-5

## Data leakage decisions
So, I have decided to keep these columns:
`annual_inc`, `emp_length`, `emp_title`, `home_ownership`, `addr_state`, `zip_code`, `verification_status`, `application_type`, 
`loan_amnt`, `term`, `purpose`, `title`, `desc`, `fico_range_high`, `fico_range_low`, `earliest_cr_line`, `open_acc`, `pub_rec`, `revol_bal`, `revol_util`, `total_acc`, `dti`, `delinq_2yrs`, `inq_last_6mths`, `mths_since_last_delinq`, `mths_since_last_record`, `collections_12_mths_ex_med`, `pub_rec_bankruptcies`, `tax_liens`, `chargeoff_within_12_mths`,`num_*`, `mo_sin_*`, `mths_since_*`, `open_*`, `bc_*`, `il_*`, `annual_inc_joint`, `dti_joint`, `verification_status_joint`, `sec_app_*`,`issue_d`

I am also including:
`int_rate` - even though this has very high correlation with grade, sub-grade(which was the technique used by LC to grade a customer and according to this grade and sub-grade they decided the int rate.), My analony says we shouldn't keep this column for modelling since it has such a high correlation with grade and sub-grade columns, because i think it some how leaks the target through some backdoor effect, But since i am curious to test this analony, I have planned to train the model with and without this feature and check it's effect.

`funded_amnt` - don't have much corr with loan_amnt hence kept, removed `funded_amnt_inv` since it has huge corr with `funded_amnt`.

`acc_now_delinq` and `delinq_amnt` is kept for further analysis while modelling.

## Recency Bais decisions
So, I grouped the data by issue date and calulated the default_rate for each date and the, Results were very interesting, You can check out the plot in the `reports/figure/default_rate_over_time.png` file.

Here is a bit of analysis:
- 2007-2008 high defaults — this was the 2008 financial crisis. The worst economic collapse since the Great Depression. Unemployment spiked, people lost homes, couldn't pay debts. The entire economy collapsed. LendingClub was also very new in 2007 with very few loans, so small sample size amplifies the rate.

- 2009-2014 stabilization — economy recovered, AND LendingClub tightened credit policy significantly after the crisis.

- 2015-2017 rise — LendingClub aggressively expanded, issuing far more loans to riskier borrowers to grow the business. Volume over quality.

- Sharp drop at end of 2018 — Those loans were issued in late 2018 and haven't had enough time to default yet. A loan issued in December 2018 might default in 2020 — but this dataset only goes to 2018. So recent loans look artificially clean. This is called survival bias or right-censoring.

Based on these observation, I have decided to make following splits:
- 2007-2014 train, 2015 val, 2016-2017 test
- I have also decided to use the 2018 data but later, There are techniques to resolve this survival bias problem. will apply it later.

# day-6
Categorical features analysis of the relevant features:
Key EDA Findings — Categorical Features:
- term — 60 month loans default at 2x the rate of 36 month loans (34% vs 17%). Strong predictor.
- emp_length — weak signal. Default rates barely differ across employment lengths (20-22% range). Likely low importance feature.
- home_ownership — mortgage holders default least (18%), renters most (24%). Moderate signal.
- verification_status — counterintuitive. Verified borrowers default more (25%) than unverified (16%). LendingClub verified riskier - applicants more carefully.
- purpose — strong signal. Small business (31%) vs wedding (12%). 19 percentage point spread.
- application_type — joint applications default more (30%) than individual (21%). Counterintuitive.
- disbursement_method — DirectPay defaults more (26%) than Cash (21%). Minor signal.
- addr_state — Mississippi highest (28%), DC lowest (14%). Geographic signal exists but spread is moderate.
- pymnt_plan — drop. Pure leakage.
- emp_title, title — too many unique values. Need text processing or grouping during feature engineering.
- earliest_cr_line — needs conversion to credit age in years during feature engineering.

# day-7

## What changed and why

Spent today rebuilding the label and the temporal split from scratch. The earlier approach — drop `Current`/`In Grace Period`/`Late (16-30 days)` and label everything else — turns out to have introduced a serious bias that I missed in days 2–5. This entry documents what was wrong, the fix, and the empirical evidence the fix worked.

## The bug: censoring bias from dropping `Current`

The original logic dropped `Current` loans because their outcome was "unknown." On the surface this seemed conservative — don't label what you can't observe. The problem: whether a loan is in `Current` status is **not random**. It is highly correlated with the outcome we're trying to predict.

Concretely: a 60-month loan issued in mid-2017, observed at the Dec 2018 snapshot, has only had ~18 months to either default or pay off. Loans that default tend to default early (most defaults happen by month 18-24). Loans that are good are still dutifully paying — meaning they're in `Current` status at snapshot time.

When I dropped `Current`, I wasn't dropping a random slice. I was dropping the *good loans disproportionately*. The survivors of my filter — the loans that had already resolved by Dec 2018 — were over-representative of fast resolvers, and fast resolution is itself a signal of default. The result: a dataset that looked like recent loans defaulted at extreme rates (close to 30%+ for 60-month 2017 loans), when in reality much of that "default rate" was an artifact of which rows survived the filter.

This is **censoring bias** — when the probability of being in your dataset is correlated with the outcome you're trying to predict, because the snapshot was taken before the world fully revealed itself.

## The fix: observation-window labeling

Instead of filtering by outcome status, filter by **observation time**.

Rule:
1. `snapshot_date` = max(`issue_d`) in raw data ≈ Dec 2018.
2. Define an observation window `W` in months.
3. Include a loan iff `(snapshot_date − issue_d) ≥ W months`.
4. On included loans, label:
   - `Charged Off`, `Default`, `Does not meet... Charged Off`, `Late (31-120 days)` → 1
   - `Fully Paid`, `Does not meet... Fully Paid`, **`Current`** → 0
   - `In Grace Period`, `Late (16-30 days)` → drop (genuinely ambiguous, tiny row count)

The critical change is that `Current` loans which survived W months without going bad are now labeled 0 (good). The selection criterion now depends only on `issue_d` and the calendar — both independent of outcome — so the bias is removed.

The cost: some loans labeled 0 will eventually default after month W (slow defaulters). This is bounded **label noise** in exchange for eliminating uncontrolled **selection bias**. Noise the model can handle; bias it cannot.

## Choosing W

W was selected empirically. For each `Charged Off` loan, computed `months_to_default = last_pymnt_d − issue_d` (note: `last_pymnt_d` is a leakage column never used as a feature — only used here for offline label-quality analysis).

Cumulative distribution of months-to-default:
- By month 12: ~25% of defaults captured
- By month 18: ~50%
- By month 24: ~80%
- By month 30: ~90%
- By month 36: ~95%
- Asymptote around month 50

**Chosen W = 24 months.** This captures ~80% of all defaults, leaves ~20% of eventual defaulters mislabeled as good (the slow defaulters), and — critically — leaves all of 2016 available as a test set.

Alternative considered: W = 30 (~90% capture) would have shrunk the test set to only H1 2016, weakening the temporal-generalization story. The trade was: 10 extra percentage points of label fidelity vs. 6 more months of test data. I prioritized test-set range because the whole point of the temporal split is measuring how well the model handles a meaningfully different time period from training. A test set of half a year of 2016 doesn't tell you that story as well as a full year does.

Caveat: `last_pymnt_d` approximates the charge-off moment but isn't exact (LendingClub officially declares charge-off ~150 days after last payment). The chosen W is robust to this — even if the true timing curve is shifted by ~5 months, W=24 still captures the bulk of defaults.

## Revised temporal split

Old (incorrect) split:
- Train: 2007–2014
- Val: 2015
- Test: 2016–2017

New split under W = 24:
- Train: 2007–2014
- Val: 2015
- Test: 2016 (full year)
- Filtered out: 2017 and 2018 (issued too recently to have cleared W)

The split ceiling is Dec 2016 — anything issued later fails the W = 24 observation-window filter and is excluded from all splits.

## New class distribution

Old regime (drop `Current`): 79% good / 21% default, ~1.35M rows.
New regime (W = 24): 82.80 % good / 17.19 % default, 1316800 rows.

The default rate dropped, as expected, because formerly-deleted `Current` good loans are now correctly counted as label 0.

## Empirical evidence the fix worked

Two checks were run.

**Check 1: Default rate over time (Figure: reports/figures/new_regime.png)**

Comparison of monthly default rate, old regime vs new regime:
- 2007–2014: both regimes produce nearly identical curves. As theory predicts — old loans had time to resolve naturally, so dropping `Current` and using W = 24 converge.
- 2015–2016: old regime showed a dramatic spike to ~28%; new regime stays stable around 17–19%.
- Sharp end-of-period cliff in old regime is gone in new regime (because the filter now correctly excludes too-young loans rather than including them with garbage labels).

## Updated interpretation of earlier findings

Day-5 noted a "rise" in default rates from 2015–2017, interpreted as LendingClub aggressively expanding to riskier borrowers (volume over quality). After the fix, most of this apparent rise disappears. There is still a *mild* upward drift in 2014–2016 (~17% → ~19%), so the underwriting-loosening narrative isn't entirely wrong — but it was significantly inflated by censoring artifacts. The corrected picture is: gentle drift, not dramatic deterioration.

This is a useful reminder: any "trend" in a temporally-snapshotted dataset where the recent end is censored should be treated with suspicion until verified under a proper observation-window filter.

## Things still to address (future work)

- A survival analysis (Cox proportional hazards) could in principle correct the residual ~20% label noise rather than just bound it. Noted as future work; not pursued for this version.
- 2017–2018 data is currently discarded entirely. With more time, a separate experiment could re-incorporate it under a shorter observation window for an additional test set, accepting higher noise as the cost.
- The exact ~150-day gap between last payment and official charge-off declaration was not modeled here. For a more rigorous timing analysis, this offset should be subtracted.

## Updated data card sections that this entry supersedes

- Section 2 (Temporal Split Strategy) of the day-4 entry is now outdated. The new split is Train 2007–2014 / Val 2015 / Test 2016, with 2017–2018 excluded.
- The label-mapping table in Section 1 should now treat `Current` as label 0 (provided it cleared W = 24), not as `DROPPED`.
- The default-rate-over-time analysis in day-5 (and the interpretation about LC expansion-era underwriting) is now substantially revised — see "Updated interpretation of earlier findings" above.

# day-8

## What changed and why

Spent today building Tier 1 data validation tests (pytest schema suite). The
process surfaced three findings about the data that hadn't been fully
internalized in earlier EDA. This entry documents them along with the
methodology choices behind the test suite itself.

## Finding 1: `application_type` is effectively constant in our splits

The day-6 EDA noted: *"application_type — joint applications default more
(30%) than individual (21%)."* That finding was computed on the full raw
data (2007-2018). After the W=24 observation-window filter and the
2007-2016 split boundaries, the picture changes substantially:

| Split | Individual apps | Joint apps  |
|-------|-----------------|-------------|
| Train | 466,071         | 0           |
| Val   | 419,694         | 510         |
| Test  | 423,032         | 8,680       |

LendingClub launched the joint-application product in 2015. Our train set
(2007-2014) predates that launch entirely, so it contains zero joint apps.
Val (2015) has 510 (~0.1% of rows). Test (2016) has 8,680 (~2%).

**Consequence:** `application_type` is *constant* in train and *near-constant*
in val/test. A model trained on train cannot learn anything from it, and
any joint-app-specific behavior cannot be modeled with train data alone.
The day-6 finding does not transfer to our modeling data.

**Lesson:** EDA findings on raw data don't automatically apply to filtered
training data. Re-validate findings against the actual modeling splits.

## Finding 2: Three distinct mechanisms producing 100% null columns

The empty-column validation test surfaced 30 columns that are 100% null
in train. Investigation revealed three structurally different causes,
which are documented in `tests/test_schema.py` as named buckets:

**Bucket 1 — Secondary-applicant fields never populated (13 columns).**
All `sec_app_*` fields plus `revol_bal_joint`. These are 100% null across
all 1.3M rows in *every* split, even though joint applications exist in
val and test. LendingClub captures secondary-borrower data internally but
does not expose it in the public CSV dump, likely for privacy reasons.
This is a property of the data publication policy, not a sampling
accident. The columns are retained in `dataset.py` rather than dropped
because:
1. The emptiness is a property of *this snapshot*, not a logical
   exclusion. A future LendingClub release with a different redaction
   policy could populate them.
2. `dataset.py` should encode invariants of the problem (leakage,
   identifiers, target source), not properties of the current data.
3. The columns will be dropped in `features.py` for the current
   modeling cycle.

**Bucket 2 — Joint-aggregate fields, null in train only (3 columns).**
`annual_inc_joint`, `dti_joint`, `verification_status_joint`. These are
the *joint* (combined-borrower) versions of standard fields. They are
populated for the joint-app rows in val and test but 100% null in train
because the joint-app product didn't exist pre-2015.

**Bucket 3 — Installment-tracker block, null in train only (14 columns).**
`open_acc_6m`, `open_act_il`, `il_util`, etc. LendingClub started
capturing these data points around 2015, so pre-2015 train data has them
as 100% null even for individual loans. This is a *data-collection*
change, distinct from Bucket 2's *product* change.

Buckets 2 and 3 look similar (null in train, populated in val/test) but
the underlying mechanisms differ. Bucket 2 is null because the feature
doesn't apply pre-2015; Bucket 3 is null because LC didn't record it
pre-2015 even when it would have applied.

## Finding 3: Refining the day-4 missingness numbers

Day-4 estimated `sec_app_*` columns as "~98% null." The actual figure on
the filtered modeling data is **100% null** in every split. The 98% came
from a quick scan of raw data that included rows we now exclude. Updated
estimates for the empty-column groups, on the modeling splits:

| Group | day-4 estimate | actual |
|-------|----------------|--------|
| `sec_app_*` | ~98% null | 100% null (all splits) |
| Installment tracker (`il_util` etc.) | ~60% null | 100% null in train |
| Joint aggregate (`annual_inc_joint` etc.) | (not flagged separately) | 100% null in train |

The day-4 missingness work was directionally correct but should not be
taken as quantitatively precise on the modeling splits. The exact
percentages and the per-split breakdown are now documented in
`tests/test_schema.py::ALLOWED_FULLY_NULL`.

## On the test suite architecture

The Tier 1 schema suite (`tests/test_schema.py`) contains 17 parametrized
checks covering: required columns present, expected logical dtypes, no
nulls in critical columns (`issue_d`, `target`), target is binary, row
counts match `metadata.json`, no leakage columns present, no
unexpectedly-empty columns.

Two design choices worth noting:

- **Logical dtypes over exact dtypes.** Initial tests used exact dtype
  strings ("datetime64[ns]", "object") and failed because pyarrow
  round-trip normalizes timestamps to microsecond precision and string
  columns to a `string` dtype. The contract was rewritten to use
  `pd.api.types.is_*_dtype` helpers, which check *kinds* (datetime, int,
  float, string) rather than exact dtype strings. This is robust to
  pandas/pyarrow version changes.

- **Allowlist for documented sparsity.** The empty-column test exempts
  the three buckets above so it fires only on *new* fully-null columns
  (regression detection). The allowlist is in code, with comments tying
  each entry back to a finding. New entries require a comment explaining
  why.

## Implications for `features.py` (Milestone 5)

Captured here as a TODO so the decisions aren't forgotten:

- The 13 Bucket-1 columns will be dropped — they are unpopulated and
  cannot contribute signal in this snapshot.
- The 3 Bucket-2 columns will likely be dropped, since a train-fit model
  cannot use them. A possible alternative is to engineer an "is joint
  app" indicator from `application_type`, but the small joint-app
  fraction in val (0.1%) makes this marginal.
- The 14 Bucket-3 columns are a harder call. Options:
  (a) drop them outright;
  (b) keep them and treat missingness as a feature using a "vintage
      2015+" indicator;
  (c) restrict training to 2014+ data only, losing temporal range but
      gaining feature coverage.
  The right answer depends on whether the installment-tracker signal is
  strong enough to justify the loss of pre-2015 training data.

## Updated sections that this entry supersedes

- Day-4 missingness estimates (Section "Missingness Patterns") are now
  superseded by the verified per-split numbers above. The day-4 entry
  remains as the original observation; this entry has the corrections.
- Day-6 finding on `application_type` ("joint apps default 30% vs 21%")
  remains true for the *raw data* but does not apply to our modeling
  splits. Day-6 is not edited; this caveat is the correction.

# Feature Engineering
## M6: Baseline modeling (Pass-1 features)

Three baseline models trained on Pass-1 feature matrix (median imputation, one-hot encoding, drop free-text columns, regime A — included LendingClub's credit-decision features `grade`, `sub_grade`, `int_rate`).

**Test set performance:**

| Model | PR-AUC | ROC-AUC | Brier |
|-------|--------|---------|-------|
| LR    | 0.311  | 0.697   | 0.130 |
| RF    | 0.291  | 0.678   | 0.132 |
| XGB   | 0.307  | 0.697   | 0.131 |

Threshold tuned via cost matrix (FN = $10000, FP = $2000) on validation set. Optimal threshold ≈ 0.15 for LR and XGB, 0.18 for RF — all near the base rate of 0.17, confirming probabilities were well-calibrated.

**Key finding from M6:** three structurally different model families (linear, bagged trees, boosted trees) converged within 2 PR-AUC points. This convergence motivated Pass-2 feature engineering rather than further model tuning — when three different model families produce nearly identical performance, the bottleneck is features or inherent signal, not model capacity.

## Pass-2: Feature engineering experiments

### Regime A vs Regime B comparison

Tested whether the model's predictive performance depends on LendingClub's own credit-decision features.

- Regime A: includes `grade`, `sub_grade`, `int_rate`.
- Regime B: excludes them.

| Model | Regime A test PR-AUC | Regime B test PR-AUC | Delta |
|-------|----------------------|----------------------|-------|
| LR    | 0.311                | 0.301                | −0.010 |
| RF    | 0.291                | 0.274                | −0.017 |
| XGB   | 0.307                | 0.299                | −0.008 |

**Finding:** Removing LC's credit-decision features cost 1–2 PR-AUC points. The model draws meaningful signal from primitive features (income, DTI, credit history) independently of LC's pricing. Project continued in regime B going forward to demonstrate the model has independent predictive signal beyond piggybacking on LC's risk system.

### Pass-2 feature engineering experiments (regime B)

Tested six structurally different feature engineering hypotheses against three baseline models. No experiment moved test PR-AUC by more than 0.01 on any model.

| Experiment | Hypothesis | Result |
|------------|-----------|--------|
| Ordinal encoding for `grade`, `sub_grade` | One-hot destroys ordinal signal that LR can't recover | Flat (skipped in regime B since these are dropped) |
| Target encoding for `zip_code` (out-of-fold CV) | Geographic risk is real signal being thrown away | Flat |
| Engineered ratios (`loan_to_income`, `installment_to_income`) | LR can't construct ratios from raw columns; explicit ratios should help | Flat |
| Missingness indicators (`mths_since_*` family + bureau-data cohort indicator) | Null is informative — encodes "event never happened" rather than absence of data | Flat |
| All combined | Combinations of weak individual effects might unlock interaction signal | Flat |
| Text features via target encoding (`title`, `emp_title`) | Free-text occupation/loan-title fields contain semantic risk signal | Flat |

**Pass-2 conclusion:** Six independent experiments confirm a robust predictive ceiling at test PR-AUC ≈ 0.30 on LendingClub origination data. The ceiling holds across three model families (LR, RF, XGB) and across structurally different feature representations (encoding, ratios, indicators, text). This indicates the ceiling is inherent to the data, not to feature representation or model capacity.

**Interpretation:** 24-month default outcomes depend heavily on borrower life events occurring after loan issuance — job loss, illness, divorce, recession exposure — that are unobservable at origination. Origination features cap out at the point where unobservable post-issuance events begin to dominate the outcome.

**Implications for project scope:**
- Pass-1 regime-B feature pipeline retained as production feature set. Pass-2 additions discarded as adding implementation cost without measurable benefit.
- M7 hyperparameter tuning expectations recalibrated: targeting 0.32–0.33 test PR-AUC (1–3 point lift from tuning), not 0.40+.
- Project value will be demonstrated through downstream milestones (production deployment, drift monitoring, fairness audit, error segmentation) rather than through further PR-AUC optimization.

---

## M7: XGBoost hyperparameter tuning with Optuna

Tuned XGBoost via Optuna (TPE sampler, 50 trials, seed=42) using
time-series 5-fold CV on the training set. Search space: 8
hyperparameters — n_estimators, max_depth, learning_rate (log),
subsample, colsample_bytree, min_child_weight, reg_alpha (log),
reg_lambda (log). Objective: maximize mean PR-AUC across folds.
Best CV PR-AUC: 0.313.

**Best hyperparameters found:**
| Parameter         | Value     | Range searched |
|-------------------|-----------|----------------|
| n_estimators      | 895       | 100-1000       |
| max_depth         | 7         | 3-10           |
| learning_rate     | 0.0114    | 0.01-0.3       |
| subsample         | 0.58      | 0.5-1.0        |
| colsample_bytree  | 0.77      | 0.5-1.0        |
| min_child_weight  | 10        | 1-10           |
| reg_alpha         | ~0        | 1e-8 to 10     |
| reg_lambda        | ~0        | 1e-8 to 10     |

**Tuned model performance:**
| Split | PR-AUC | ROC-AUC | Brier |
|-------|--------|---------|-------|
| Train | 0.382  | 0.744   | 0.123 |
| Val   | 0.349  | 0.708   | 0.137 |
| Test  | 0.310  | 0.694   | 0.130 |

Tuning lifted test PR-AUC from 0.299 (baseline XGB) to 0.310 (+0.011).
Within the 1-3 point range expected from hyperparameter tuning,
consistent with the feature ceiling identified in Pass-2.

**Interpretation of chosen hyperparameters:**
Optuna pushed regularization through structural mechanisms (aggressive
row subsampling at 0.58, large min_child_weight at 10) rather than
through L1/L2 leaf-weight regularization (both reg_alpha and reg_lambda
near zero). Many trees (895) with very small learning rate (0.011) —
the classic "slow careful learning" pattern. Train PR-AUC decreased
from baseline's 0.414 to 0.382, indicating less memorization while
generalization improved.

**Known boundaries of the search:**
- min_child_weight hit upper bound (10) — expanded search to 1-30 might
  find slightly better
- n_estimators landed at 895 of 1000 — expanded range to 2000 might help
- Deferred as future work; expected gain <0.5 PR-AUC points, below the
  threshold of meaningful project-level impact

**Calibration check:** Brier (0.130 test) effectively unchanged from
baseline XGB (0.132). Tuning preserved calibration. Threshold returned
to 0.16 (cost-optimal theoretical value 0.18), consistent with
well-calibrated probabilities. Full reliability diagnostic in M8.

---

## M8: Calibration analysis

Diagnostic on tuned XGBoost from M7.

**Val Brier score: 0.137.** Constant-base-rate predictor reference:
0.147 (where base_rate × (1 - base_rate) = 0.18 × 0.82). Model beats
the constant predictor — calibration is meaningful.

**Reliability diagram (val, 10 equal-width bins):** Calibration curve
lies close to the diagonal across the bulk of predicted probabilities
(0 to ~0.6), which contains essentially all val mass per the
predicted-probability histogram. Slight upward deviation at predicted
0.7+ (model underconfident — empirical rate higher than predicted),
but histogram shows near-empty bins in that region (few hundred loans
out of 420k). Interpreted as small-N noise, not systematic
miscalibration.

**Decision: no recalibration step applied.** `CalibratedClassifierCV`
with isotonic regression was considered as the standard remediation
but not applied — diagnostic shows existing probabilities are honest
across the regions with operational volume. Adding a recalibration
step would solve a problem that doesn't exist on this data.

**Implication for downstream use:** Model probabilities can be used
directly for cost-based threshold tuning (M9 / already done in M6) and
for any downstream risk-based pricing logic, without further
transformation. The cost-optimal threshold of 0.16 sits near the
theoretical value (fp_cost / (fp_cost + fn_cost) = 0.18), consistent
with well-calibrated outputs.

---

## M9: Cost-based threshold framework

Cost-derivation framework documented in references/cost_framework.md.
Threshold tuning mechanism was implemented in M6 and applied in M7.
M9's contribution is the standalone documentation artifact explaining
the cost assumptions and a sensitivity analysis bounding the risk of
those placeholder estimates.

**Cost model:**
- FN cost = principal × LGD ≈ $10,000 (estimate: avg loan $15K, LGD ~65%)
- FP cost = forgone interest ≈ $2,000 (estimate over 36-month loan term)
- Cost ratio (FN:FP) = 5:1

**Threshold derivation:**
- Empirical optimum on val: t = 0.16
- Theoretical optimum: fp_cost / (fp_cost + fn_cost) = 2000/12000 ≈ 0.167
- Empirical and theoretical agree, confirming calibration (also verified in M8)

**Sensitivity analysis (penalty for using t=0.16 if true cost ratio differs):**
| True ratio | Penalty |
|------------|---------|
| 3:1        | ~8%     |
| 4.5:1      | ~0%     |
| 6:1        | ~1%     |
| 10:1       | ~18%    |

**Findings:**
- Model is robust within the plausible range (3:1 to 6:1) — at most 8% off optimum.
- Outside this range, the cost penalty grows substantially. The 10:1 case
  (FN much more expensive than assumed) costs 18% more than optimal.
- Asymmetry: underestimating FN cost is more dangerous than overestimating
  it. If true ratio is uncertain, a more conservative threshold is safer.

**Production implications:** In a deployed system, cost numbers would be
reviewed quarterly with finance teams and potentially per-loan rather
than global. The framework generalizes to per-loan cost computation
without architectural change.

---

## M10: Segmented error analysis

Evaluated tuned XGBoost model (M7) on five segmentation features
across the test set, holding the model and threshold (t=0.16) fixed.
Six metrics per segment: n, n_positives, base_rate, ROC-AUC, PR-AUC,
mean_pred_proba, Brier, precision, recall.

Methodology note: per-segment metrics computed at the global threshold
to mimic deployment. Re-tuning threshold per segment was considered
but is a different question (per-segment policy design) than the M10
question (how does the deployed model behave across segments).

### Segment 1: `term`

| segment    | n       | base_rate | ROC-AUC | PR-AUC | mean_pred | Brier | precision | recall |
|------------|---------|-----------|---------|--------|-----------|-------|-----------|--------|
| 36 months  | 321,815 | 0.152     | 0.693   | 0.282  | 0.136     | 0.121 | 0.260     | 0.540  |
| 60 months  | 109,897 | 0.217     | 0.693   | 0.374  | 0.253     | 0.158 | 0.258     | 0.908  |

Ranking quality identical across segments (ROC-AUC 0.693 on both).
Calibration good on both (mean_pred within 1-3 percentage points of
base_rate). The PR-AUC and recall asymmetry reflect base-rate
differences and the fixed threshold sliding to different operating
points on each segment's PR curve — not a model defect.

### Segment 2: `application_type`

| segment    | n       | base_rate | ROC-AUC | PR-AUC | mean_pred | Brier | precision | recall |
|------------|---------|-----------|---------|--------|-----------|-------|-----------|--------|
| Individual | 423,032 | 0.169     | 0.695   | 0.313  | 0.164     | 0.130 | 0.261     | 0.656  |
| Joint App  | 8,680   | 0.163     | 0.687   | 0.285  | 0.239     | 0.136 | 0.209     | 0.869  |

**Most important finding in M10.** Joint applications didn't exist in
training data (Joint product introduced by LendingClub in 2015; training
spans 2007-2014). The model has never seen this loan type.

- **Ranking generalizes:** ROC-AUC 0.687 on Joint vs 0.695 on
  Individual. The model orders Joint loans about as well as Individual,
  drawing on primitive features (income, DTI, credit history) that
  transfer.
- **Calibration breaks:** Mean predicted on Joint = 0.239, actual
  base rate = 0.163. Model overpredicts Joint default risk by 7.6
  percentage points (47% relative). For risk-based pricing, this
  would over-price Joint loans by ~50% and lose them to better-calibrated
  competitors. The operational consequence shows up in recall (0.87
  vs 0.66 on Individual) and precision (0.21 vs 0.26): the model
  flags far more Joint loans for rejection than its underlying ranking
  warrants.

This is exactly the failure mode M19 (PSI drift detection) is built
to catch in production: a feature distribution shift the trained model
can't reason about. The honest deployment-time remediation would be
per-segment calibration (isotonic regression fit on Joint predictions
specifically).

### Segment 3: `home_ownership`

| segment   | n       | base_rate | ROC-AUC | PR-AUC | mean_pred | Brier | precision | recall |
|-----------|---------|-----------|---------|--------|-----------|-------|-----------|--------|
| MORTGAGE  | 210,252 | 0.143     | 0.695   | 0.273  | 0.149     | 0.115 | 0.236     | 0.598  |
| RENT      | 168,655 | 0.200     | 0.685   | 0.345  | 0.187     | 0.149 | 0.281     | 0.721  |
| OWN       | 52,695  | 0.169     | 0.678   | 0.294  | 0.164     | 0.133 | 0.253     | 0.641  |
| ANY       | 110     | 0.164     | —       | —      | —         | —     | —         | —      |

(ANY segment excluded from interpretation: n=110, n_positives=18,
sample too small for stable metrics.)

Calibration good across all three real segments. Mean predicted within
1 percentage point of base rate everywhere. Ranking comparable across
segments (ROC-AUC 0.68-0.70). The PR-AUC differences reflect base-rate
variation (RENT highest at 20%, MORTGAGE lowest at 14%), not differential
model quality. Confirms the model handles a stability-proxy feature
correctly when it has training volume across all categories.

### Segment 4: `annual_inc` (income brackets)

| segment    | n       | base_rate | ROC-AUC | PR-AUC | mean_pred | Brier | precision | recall |
|------------|---------|-----------|---------|--------|-----------|-------|-----------|--------|
| <$40K      | 72,497  | 0.204     | 0.660   | 0.324  | 0.200     | 0.154 | 0.261     | 0.770  |
| $40K-$80K  | 208,784 | 0.177     | 0.692   | 0.321  | 0.173     | 0.135 | 0.265     | 0.679  |
| $80K-$120K | 96,273  | 0.149     | 0.700   | 0.292  | 0.145     | 0.118 | 0.254     | 0.578  |
| >$120K     | 54,101  | 0.125     | 0.699   | 0.250  | 0.128     | 0.103 | 0.226     | 0.496  |

Default rates fall monotonically with income (20.4% → 12.5%) — expected
given income's role as a financial-stability proxy. Calibration is
excellent across all four brackets (mean_pred within 0.5 percentage
points of base_rate everywhere).

**Finding worth flagging:** ROC-AUC drops to 0.660 on the <$40K segment
versus 0.69-0.70 elsewhere. The model's *ranking ability* is meaningfully
weaker for low-income borrowers. Likely causes: more variable outcomes
at low income (default risk depends on small life events not captured
in origination features), feature ceiling effects (most low-income
borrowers cluster at the high-stress end of features like DTI, reducing
their discriminative power), higher base rate making ranking inherently
harder.

This is operationally significant: the model is least precise on the
segment where lending decisions matter most for the borrower. **Flagged
for M11 fairness audit** — income likely correlates with protected
attributes (race, age) in real populations, so income-segment performance
gaps may translate to disparate-impact concerns.

### Segment 5: `purpose`

| segment            | n       | base_rate | ROC-AUC | PR-AUC | mean_pred | Brier |
|--------------------|---------|-----------|---------|--------|-----------|-------|
| car                | 4,788   | 0.126     | 0.687   | 0.227  | 0.133     | 0.105 |
| home_improvement   | 30,996  | 0.145     | 0.694   | 0.271  | 0.143     | 0.116 |
| credit_card        | 91,101  | 0.146     | 0.702   | 0.281  | 0.142     | 0.116 |
| major_purchase     | 10,354  | 0.156     | 0.702   | 0.305  | 0.145     | 0.122 |
| vacation           | 3,249   | 0.163     | 0.693   | 0.302  | 0.146     | 0.128 |
| other              | 28,311  | 0.166     | 0.680   | 0.293  | 0.165     | 0.130 |
| medical            | 5,417   | 0.179     | 0.661   | 0.291  | 0.166     | 0.140 |
| debt_consolidation | 247,233 | 0.180     | 0.689   | 0.322  | 0.178     | 0.137 |
| moving             | 3,213   | 0.195     | 0.686   | 0.349  | 0.176     | 0.146 |
| renewable_energy   | 303     | 0.201     | —       | —      | —         | —     |
| house              | 1,991   | 0.209     | 0.707   | 0.373  | 0.177     | 0.152 |
| small_business     | 4,754   | 0.239     | 0.675   | 0.393  | 0.234     | 0.169 |

(renewable_energy excluded: n_positives=61, ranking metrics unstable.
house and vacation reported but interpreted with caution due to
moderate sample sizes.)

Across 11 purposes covering 4.6 percentage points of base-rate
variation (12.6% to 23.9%), calibration is uniformly excellent —
mean_pred within 1-2 percentage points of base_rate at every level.
Small_business at 24% base rate is the highest-risk segment and the
model predicts 23.4% — essentially perfect calibration on the segment
furthest from the population mean.

Soft finding: ROC-AUC drops to 0.66 on `medical` loans (n=5,417,
n_positives=969). Possible that medical-debt borrowers have a risk
profile less well-captured by origination features. Not a strong
finding on this sample size, but worth noting.

### Cross-cutting findings

**1. Calibration generalizes when training volume is present, fails
without it.** The contrast that defines M10:

- **small_business** (purpose): 24% base rate, mean_pred 23.4%. Highly
  distinctive risk segment, well-represented in training, perfectly
  calibrated.
- **Joint App** (application_type): 16% base rate, mean_pred 24%.
  Absent from training (post-2015 product), systematically overpredicted.

Same model, two different category situations, two outcomes. Demonstrates
clearly what the model can and cannot be trusted to do.

**2. Ranking is mostly stable across segments.** ROC-AUC clusters
around 0.68-0.70 across most segment values. The two notable exceptions
(<$40K income at 0.660, medical purpose at 0.661) are both at the
high-base-rate end of their respective features, suggesting the model's
ranking power degrades modestly when discriminating among many
positives.

**3. Operational metrics (precision, recall) are dominated by base-rate
variation, not model quality differences.** At a fixed threshold,
higher-base-rate segments mechanically produce higher recall and
slightly lower precision. This pattern is universal across all five
segmentations and is the right behavior for a calibrated model with
a global threshold — not a defect, but worth understanding when
reading segment tables.

**4. Income-as-proxy flag for M11.** The <$40K income segment shows
weaker ranking, highest base rate, and highest threshold-crossing
rate. In a real deployment with demographic features, income would
likely correlate with protected attributes; the segment-level
disparities seen here would translate to disparate-impact concerns
worth auditing. LendingClub data lacks demographic fields, so M11's
fairness audit will be limited, but the income-bracket findings give
M11 a concrete hook.

### Implications for downstream milestones

- **M11 (fairness audit):** anchor analysis on income brackets given
  their proxy potential.
- **M19 (drift detection):** prioritize monitoring `application_type`
  category distribution — the Joint applications case is exactly the
  failure mode PSI is designed to flag.
- **M20 (prediction logging dashboard):** log segment IDs (term,
  home_ownership, purpose, income bracket, application_type) per
  prediction so segment-level metrics can be tracked over time in
  production.
- **Deployment policy:** the global threshold of 0.16 produces honest
  but uneven operational metrics across segments. Per-segment thresholds
  would be a defensible policy choice (not a model change), particularly
  to tighten the Joint application threshold or loosen the 36-month
  threshold. Documented as a deployment-time choice; not implemented
  here.

  