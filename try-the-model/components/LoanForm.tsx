import type { CuratedInputs, EmpLength, HomeOwnership, Purpose } from "@/lib/types";
import { Field } from "@/components/ui/Field";
import { Slider } from "@/components/ui/Slider";
import { Select } from "@/components/ui/Select";

const PURPOSE_OPTIONS: { value: Purpose; label: string }[] = [
  { value: "debt_consolidation", label: "Debt consolidation" },
  { value: "credit_card", label: "Credit card refinancing" },
  { value: "home_improvement", label: "Home improvement" },
  { value: "major_purchase", label: "Major purchase" },
  { value: "small_business", label: "Small business" },
  { value: "car", label: "Car" },
  { value: "medical", label: "Medical expenses" },
  { value: "moving", label: "Moving" },
  { value: "vacation", label: "Vacation" },
  { value: "house", label: "House" },
  { value: "wedding", label: "Wedding" },
  { value: "renewable_energy", label: "Renewable energy" },
  { value: "educational", label: "Education" },
  { value: "other", label: "Other" },
];

const EMP_LENGTH_OPTIONS: EmpLength[] = [
  "< 1 year",
  "1 year",
  "2 years",
  "3 years",
  "4 years",
  "5 years",
  "6 years",
  "7 years",
  "8 years",
  "9 years",
  "10+ years",
];

const HOME_OWNERSHIP_OPTIONS: { value: HomeOwnership; label: string }[] = [
  { value: "RENT", label: "Rent" },
  { value: "MORTGAGE", label: "Mortgage" },
  { value: "OWN", label: "Own outright" },
  { value: "OTHER", label: "Other" },
];

const currency = (n: number) => `$${n.toLocaleString()}`;

export function LoanForm({
  inputs,
  onChange,
  onSubmit,
  loading,
}: {
  inputs: CuratedInputs;
  onChange: (patch: Partial<CuratedInputs>) => void;
  onSubmit: () => void;
  loading: boolean;
}) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      className="flex flex-col gap-8"
    >
      <section className="flex flex-col gap-5">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-text-muted">Loan details</h3>

        <Field label="Loan amount" value={currency(inputs.loanAmnt)}>
          <Slider
            min={1000}
            max={40000}
            step={500}
            value={inputs.loanAmnt}
            onChange={(v) => onChange({ loanAmnt: v })}
          />
        </Field>

        <Field label="Loan term">
          <div className="flex gap-2">
            {(["36", "60"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => onChange({ term: t })}
                className={
                  "flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors " +
                  (inputs.term === t
                    ? "border-series-1 bg-[color-mix(in_oklab,var(--series-1)_10%,transparent)] text-series-1"
                    : "border-border bg-surface-1 text-text-secondary hover:bg-surface-3")
                }
              >
                {t} months
              </button>
            ))}
          </div>
        </Field>

        <Field label="Loan purpose">
          <Select value={inputs.purpose} onChange={(e) => onChange({ purpose: e.target.value as Purpose })}>
            {PURPOSE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </Field>
      </section>

      <section className="flex flex-col gap-5">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-text-muted">Income &amp; employment</h3>

        <Field label="Annual income" value={currency(inputs.annualInc)}>
          <Slider
            min={15000}
            max={300000}
            step={1000}
            value={inputs.annualInc}
            onChange={(v) => onChange({ annualInc: v })}
          />
        </Field>

        <Field label="Employment length">
          <Select
            value={inputs.empLength}
            onChange={(e) => onChange({ empLength: e.target.value as EmpLength })}
          >
            {EMP_LENGTH_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Home ownership">
          <Select
            value={inputs.homeOwnership}
            onChange={(e) => onChange({ homeOwnership: e.target.value as HomeOwnership })}
          >
            {HOME_OWNERSHIP_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </Field>
      </section>

      <section className="flex flex-col gap-5">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-text-muted">Credit profile</h3>

        <Field label="Debt-to-income ratio" value={`${inputs.dti}%`}>
          <Slider min={0} max={40} step={0.5} value={inputs.dti} onChange={(v) => onChange({ dti: v })} />
        </Field>

        <Field label="FICO score" value={`${inputs.ficoLow}–${inputs.ficoLow + 4}`}>
          <Slider
            min={600}
            max={845}
            step={5}
            value={inputs.ficoLow}
            onChange={(v) => onChange({ ficoLow: v })}
          />
        </Field>

        <Field label="Revolving credit utilization" value={`${inputs.revolUtil}%`}>
          <Slider min={0} max={100} step={1} value={inputs.revolUtil} onChange={(v) => onChange({ revolUtil: v })} />
        </Field>

        <Field label="Years of credit history" value={`${inputs.creditHistoryYears} yrs`}>
          <Slider
            min={1}
            max={40}
            step={1}
            value={inputs.creditHistoryYears}
            onChange={(v) => onChange({ creditHistoryYears: v })}
          />
        </Field>

        <Field label="Open credit accounts" value={inputs.openAcc}>
          <Slider min={1} max={30} step={1} value={inputs.openAcc} onChange={(v) => onChange({ openAcc: v })} />
        </Field>

        <Field label="Delinquencies in last 2 years" value={inputs.delinq2yrs}>
          <Slider
            min={0}
            max={5}
            step={1}
            value={inputs.delinq2yrs}
            onChange={(v) => onChange({ delinq2yrs: v })}
          />
        </Field>

        <Field label="Credit inquiries in last 6 months" value={inputs.inqLast6mths}>
          <Slider
            min={0}
            max={10}
            step={1}
            value={inputs.inqLast6mths}
            onChange={(v) => onChange({ inqLast6mths: v })}
          />
        </Field>
      </section>

      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-series-1 px-4 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Scoring application…" : "Get a prediction"}
      </button>
    </form>
  );
}
