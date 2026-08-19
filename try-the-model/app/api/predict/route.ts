import { NextResponse } from "next/server";

// Server-side proxy to the real credit_risk /predict API. Keeping this on the
// server (rather than calling the API directly from the browser) sidesteps CORS
// — the real API has none configured, and we treat it as an external contract
// we don't modify — and keeps PREDICT_API_URL out of client-side code.
const PREDICT_API_URL = process.env.PREDICT_API_URL ?? "http://127.0.0.1:8000/predict";

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(PREDICT_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
  } catch (err) {
    return NextResponse.json(
      { detail: `Could not reach the prediction API: ${err instanceof Error ? err.message : String(err)}` },
      { status: 502 },
    );
  }

  const payload = await upstream.json().catch(() => null);
  return NextResponse.json(payload, { status: upstream.status });
}
