import type { CuratedInputs } from "./types";

export interface Preset {
  id: string;
  label: string;
  blurb: string;
  inputs: CuratedInputs;
}

export const PRESETS: Preset[] = [
  {
    id: "typical",
    label: "Typical applicant",
    blurb: "An average-looking borrower — moderate income, some revolving debt, a clean-ish history.",
    inputs: {
      loanAmnt: 15000,
      term: "36",
      purpose: "debt_consolidation",
      annualInc: 65000,
      empLength: "5 years",
      homeOwnership: "RENT",
      dti: 18,
      ficoLow: 690,
      revolUtil: 45,
      creditHistoryYears: 10,
      delinq2yrs: 0,
      inqLast6mths: 1,
      openAcc: 9,
    },
  },
  {
    id: "low-risk",
    label: "Low-risk applicant",
    blurb: "High income, low utilization, strong credit score, long track record — the model should like this one.",
    inputs: {
      loanAmnt: 12000,
      term: "36",
      purpose: "credit_card",
      annualInc: 120000,
      empLength: "10+ years",
      homeOwnership: "MORTGAGE",
      dti: 9,
      ficoLow: 780,
      revolUtil: 12,
      creditHistoryYears: 22,
      delinq2yrs: 0,
      inqLast6mths: 0,
      openAcc: 11,
    },
  },
  {
    id: "high-risk",
    label: "High-risk applicant",
    blurb: "Thin credit history, high utilization, recent delinquencies, a large loan relative to income.",
    inputs: {
      loanAmnt: 30000,
      term: "60",
      purpose: "small_business",
      annualInc: 38000,
      empLength: "< 1 year",
      homeOwnership: "RENT",
      dti: 34,
      ficoLow: 645,
      revolUtil: 88,
      creditHistoryYears: 3,
      delinq2yrs: 3,
      inqLast6mths: 6,
      openAcc: 5,
    },
  },
];
