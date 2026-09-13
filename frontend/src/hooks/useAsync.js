import { useCallback, useEffect, useState } from 'react';

const IDLE = { status: 'idle', data: null, error: null };

/**
 * Runs `load` whenever `deps` change and tracks its state. Pass `null` instead of a
 * function to skip loading. Responses from stale requests are ignored.
 */
export function useAsync(load, deps) {
  const [state, setState] = useState(load ? { ...IDLE, status: 'loading' } : IDLE);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!load) {
      setState(IDLE);
      return undefined;
    }

    let cancelled = false;
    setState({ status: 'loading', data: null, error: null });
    load().then(
      (data) => !cancelled && setState({ status: 'success', data, error: null }),
      (error) => !cancelled && setState({ status: 'error', data: null, error }),
    );
    return () => {
      cancelled = true;
    };
  }, [...deps, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  return { ...state, retry };
}
