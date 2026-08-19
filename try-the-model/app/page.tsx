"use client";

import { useState } from "react";
import { LoanForm } from "@/components/LoanForm";
import { PresetPicker } from "@/components/PresetPicker";
import { ResultPanel } from "@/components/ResultPanel";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { buildPayload } from "@/lib/buildPayload";
import { PRESETS } from "@/lib/presets";
import type { CuratedInputs, ResponseModel } from "@/lib/types";

export default function HomePage() {
  const [inputs, setInputs] = useState<CuratedInputs>(PRESETS[0].inputs);
  const [activePresetId, setActivePresetId] = useState<string | null>(PRESETS[0].id);
  const [response, setResponse] = useState<ResponseModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleChange(patch: Partial<CuratedInputs>) {
    setInputs((prev) => ({ ...prev, ...patch }));
    setActivePresetId(null);
  }

  function handlePresetSelect(presetId: string) {
    const preset = PRESETS.find((p) => p.id === presetId);
    if (!preset) return;
    setInputs(preset.inputs);
    setActivePresetId(preset.id);
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload(inputs)),
      });
      const body = await res.json();
      if (!res.ok) {
        throw new Error(body?.detail ? String(body.detail) : `Request failed (${res.status})`);
      }
      setResponse(body as ResponseModel);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error while contacting the prediction API.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2 text-center">
        <h1 className="text-2xl font-semibold text-text-primary">Try the credit risk model</h1>
        <p className="mx-auto max-w-xl text-sm text-text-secondary">
          This calls the real, deployed prediction model — not a mockup. Fill out a simplified loan application below
          and get a live default-risk prediction.
        </p>
      </header>

      <PresetPicker activeId={activePresetId} onSelect={handlePresetSelect} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader
            title="Loan application"
            subtitle="The model considers 65 factors from an applicant's credit history; these ~13 are the ones that most strongly influence the prediction. Everything else is filled in with realistic defaults behind the scenes."
          />
          <CardBody>
            <LoanForm inputs={inputs} onChange={handleChange} onSubmit={handleSubmit} loading={loading} />
          </CardBody>
        </Card>

        <Card className="lg:col-span-2 lg:self-start">
          <CardHeader title="Prediction" subtitle="From the live model, not a mockup" />
          <CardBody>
            <ResultPanel response={response} loading={loading} error={error} />
          </CardBody>
        </Card>
      </div>

      <p className="text-center text-xs text-text-muted">
        Inputs beyond the fields above are populated with realistic, internally-consistent defaults derived from what
        you enter. Nothing you submit here is stored against a real identity.
      </p>
    </main>
  );
}
