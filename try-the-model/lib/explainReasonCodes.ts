/**
 * Translates raw SHAP reason codes (feature name -> SHAP value, positive = pushes
 * toward "will default") into plain-language sentences for a non-technical visitor.
 */

export interface ExplainedReason {
  feature: string;
  label: string;
  direction: "up" | "down";
  magnitude: "slightly" | "moderately" | "strongly";
  sentence: string;
}

interface FeatureInfo {
  label: string;
  /** Sentence used when this feature pushed the prediction toward higher risk. */
  up: string;
  /** Sentence used when this feature pushed the prediction toward lower risk. */
  down: string;
}

const FEATURE_INFO: Record<string, FeatureInfo> = {
  dti: {
    label: "Debt-to-income ratio",
    up: "A relatively high debt-to-income ratio increased the estimated risk.",
    down: "A relatively low debt-to-income ratio helped lower the estimated risk.",
  },
  fico_range_low: {
    label: "Credit score (FICO)",
    up: "A lower credit score increased the estimated risk.",
    down: "A higher credit score helped lower the estimated risk.",
  },
  fico_range_high: {
    label: "Credit score (FICO)",
    up: "A lower credit score increased the estimated risk.",
    down: "A higher credit score helped lower the estimated risk.",
  },
  // The model doesn't see fico_range_low/high or earliest_cr_line directly — it derives
  // fico_mid and credit_age_yrs from them, and those are what actually show up in SHAP output.
  fico_mid: {
    label: "Credit score (FICO)",
    up: "A lower credit score increased the estimated risk.",
    down: "A higher credit score helped lower the estimated risk.",
  },
  credit_age_yrs: {
    label: "Length of credit history",
    up: "A shorter credit history increased the estimated risk.",
    down: "A longer credit history helped lower the estimated risk.",
  },
  revol_util: {
    label: "Credit utilization",
    up: "High revolving credit utilization increased the estimated risk.",
    down: "Low revolving credit utilization helped lower the estimated risk.",
  },
  bc_util: {
    label: "Credit card utilization",
    up: "High credit card utilization increased the estimated risk.",
    down: "Low credit card utilization helped lower the estimated risk.",
  },
  annual_inc: {
    label: "Annual income",
    up: "A lower annual income increased the estimated risk.",
    down: "A higher annual income helped lower the estimated risk.",
  },
  loan_amnt: {
    label: "Loan amount",
    up: "The size of the loan requested increased the estimated risk.",
    down: "The size of the loan requested helped lower the estimated risk.",
  },
  installment: {
    label: "Monthly payment",
    up: "A relatively large monthly payment increased the estimated risk.",
    down: "A relatively small monthly payment helped lower the estimated risk.",
  },
  delinq_2yrs: {
    label: "Recent delinquencies",
    up: "A history of recent missed payments increased the estimated risk.",
    down: "No recent missed payments helped lower the estimated risk.",
  },
  inq_last_6mths: {
    label: "Recent credit inquiries",
    up: "A number of recent credit inquiries increased the estimated risk.",
    down: "Few recent credit inquiries helped lower the estimated risk.",
  },
  open_acc: {
    label: "Open credit accounts",
    up: "The number of open credit accounts increased the estimated risk.",
    down: "The number of open credit accounts helped lower the estimated risk.",
  },
  total_acc: {
    label: "Total credit accounts",
    up: "The total number of credit accounts on file increased the estimated risk.",
    down: "The total number of credit accounts on file helped lower the estimated risk.",
  },
  mort_acc: {
    label: "Mortgage accounts",
    up: "Having no mortgage accounts increased the estimated risk.",
    down: "Having an established mortgage helped lower the estimated risk.",
  },
  term: {
    label: "Loan term",
    up: "The longer repayment term increased the estimated risk.",
    down: "The shorter repayment term helped lower the estimated risk.",
  },
  emp_length: {
    label: "Employment history",
    up: "A shorter employment history increased the estimated risk.",
    down: "A longer employment history helped lower the estimated risk.",
  },
  home_ownership: {
    label: "Home ownership",
    up: "Renting rather than owning increased the estimated risk.",
    down: "Home ownership status helped lower the estimated risk.",
  },
  purpose: {
    label: "Loan purpose",
    up: "The stated purpose of the loan increased the estimated risk.",
    down: "The stated purpose of the loan helped lower the estimated risk.",
  },
  verification_status: {
    label: "Income verification",
    up: "Unverified income increased the estimated risk.",
    down: "Verified income helped lower the estimated risk.",
  },
  pub_rec: {
    label: "Public records",
    up: "A public record (bankruptcy, lien, or judgment) increased the estimated risk.",
    down: "A clean public record helped lower the estimated risk.",
  },
  pub_rec_bankruptcies: {
    label: "Bankruptcies on file",
    up: "A bankruptcy on file increased the estimated risk.",
    down: "No bankruptcies on file helped lower the estimated risk.",
  },
  tax_liens: {
    label: "Tax liens",
    up: "A tax lien on file increased the estimated risk.",
    down: "No tax liens on file helped lower the estimated risk.",
  },
  acc_now_delinq: {
    label: "Accounts currently delinquent",
    up: "Currently-delinquent accounts increased the estimated risk.",
    down: "Having no currently-delinquent accounts helped lower the estimated risk.",
  },
  num_accts_ever_120_pd: {
    label: "History of serious late payments",
    up: "A history of accounts 120+ days past due increased the estimated risk.",
    down: "No history of serious late payments helped lower the estimated risk.",
  },
  acc_open_past_24mths: {
    label: "Recently opened accounts",
    up: "A number of recently opened credit accounts increased the estimated risk.",
    down: "Few recently opened credit accounts helped lower the estimated risk.",
  },
  pct_tl_nvr_dlq: {
    label: "On-time payment history",
    up: "A lower share of accounts always paid on time increased the estimated risk.",
    down: "A high share of accounts always paid on time helped lower the estimated risk.",
  },
  mo_sin_old_rev_tl_op: {
    label: "Length of credit history",
    up: "A shorter credit history increased the estimated risk.",
    down: "A longer credit history helped lower the estimated risk.",
  },
  earliest_cr_line: {
    label: "Length of credit history",
    up: "A shorter credit history increased the estimated risk.",
    down: "A longer credit history helped lower the estimated risk.",
  },
  tot_cur_bal: {
    label: "Total balances across accounts",
    up: "High total balances across accounts increased the estimated risk.",
    down: "Manageable total balances across accounts helped lower the estimated risk.",
  },
  avg_cur_bal: {
    label: "Average account balance",
    up: "High average account balances increased the estimated risk.",
    down: "Modest average account balances helped lower the estimated risk.",
  },
  total_bal_ex_mort: {
    label: "Non-mortgage debt balance",
    up: "A high non-mortgage debt balance increased the estimated risk.",
    down: "A modest non-mortgage debt balance helped lower the estimated risk.",
  },
  percent_bc_gt_75: {
    label: "Maxed-out credit cards",
    up: "A high share of credit cards near their limit increased the estimated risk.",
    down: "Few credit cards near their limit helped lower the estimated risk.",
  },
};

/** SHAP reason codes come back keyed by the ColumnTransformer's output names
 *  (e.g. "num__dti", "cat__term") rather than the raw request field names. */
function stripPipelinePrefix(feature: string): string {
  return feature.replace(/^(num|cat)__/, "");
}

function humanizeLabel(feature: string): string {
  return stripPipelinePrefix(feature)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Sorts by |SHAP value| descending and returns plain-language explanations,
 * with magnitude ("slightly"/"moderately"/"strongly") relative to the
 * strongest factor in the set.
 */
export function explainReasonCodes(reasonCodes: Record<string, number>): ExplainedReason[] {
  const entries = Object.entries(reasonCodes).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  if (entries.length === 0) return [];

  const maxAbs = Math.abs(entries[0][1]) || 1;

  return entries.map(([feature, value]) => {
    const ratio = Math.abs(value) / maxAbs;
    const magnitude: ExplainedReason["magnitude"] =
      ratio > 0.66 ? "strongly" : ratio > 0.33 ? "moderately" : "slightly";
    const direction: ExplainedReason["direction"] = value > 0 ? "up" : "down";

    const info = FEATURE_INFO[stripPipelinePrefix(feature)];
    const label = info?.label ?? humanizeLabel(feature);
    const sentence =
      info?.[direction] ??
      `${label} ${direction === "up" ? "increased" : "decreased"} the estimated risk.`;

    return { feature, label, direction, magnitude, sentence };
  });
}
