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