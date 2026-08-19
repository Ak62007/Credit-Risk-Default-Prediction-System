// Mirrors credit_risk/api/schemas.py — RequestModel / ResponseModel.
// This app treats /predict as a stable external contract; it does not import
// from credit_risk directly.

export type Term = " 36 months" | " 60 months";

export type EmpLength =
  | "< 1 year"
  | "1 year"
  | "2 years"
  | "3 years"
  | "4 years"
  | "5 years"
  | "6 years"
  | "7 years"
  | "8 years"
  | "9 years"
  | "10+ years";

export type HomeOwnership = "MORTGAGE" | "RENT" | "OWN" | "OTHER" | "ANY" | "NONE";

export type VerificationStatus = "Verified" | "Source Verified" | "Not Verified";

export type Purpose =
  | "debt_consolidation"
  | "credit_card"
  | "home_improvement"
  | "other"
  | "major_purchase"
  | "small_business"
  | "car"
  | "medical"
  | "moving"
  | "vacation"
  | "house"
  | "wedding"
  | "renewable_energy"
  | "educational";

export type AddrState = string;

export type InitialListStatus = "w" | "f";

/** Full payload shape the real /predict endpoint expects (~65 fields). */
export interface RequestModel {
  loan_amnt: number;
  installment: number;
  annual_inc: number;
  dti: number;
  delinq_2yrs: number;
  inq_last_6mths: number;
  mths_since_last_delinq: number | null;
  mths_since_last_record: number | null;
  open_acc: number;
  pub_rec: number;
  revol_bal: number;
  revol_util: number;
  total_acc: number;
  collections_12_mths_ex_med: number;
  mths_since_last_major_derog: number | null;
  acc_now_delinq: number;
  tot_coll_amt: number;
  tot_cur_bal: number;
  total_rev_hi_lim: number;
  acc_open_past_24mths: number;
  avg_cur_bal: number;
  bc_open_to_buy: number;
  bc_util: number;
  chargeoff_within_12_mths: number;
  delinq_amnt: number;
  mo_sin_old_il_acct: number;
  mo_sin_old_rev_tl_op: number;
  mo_sin_rcnt_rev_tl_op: number;
  mo_sin_rcnt_tl: number;
  mort_acc: number;
  mths_since_recent_bc: number | null;
  mths_since_recent_bc_dlq: number | null;
  mths_since_recent_inq: number | null;
  mths_since_recent_revol_delinq: number | null;
  num_accts_ever_120_pd: number;
  num_actv_bc_tl: number;
  num_actv_rev_tl: number;
  num_bc_sats: number;
  num_bc_tl: number;
  num_il_tl: number;
  num_op_rev_tl: number;
  num_rev_accts: number;
  num_rev_tl_bal_gt_0: number;
  num_sats: number;
  num_tl_120dpd_2m: number;
  num_tl_30dpd: number;
  num_tl_90g_dpd_24m: number;
  num_tl_op_past_12m: number;
  pct_tl_nvr_dlq: number;
  percent_bc_gt_75: number;
  pub_rec_bankruptcies: number;
  tax_liens: number;
  tot_hi_cred_lim: number;
  total_bal_ex_mort: number;
  total_bc_limit: number;
  total_il_high_credit_limit: number;
  earliest_cr_line: string; // ISO date
  fico_range_low: number;
  fico_range_high: number;
  term: Term;
  emp_length: EmpLength;
  home_ownership: HomeOwnership;
  verification_status: VerificationStatus;
  purpose: Purpose;
  addr_state: AddrState;
  initial_list_status: InitialListStatus;
}

export interface ResponseModel {
  pred: number;
  prob: number;
  reason_codes: Record<string, number>;
}

/** The curated subset of fields exposed as real form inputs. */
export interface CuratedInputs {
  loanAmnt: number;
  term: "36" | "60";
  purpose: Purpose;
  annualInc: number;
  empLength: EmpLength;
  homeOwnership: HomeOwnership;
  dti: number;
  ficoLow: number;
  revolUtil: number;
  creditHistoryYears: number;
  delinq2yrs: number;
  inqLast6mths: number;
  openAcc: number;
}
