-- M20: prediction_logs table
-- One row per /predict request. Column set mirrors credit_risk/api/schemas.py's
-- RequestModel exactly (translated to Postgres types), plus request_id/logged_at/
-- issue_d/pred/prob/reason_codes, which aren't part of the API request itself.

CREATE TABLE prediction_logs (
    -- identity / correlation
    id BIGSERIAL PRIMARY KEY,
    request_id UUID NOT NULL UNIQUE,
    logged_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- substituted at request time, not part of RequestModel (needed by prep_one_split)
    issue_d DATE NOT NULL,

    -- RequestModel: required numeric fields
    loan_amnt DOUBLE PRECISION NOT NULL,
    installment DOUBLE PRECISION NOT NULL,
    annual_inc DOUBLE PRECISION NOT NULL,
    dti DOUBLE PRECISION NOT NULL,
    delinq_2yrs DOUBLE PRECISION NOT NULL,
    inq_last_6mths DOUBLE PRECISION NOT NULL,
    open_acc DOUBLE PRECISION NOT NULL,
    pub_rec DOUBLE PRECISION NOT NULL,
    revol_bal DOUBLE PRECISION NOT NULL,
    revol_util DOUBLE PRECISION NOT NULL,
    total_acc DOUBLE PRECISION NOT NULL,
    collections_12_mths_ex_med DOUBLE PRECISION NOT NULL,
    acc_now_delinq DOUBLE PRECISION NOT NULL,
    tot_coll_amt DOUBLE PRECISION NOT NULL,
    tot_cur_bal DOUBLE PRECISION NOT NULL,
    total_rev_hi_lim DOUBLE PRECISION NOT NULL,
    acc_open_past_24mths DOUBLE PRECISION NOT NULL,
    avg_cur_bal DOUBLE PRECISION NOT NULL,
    bc_open_to_buy DOUBLE PRECISION NOT NULL,
    bc_util DOUBLE PRECISION NOT NULL,
    chargeoff_within_12_mths DOUBLE PRECISION NOT NULL,
    delinq_amnt DOUBLE PRECISION NOT NULL,
    mo_sin_old_il_acct DOUBLE PRECISION NOT NULL,
    mo_sin_old_rev_tl_op DOUBLE PRECISION NOT NULL,
    mo_sin_rcnt_rev_tl_op DOUBLE PRECISION NOT NULL,
    mo_sin_rcnt_tl DOUBLE PRECISION NOT NULL,
    mort_acc DOUBLE PRECISION NOT NULL,
    num_accts_ever_120_pd DOUBLE PRECISION NOT NULL,
    num_actv_bc_tl DOUBLE PRECISION NOT NULL,
    num_actv_rev_tl DOUBLE PRECISION NOT NULL,
    num_bc_sats DOUBLE PRECISION NOT NULL,
    num_bc_tl DOUBLE PRECISION NOT NULL,
    num_il_tl DOUBLE PRECISION NOT NULL,
    num_op_rev_tl DOUBLE PRECISION NOT NULL,
    num_rev_accts DOUBLE PRECISION NOT NULL,
    num_rev_tl_bal_gt_0 DOUBLE PRECISION NOT NULL,
    num_sats DOUBLE PRECISION NOT NULL,
    num_tl_120dpd_2m DOUBLE PRECISION NOT NULL,
    num_tl_30dpd DOUBLE PRECISION NOT NULL,
    num_tl_90g_dpd_24m DOUBLE PRECISION NOT NULL,
    num_tl_op_past_12m DOUBLE PRECISION NOT NULL,
    pct_tl_nvr_dlq DOUBLE PRECISION NOT NULL,
    percent_bc_gt_75 DOUBLE PRECISION NOT NULL,
    pub_rec_bankruptcies DOUBLE PRECISION NOT NULL,
    tax_liens DOUBLE PRECISION NOT NULL,
    tot_hi_cred_lim DOUBLE PRECISION NOT NULL,
    total_bal_ex_mort DOUBLE PRECISION NOT NULL,
    total_bc_limit DOUBLE PRECISION NOT NULL,
    total_il_high_credit_limit DOUBLE PRECISION NOT NULL,
    fico_range_low DOUBLE PRECISION NOT NULL,
    fico_range_high DOUBLE PRECISION NOT NULL,

    -- RequestModel: nullable numeric fields (float | None in the Pydantic schema)
    mths_since_last_delinq DOUBLE PRECISION,
    mths_since_last_record DOUBLE PRECISION,
    mths_since_last_major_derog DOUBLE PRECISION,
    mths_since_recent_bc DOUBLE PRECISION,
    mths_since_recent_bc_dlq DOUBLE PRECISION,
    mths_since_recent_inq DOUBLE PRECISION,
    mths_since_recent_revol_delinq DOUBLE PRECISION,

    -- RequestModel: date field
    earliest_cr_line DATE NOT NULL,

    -- RequestModel: categorical fields
    term TEXT NOT NULL,
    emp_length TEXT NOT NULL,
    home_ownership TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    purpose TEXT NOT NULL,
    addr_state TEXT NOT NULL,
    initial_list_status TEXT NOT NULL,

    -- ResponseModel: prediction output
    pred INTEGER NOT NULL,
    prob DOUBLE PRECISION NOT NULL,
    reason_codes JSONB NOT NULL
);
