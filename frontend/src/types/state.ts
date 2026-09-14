export type Confidence = "confirmed" | "estimated" | "uncertain";
export type Phase = "gathering" | "clarifying" | "planning" | "reviewing";

export interface IncomeItem {
  id: string;
  label: string;
  amount: number | null;
  day_of_month: number | null;
  confidence: Confidence;
}

export interface PaymentItem {
  id: string;
  label: string;
  type: "loan_emi" | "credit_card_min" | "credit_card_full";
  amount: number | null;
  due_day: number | null;
  is_essential: boolean;
  confidence: Confidence;
}

export interface ExpenseItem {
  id: string;
  label: string;
  amount: number | null;
  category: "essential" | "optional";
  day_of_month: number | null;
  confidence: Confidence;
}

export interface Conflict {
  id: string;
  field_ref: string;
  entity_type: "income" | "payment" | "expense";
  values_seen: number[];
  resolved: boolean;
}

export interface MissingField {
  id: string;
  description: string;
  why_it_matters: string;
}

export interface FinancialState {
  session_id: string;
  today: string;
  income: IncomeItem[];
  essential_expenses: ExpenseItem[];
  optional_expenses: ExpenseItem[];
  payments: PaymentItem[];
  conflicts: Conflict[];
  missing_fields: MissingField[];
  starting_balance: number | null;
  phase: Phase;
}

export interface SuggestedCut {
  expense_id: string;
  label: string;
  original_amount: number;
  cut_amount: number;
}

export interface Assumption {
  description: string;
}

export interface DayBalance {
  date: string;
  balance: number;
  events: string[];
}

export interface ActionStep {
  day: string;
  order: number;
  kind: "income" | "essential_payment" | "debt_payment" | "optional_expense" | "optional_cut";
  label: string;
  amount: number;
  original_amount: number | null;
  running_balance_after: number;
  instruction: string;
}

export interface Plan {
  total_income: number;
  total_essential: number;
  total_optional: number;
  net_position: number;
  monthly_headroom: number;
  balance_curve: DayBalance[];
  shortfall_days: string[];
  is_solvable: boolean;
  suggested_cuts: SuggestedCut[];
  adjusted_balance_curve: DayBalance[] | null;
  action_plan: ActionStep[];
  assumptions: Assumption[];
}