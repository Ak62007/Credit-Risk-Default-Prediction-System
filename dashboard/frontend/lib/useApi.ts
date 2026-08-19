"use client";

/* eslint-disable react-hooks/set-state-in-effect --
   Deliberate imperative fetch-lifecycle hook: resetting loading/error at the
   start of a fetch effect is the standard data-fetching pattern (what
   react-query/SWR do internally), not a render-derivable value. */

import { useEffect, useRef, useState, useCallback } from "react";

interface UseApiState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
  reload: () => void;
}

/**
 * Small fetch-on-mount/deps-change hook -- deliberately not a general cache
 * (no request de-dup across components, no revalidation), which is fine for
 * this dashboard's scale. `deps` drives refetching the same way a useEffect
 * dependency array would.
 */
export function useApi<T>(loader: () => Promise<T>, deps: unknown[] = []): UseApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);

  const loaderRef = useRef(loader);
  useEffect(() => {
    loaderRef.current = loader;
  });

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    loaderRef
      .current()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- deps is caller-supplied
  }, [tick, ...deps]);

  const reload = useCallback(() => setTick((t) => t + 1), []);

  return { data, error, loading, reload };
}
