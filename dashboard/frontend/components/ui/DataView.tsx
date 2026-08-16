"use client";

import type { ReactNode } from "react";
import { Spinner, ErrorState } from "./Spinner";

export function DataView<T>({
  data,
  loading,
  error,
  render,
}: {
  data: T | null;
  loading: boolean;
  error: Error | null;
  render: (data: T) => ReactNode;
}) {
  if (loading && !data) return <Spinner />;
  if (error) return <ErrorState message={error.message} />;
  if (!data) return null;
  return <>{render(data)}</>;
}
