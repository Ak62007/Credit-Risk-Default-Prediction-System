import { FileQuestion } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ProbabilityGauge } from "@/components/ProbabilityGauge";
import { ReasonCodeList } from "@/components/ReasonCodeList";
import { explainReasonCodes } from "@/lib/explainReasonCodes";
import type { ResponseModel } from "@/lib/types";

export function ResultPanel({
  response,
  loading,
  error,
}: {
  response: ResponseModel | null;
  loading: boolean;
  error: string | null;
}) {
  if (error) {
    return (
      <div className="flex flex-col items-center gap-3 py-12 text-center">
        <p className="text-sm font-medium text-[var(--status-critical)]">Something went wrong</p>
        <p className="max-w-sm text-sm text-text-muted">{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-series-1" />
        <p className="text-sm text-text-muted">Running the real model…</p>
      </div>
    );
  }

  if (!response) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <FileQuestion className="h-8 w-8 text-text-muted" strokeWidth={1.5} />
        <p className="max-w-xs text-sm text-text-muted">
          Fill out the application on the left and click &ldquo;Get a prediction&rdquo; to see a live result from the
          deployed model.
        </p>
      </div>
    );
  }

  const willDefault = response.pred === 1;
  const reasons = explainReasonCodes(response.reason_codes);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-4 text-center">
        <Badge tone={willDefault ? "critical" : "good"} className="text-sm">
          {willDefault ? "Predicted: likely to default" : "Predicted: likely to repay"}
        </Badge>
        <ProbabilityGauge probability={response.prob} />
      </div>

      <div>
        <h4 className="mb-1 text-sm font-semibold text-text-primary">What drove this prediction</h4>
        <p className="mb-3 text-xs text-text-muted">
          The 5 factors that most influenced this specific prediction, in plain language.
        </p>
        <ReasonCodeList reasons={reasons} />
      </div>
    </div>
  );
}
