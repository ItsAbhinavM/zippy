import { create } from "zustand";
import type { FinancialState, Plan } from "../types/state";

export function emptyArray<T>(): T[] {
  return _EMPTY as T[];
}
const _EMPTY: unknown[] = [];

export interface Transcript {
  role: "user" | "assistant";
  text: string;
  id: number;
}

interface FinancialStore {
  state: FinancialState | null;
  plan: Plan | null;
  connected: boolean;
  transcript: Transcript | null;

  applySnapshot: (state: FinancialState) => void;
  applyDiff: (diff: Partial<FinancialState> & { plan?: Plan }) => void;
  applyTranscript: (role: "user" | "assistant", text: string) => void;
  setConnected: (connected: boolean) => void;
  reset: () => void;
}

export const useFinancialStore = create<FinancialStore>((set) => ({
  state: null,
  plan: null,
  connected: false,
  transcript: null,

  applySnapshot: (state) => set({ state, plan: null }),

  applyDiff: (diff) =>
    set((prev) => {
      if (!prev.state) return prev;
      const { plan, ...stateFields } = diff;
      const next: Partial<FinancialStore> = { state: { ...prev.state, ...stateFields } };
      if (plan !== undefined) next.plan = plan;
      return next as FinancialStore;
    }),

  applyTranscript: (role, text) =>
    set({ transcript: { role, text, id: Date.now() } }),

  setConnected: (connected) => set({ connected }),

  reset: () => set({ state: null, plan: null, connected: false, transcript: null }),
}));