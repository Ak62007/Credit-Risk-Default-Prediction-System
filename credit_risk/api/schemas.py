from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class RequestModel(BaseModel):
    loan_amnt: float = Field(
        ...,
        description="The loan amount the borrower requested. In dollars.",
        examples=[3600.0, 20000.0])
    
    installment: float = Field(
        ...,
        description="The fixed monthly payment the borrower owes. Mathematically derived from loan_amnt, int_rate, and term.",
        examples=[820.28, 432.66]
    )
    
    annual_inc: float = Field(
        ...,
        description="Borrower's self-reported annual income, in dollars.",
        examples=[55000.0, 104433.0]
    )
    
    dti: float = Field(
        ...,
        description="Debt-to-income ratio. Total monthly debt payments / monthly income, as a percentage.",
        examples=[16.06, 10.78]
    )
    
    delinq_2yrs: float = Field(
        ...,
        description="Number of times the borrower was 30+ days late on any payment in the last 2 years.",
        examples=[1.0, 3.0]
    )
    
    inq_last_6mths: float = Field(
        ...,
        description="Number of 'hard' credit inquiries in the last 6 months.",
        examples=[1.0, 3.0]
    )
    
    mths_since_last_delinq: float | None = Field(
        description="Months since the borrower's last 30+ day delinquency.",
        examples=[2.0, 5.0],
        default=None
    )
    
    mths_since_last_record: float | None = Field(
        description="Months since the last derogatory public record (bankruptcy, lien, judgment).",
        examples=[2.0, 5.0],
        default=None
    )
    
    open_acc: float = Field(
        ...,
        description="Number of open credit lines (any type — credit cards, loans, mortgages, etc.) on the credit report.",
        examples=[2.0, 6.0]
    )
    
    pub_rec: float = Field(
        ...,
        description="Number of derogatory public records (bankruptcies, tax liens, civil judgments).",
        examples=[2.0, 3.0]
    )
    
    revol_bal: float = Field(
        ...,
        description="Total balance currently owed on revolving credit (mostly credit cards), in dollars.",
        examples=[2765.0, 21470.0]
    )
    
    revol_util: float = Field(
        ...,
        description="Revolving credit utilization — what % of available revolving credit the borrower is using (e.g., 30% means using $3k of a $10k limit).",
        examples=[29.7, 19.2]
    )
    
    total_acc: float = Field(
        ...,
        description="Total number of credit lines ever opened, including closed ones.",
        examples=[13.0, 38.0]
    )
    
    collections_12_mths_ex_med: float = Field(
        ...,
        description="Number of collection accounts in the last 12 months, excluding medical collections.",
        examples=[0.0, 1.0]
    )

    mths_since_last_major_derog: float | None = Field(
        description="Months since the last major derogatory event (90+ days late). Null = never.",
        examples=[6.0, 24.0],
        default=None
    )

    acc_now_delinq: float = Field(
        ...,
        description="Number of accounts currently delinquent.",
        examples=[0.0, 1.0]
    )

    tot_coll_amt: float = Field(
        ...,
        description="Total amount currently in collections, across all accounts.",
        examples=[0.0, 500.0]
    )

    tot_cur_bal: float = Field(
        ...,
        description="Total current balance on all accounts combined.",
        examples=[28854.0, 113418.0]
    )

    total_rev_hi_lim: float = Field(
        ...,
        description="Total high credit limit on revolving accounts only.",
        examples=[15000.0, 42000.0]
    )

    acc_open_past_24mths: float = Field(
        ...,
        description="Number of credit accounts opened in the last 24 months.",
        examples=[2.0, 5.0]
    )

    avg_cur_bal: float = Field(
        ...,
        description="Average current balance across all accounts.",
        examples=[4809.0, 12602.0]
    )

    bc_open_to_buy: float = Field(
        ...,
        description="Available credit on bankcards (limit minus current balance). Lower = more constrained.",
        examples=[3200.0, 9100.0]
    )

    bc_util: float = Field(
        ...,
        description="Bankcard utilization — % of bankcard credit being used.",
        examples=[45.3, 71.2]
    )

    chargeoff_within_12_mths: float = Field(
        ...,
        description="Number of charge-offs in the last 12 months.",
        examples=[0.0, 1.0]
    )

    delinq_amnt: float = Field(
        ...,
        description="Dollar amount currently past due across delinquent accounts.",
        examples=[0.0, 250.0]
    )

    mo_sin_old_il_acct: float = Field(
        ...,
        description="Months since the borrower's oldest installment account was opened.",
        examples=[120.0, 200.0]
    )

    mo_sin_old_rev_tl_op: float = Field(
        ...,
        description="Months since the oldest revolving account was opened.",
        examples=[150.0, 220.0]
    )

    mo_sin_rcnt_rev_tl_op: float = Field(
        ...,
        description="Months since the most recent revolving account was opened.",
        examples=[4.0, 18.0]
    )

    mo_sin_rcnt_tl: float = Field(
        ...,
        description="Months since the most recent account of any kind was opened.",
        examples=[2.0, 10.0]
    )

    mort_acc: float = Field(
        ...,
        description="Number of mortgage accounts.",
        examples=[0.0, 2.0]
    )

    mths_since_recent_bc: float | None = Field(
        description="Months since the most recent bankcard was opened.",
        examples=[8.0, 30.0],
        default=None
    )

    mths_since_recent_bc_dlq: float | None = Field(
        description="Months since the most recent bankcard delinquency.",
        examples=[10.0, 40.0],
        default=None
    )

    mths_since_recent_inq: float | None = Field(
        description="Months since the most recent credit inquiry.",
        examples=[3.0, 12.0],
        default=None
    )

    mths_since_recent_revol_delinq: float | None = Field(
        description="Months since the most recent revolving-account delinquency.",
        examples=[12.0, 36.0],
        default=None
    )

    num_accts_ever_120_pd: float = Field(
        ...,
        description="Lifetime count of accounts that were ever 120+ days past due.",
        examples=[0.0, 1.0]
    )

    num_actv_bc_tl: float = Field(
        ...,
        description="Number of active bankcard (credit card) accounts.",
        examples=[2.0, 5.0]
    )

    num_actv_rev_tl: float = Field(
        ...,
        description="Number of active revolving accounts (credit cards + lines of credit).",
        examples=[3.0, 7.0]
    )

    num_bc_sats: float = Field(
        ...,
        description="Number of satisfactory bankcard accounts.",
        examples=[2.0, 6.0]
    )

    num_bc_tl: float = Field(
        ...,
        description="Total number of bankcard accounts (active + closed).",
        examples=[4.0, 10.0]
    )

    num_il_tl: float = Field(
        ...,
        description="Number of installment loans (auto, mortgage, student, etc.).",
        examples=[2.0, 6.0]
    )

    num_op_rev_tl: float = Field(
        ...,
        description="Number of open revolving accounts.",
        examples=[3.0, 8.0]
    )

    num_rev_accts: float = Field(
        ...,
        description="Total revolving accounts.",
        examples=[8.0, 20.0]
    )

    num_rev_tl_bal_gt_0: float = Field(
        ...,
        description="Number of revolving accounts with a non-zero balance (i.e., actively used).",
        examples=[3.0, 7.0]
    )

    num_sats: float = Field(
        ...,
        description="Number of satisfactory (paid as agreed) accounts.",
        examples=[8.0, 15.0]
    )

    num_tl_120dpd_2m: float = Field(
        ...,
        description="Number of accounts currently 120+ days past due (2-month window).",
        examples=[0.0, 1.0]
    )

    num_tl_30dpd: float = Field(
        ...,
        description="Number of accounts currently 30+ days past due.",
        examples=[0.0, 1.0]
    )

    num_tl_90g_dpd_24m: float = Field(
        ...,
        description="Number of accounts 90+ days past due in the last 24 months.",
        examples=[0.0, 1.0]
    )

    num_tl_op_past_12m: float = Field(
        ...,
        description="Number of accounts opened in the last 12 months.",
        examples=[1.0, 4.0]
    )

    pct_tl_nvr_dlq: float = Field(
        ...,
        description="% of the borrower's accounts that have never been delinquent. Higher = cleaner history.",
        examples=[92.5, 100.0]
    )

    percent_bc_gt_75: float = Field(
        ...,
        description="% of bankcards with utilization above 75%.",
        examples=[0.0, 33.3]
    )

    pub_rec_bankruptcies: float = Field(
        ...,
        description="Subset of pub_rec: number of bankruptcy filings specifically.",
        examples=[0.0, 1.0]
    )

    tax_liens: float = Field(
        ...,
        description="Number of tax liens against the borrower.",
        examples=[0.0, 1.0]
    )

    tot_hi_cred_lim: float = Field(
        ...,
        description="Total high credit limit across all accounts (sum of credit limits).",
        examples=[45000.0, 130000.0]
    )

    total_bal_ex_mort: float = Field(
        ...,
        description="Total balance on all accounts excluding mortgage.",
        examples=[22000.0, 61000.0]
    )

    total_bc_limit: float = Field(
        ...,
        description="Total credit limit across bankcards.",
        examples=[10000.0, 28000.0]
    )

    total_il_high_credit_limit: float = Field(
        ...,
        description="Total high credit limit on installment loans.",
        examples=[15000.0, 55000.0]
    )

    earliest_cr_line: date = Field(
        ...,
        description="Date of the borrower's first-ever credit account. Used to compute credit history age.",
        examples=["1998-03-01", "2010-07-01"]
    )

    fico_range_low: float = Field(
        ...,
        description="Lower bound of the borrower's FICO score range at application.",
        examples=[660.0, 700.0]
    )

    fico_range_high: float = Field(
        ...,
        description="Upper bound of the FICO range. Always fico_range_low + 4.",
        examples=[664.0, 704.0]
    )

    term: Literal[" 36 months", " 60 months"] = Field(
        ...,
        description="Loan duration.",
        examples=[" 36 months"]
    )

    emp_length: Literal[
        "< 1 year", "1 year", "2 years", "3 years", "4 years", "5 years",
        "6 years", "7 years", "8 years", "9 years", "10+ years"
    ] = Field(
        ...,
        description="How long the borrower has been employed.",
        examples=["5 years"]
    )

    home_ownership: Literal["MORTGAGE", "RENT", "OWN", "OTHER", "ANY", "NONE"] = Field(
        ...,
        description="Living situation.",
        examples=["MORTGAGE"]
    )

    verification_status: Literal["Verified", "Source Verified", "Not Verified"] = Field(
        ...,
        description="Whether LC verified the income claim.",
        examples=["Source Verified"]
    )

    purpose: Literal[
        "debt_consolidation", "credit_card", "home_improvement", "other",
        "major_purchase", "small_business", "car", "medical", "moving",
        "vacation", "house", "wedding", "renewable_energy", "educational"
    ] = Field(
        ...,
        description="Borrower's stated reason for the loan.",
        examples=["debt_consolidation"]
    )

    addr_state: Literal[
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
        "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
        "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
        "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
        "WI", "WY", "DC"
    ] = Field(
        ...,
        description="Borrower's US state.",
        examples=["CA"]
    )

    initial_list_status: Literal["w", "f"] = Field(
        ...,
        description="The loan's initial listing status.",
        examples=["w"]
    )
    
class ResponseModel(BaseModel):
    pred: int = Field(
        ...,
        description="Final prediction of the model 1 -> will default, 0 -> repayable"
    )
    
    prob: float = Field(
        ...,
        description="Predicted probability of default"
    )
    
    reason_codes: dict[str, float] = Field(
        ...,
        description="Top 5 features with highest SHAP values that explains the model predictions"
    )