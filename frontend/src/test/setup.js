import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';
import { mockFetch } from '../api/mock/mockFetch.js';

// Tests don't need a running backend: fetch is served by the in-memory mock.
beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(mockFetch));
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
