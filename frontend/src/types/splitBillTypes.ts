import { TravelDetailData } from "./travelPlan";

export interface Expense {
  id: string;
  description: string;
  amount: number;
  paidBy: string;
  splitAmong: string[];
  category: string;
  date: string;
  customSplitData?: Record<string, number>;
}

export interface Settlement {
  from: string;
  to: string;
  amount: number;
}

export interface SplitBillProps {
  travelDetail: TravelDetailData;
}

export interface ParticipantListProps {
  participants: string[];
  onAddParticipant: (name: string) => void;
  onRemoveParticipant: (name: string) => void;
  getDisplayName: (id: string) => string;
}

export interface ExpenseListProps {
  expenses: Expense[];
  onRemoveExpense: (id: string) => void;
  onAddExpense: () => void;
  getDisplayName: (id: string) => string;
}

export interface BalanceSummaryProps {
  balances: Record<string, number>;
  totalOwed: number;
  totalOwing: number;
}

export interface AddExpenseModalProps {
  visible: boolean;
  onClose: () => void;
  onAddExpense: (expense: Omit<Expense, "id">) => void;
  participants: string[];
  expenseCategories: string[];
  getDisplayName: (id: string) => string;
}

export interface SettlementSuggestionsProps {
  settlements: Settlement[];
  getDisplayName: (id: string) => string;
} 