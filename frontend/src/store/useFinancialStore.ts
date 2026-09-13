import { create } from "zustand";
import type { FinancialState, Plan } from "../types/state";

const _EMPTY: unknown[] = [];
export function emptyArray<T>(): T[] {
  return _EMPTY as T[];
}
interface FinancialStore {
  state: FinancialState | null;
  plan: Plan | null;
  connected: boolean;

  applySnapshot: (state: FinancialState) => void;
  applyDiff: (diff: Partial<FinancialState> & { plan?: Plan }) => void;
  setConnected: (connected: boolean) => void;
  reset: () => void;
}

export const useFinancialStore = create<FinancialStore>((set) => ({
  state: null,
  plan: null,
  connected: false,

  applySnapshot: (state) => set({ state, plan: null }),

  applyDiff: (diff) =>
    set((prev) => {
      if (!prev.state) return prev;
      const { plan, ...stateFields } = diff;
      const next: Partial<FinancialStore> = {
        state: { ...prev.state, ...stateFields },
      };
      if (plan !== undefined) next.plan = plan;
      return next as FinancialStore;
    }),

  setConnected: (connected) => set({ connected }),

  reset: () => set({ state: null, plan: null, connected: false }),
}));