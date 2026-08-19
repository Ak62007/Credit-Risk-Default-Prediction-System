import type { CuratedInputs, RequestModel, Term, VerificationStatus } from "./types";
import { clamp } from "./utils";

/**
 * Turns the ~13 curated inputs a visitor actually edits into the full ~65-field
 * payload the real /predict endpoint expects. The uncurated fields aren't random —
 * they're derived deterministically from the curated ones plus a composite
 * "risk score", so a full profile stays internally consistent (e.g. utilization,
 * balances, and delinquency-history fields all move together) instead of being
 * frozen leftovers from whichever preset was last loaded.
 */
export function buildPayload(inputs: CuratedInputs): RequestModel {
  const {
    loanAmnt,
    term,
    purpose,
    annualInc,
    empLength,
    homeOwnership,
    dti,
    ficoLow,
    revolUtil,
    creditHistoryYears,
    delinq2yrs,
    inqLast6mths,
    openAcc,
  } = inputs;

  const termMonths = term === "36" ? 36 : 60;
  const termLiteral: Term = term === "36" ? " 36 months" : " 60 months";
  const ficoHigh = ficoLow + 4;

  // Composite 0..1 risk score driving the fields the visitor never sees directly.
  const riskScore = clamp(
    0.35 * clamp((820 - ficoLow) / (820 - 600), 0, 1) +
      0.25 * clamp(dti / 40, 0, 1) +
      0.2 * clamp(revolUtil / 100, 0, 1) +
      0.12 * clamp(delinq2yrs / 5, 0, 1) +
      0.08 * clamp(inqLast6mths / 10, 0, 1),
    0,
    1,
  );

  const apr = estimateApr(ficoLow);
  const installment = amortizedPayment(loanAmnt, apr, termMonths);
  const earliestCrLine = yearsAgoIso(creditHistoryYears);

  // Revolving credit picture
  const totalRevHiLim = round(clamp(annualInc * 0.22 * (1 - 0.4 * riskScore), 2000, 250000));
  const revolBal = round((revolUtil / 100) * totalRevHiLim);
  const bcUtil = clamp(revolUtil * 1.05, 0, 100);
  const totalBcLimit = round(totalRevHiLim * 0.6);
  const bcOpenToBuy = Math.max(0, round(totalBcLimit - (bcUtil / 100) * totalBcLimit));
  const percentBcGt75 = clamp((bcUtil - 50) * 2, 0, 100);

  // Account counts
  const totalAcc = Math.max(openAcc, round(openAcc + creditHistoryYears * 0.6 + riskScore * 2));
  const numSats = Math.min(totalAcc, round(totalAcc * (1 - riskScore * 0.15)));
  const numRevAccts = Math.max(1, round(totalAcc * 0.55));
  const numOpRevTl = Math.min(openAcc, numRevAccts);
  const numActvRevTl = Math.max(1, round(numOpRevTl * 0.8));
  const numActvBcTl = Math.max(0, round(numActvRevTl * 0.5));
  const numBcTl = Math.max(numActvBcTl, round(numRevAccts * 0.4));
  const numBcSats = Math.max(0, round(numBcTl * (1 - riskScore * 0.1)));
  const mortAcc = homeOwnership === "MORTGAGE" ? round(1 + (1 - riskScore) * 2) : 0;
  const numIlTl = Math.max(0, round(totalAcc - numRevAccts - mortAcc));
  const numRevTlBalGt0 = Math.max(0, round(numActvRevTl * 0.85));

  // Recent activity
  const numTlOpPast12m = round(1 + riskScore * 3);
  const accOpenPast24mths = round(numTlOpPast12m * 1.5);
  const moSinRcntTl = round(clamp(24 - riskScore * 20, 1, 60));
  const moSinRcntRevTlOp = moSinRcntTl + round(riskScore * 3);
  const moSinOldRevTlOp = Math.max(12, creditHistoryYears * 12 - moSinRcntRevTlOp);
  const moSinOldIlAcct = Math.max(12, round(creditHistoryYears * 12 * 0.8));

  // Balances
  const totalIlHighCreditLimit = round(annualInc * 0.15 * (1 - riskScore * 0.3));
  const totalBalExMort = round(revolBal + totalIlHighCreditLimit * 0.3);
  const totCurBal = round(totalBalExMort + (mortAcc > 0 ? annualInc * 1.5 : 0));
  const avgCurBal = round(totCurBal / Math.max(1, totalAcc));
  const totHiCredLim = round(totalRevHiLim + totalIlHighCreditLimit + (mortAcc > 0 ? annualInc * 2 : 0));

  // Derogatory / delinquency history
  const accNowDelinq = delinq2yrs >= 4 ? 1 : 0;
  const delinqAmnt = accNowDelinq ? round(200 + riskScore * 800) : 0;
  const numAcctsEver120Pd = delinq2yrs >= 2 ? 1 : 0;
  const numTl30dpd = delinq2yrs >= 1 && riskScore > 0.7 ? 1 : 0;
  const numTl90gDpd24m = delinq2yrs >= 3 ? 1 : 0;
  const pctTlNvrDlq = clamp(100 - riskScore * 35, 60, 100);
  const pubRec = riskScore > 0.75 ? 1 : 0;
  const taxLiens = riskScore > 0.9 ? 1 : 0;
  const totCollAmt = riskScore > 0.6 ? round(riskScore * 500) : 0;
  const collections12MthsExMed = riskScore > 0.7 ? 1 : 0;
  const chargeoffWithin12Mths = riskScore > 0.8 ? 1 : 0;

  const mthsSinceLastDelinq = delinq2yrs > 0 ? round(Math.max(1, 24 - delinq2yrs * 4)) : null;
  const mthsSinceLastRecord = pubRec ? round(30 + riskScore * 20) : null;
  const mthsSinceLastMajorDerog = riskScore > 0.75 ? round(20 - riskScore * 10) : null;
  const mthsSinceRecentBc = round(6 + (1 - riskScore) * 30);
  const mthsSinceRecentBcDlq = delinq2yrs > 0 && riskScore > 0.5 ? round(12 + riskScore * 20) : null;
  const mthsSinceRecentInq =
    inqLast6mths > 0 ? round(1 + Math.max(0, 6 - inqLast6mths)) : round(12 + (1 - riskScore) * 20);
  const mthsSinceRecentRevolDelinq = delinq2yrs > 0 && riskScore > 0.5 ? round(15 + riskScore * 25) : null;

  const verificationStatus: VerificationStatus =
    riskScore < 0.3 ? "Verified" : riskScore < 0.6 ? "Source Verified" : "Not Verified";

  return {
    loan_amnt: loanAmnt,
    installment,
    annual_inc: annualInc,
    dti,
    delinq_2yrs: delinq2yrs,
    inq_last_6mths: inqLast6mths,
    mths_since_last_delinq: mthsSinceLastDelinq,
    mths_since_last_record: mthsSinceLastRecord,
    open_acc: openAcc,
    pub_rec: pubRec,
    revol_bal: revolBal,
    revol_util: revolUtil,
    total_acc: totalAcc,
    collections_12_mths_ex_med: collections12MthsExMed,
    mths_since_last_major_derog: mthsSinceLastMajorDerog,
    acc_now_delinq: accNowDelinq,
    tot_coll_amt: totCollAmt,
    tot_cur_bal: totCurBal,
    total_rev_hi_lim: totalRevHiLim,
    acc_open_past_24mths: accOpenPast24mths,
    avg_cur_bal: avgCurBal,
    bc_open_to_buy: bcOpenToBuy,
    bc_util: round(bcUtil),
    chargeoff_within_12_mths: chargeoffWithin12Mths,
    delinq_amnt: delinqAmnt,
    mo_sin_old_il_acct: moSinOldIlAcct,
    mo_sin_old_rev_tl_op: moSinOldRevTlOp,
    mo_sin_rcnt_rev_tl_op: moSinRcntRevTlOp,
    mo_sin_rcnt_tl: moSinRcntTl,
    mort_acc: mortAcc,
    mths_since_recent_bc: mthsSinceRecentBc,
    mths_since_recent_bc_dlq: mthsSinceRecentBcDlq,
    mths_since_recent_inq: mthsSinceRecentInq,
    mths_since_recent_revol_delinq: mthsSinceRecentRevolDelinq,
    num_accts_ever_120_pd: numAcctsEver120Pd,
    num_actv_bc_tl: numActvBcTl,
    num_actv_rev_tl: numActvRevTl,
    num_bc_sats: numBcSats,
    num_bc_tl: numBcTl,
    num_il_tl: numIlTl,
    num_op_rev_tl: numOpRevTl,
    num_rev_accts: numRevAccts,
    num_rev_tl_bal_gt_0: numRevTlBalGt0,
    num_sats: numSats,
    num_tl_120dpd_2m: 0,
    num_tl_30dpd: numTl30dpd,
    num_tl_90g_dpd_24m: numTl90gDpd24m,
    num_tl_op_past_12m: numTlOpPast12m,
    pct_tl_nvr_dlq: round(pctTlNvrDlq),
    percent_bc_gt_75: round(percentBcGt75),
    pub_rec_bankruptcies: pubRec,
    tax_liens: taxLiens,
    tot_hi_cred_lim: totHiCredLim,
    total_bal_ex_mort: totalBalExMort,
    total_bc_limit: totalBcLimit,
    total_il_high_credit_limit: totalIlHighCreditLimit,
    earliest_cr_line: earliestCrLine,
    fico_range_low: ficoLow,
    fico_range_high: ficoHigh,
    term: termLiteral,
    emp_length: empLength,
    home_ownership: homeOwnership,
    verification_status: verificationStatus,
    purpose,
    addr_state: "CA",
    initial_list_status: "w",
  };
}

/** Rough FICO-bucketed APR, since the schema has no int_rate input to derive installment from. */
function estimateApr(ficoLow: number): number {
  if (ficoLow >= 760) return 7.5;
  if (ficoLow >= 720) return 9.5;
  if (ficoLow >= 680) return 12;
  if (ficoLow >= 640) return 16;
  if (ficoLow >= 600) return 21;
  return 26;
}

function amortizedPayment(principal: number, aprPercent: number, months: number): number {
  const monthlyRate = aprPercent / 100 / 12;
  const factor = Math.pow(1 + monthlyRate, months);
  const payment = (principal * monthlyRate * factor) / (factor - 1);
  return Math.round(payment * 100) / 100;
}

function yearsAgoIso(years: number): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - years);
  return d.toISOString().slice(0, 10);
}

function round(value: number): number {
  return Math.round(value);
}
