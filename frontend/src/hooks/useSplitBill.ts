import { useState } from "react";
import { Expense, Settlement } from "../types/splitBillTypes";

// Define constant for current user ID
export const CURRENT_USER_ID = "user1";

export const useSplitBill = () => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [participants, setParticipants] = useState<string[]>([
    CURRENT_USER_ID,
    "friend1",
    "friend2",
  ]);
  const [modalVisible, setModalVisible] = useState(false);

  const expenseCategories = [
    "Ăn uống",
    "Di chuyển",
    "Chỗ ở",
    "Hoạt động",
    "Mua sắm",
    "Khác",
  ];

  const addParticipant = (name: string) => {
    if (name && !participants.includes(name)) {
      setParticipants([...participants, name]);
    }
  };

  const removeParticipant = (name: string) => {
    // Don't allow removing the current user
    if (name === CURRENT_USER_ID) return;
    
    setParticipants(participants.filter((p) => p !== name));
    // Also update expenses that involve this participant
    setExpenses(
      expenses.map((expense) => ({
        ...expense,
        paidBy: expense.paidBy === name ? CURRENT_USER_ID : expense.paidBy,
        splitAmong: expense.splitAmong.filter((p) => p !== name),
      }))
    );
  };

  const addExpense = (expenseData: Omit<Expense, "id">) => {
    const newExpense: Expense = {
      id: Date.now().toString(),
      ...expenseData,
    };
    setExpenses([...expenses, newExpense]);
  };

  const removeExpense = (id: string) => {
    setExpenses(expenses.filter((expense) => expense.id !== id));
  };

  // Calculation utilities
  const calculateBalances = (): Record<string, number> => {
    const balances: Record<string, number> = {};

    // Initialize all participants with zero balance
    participants.forEach((p: string) => {
      balances[p] = 0;
    });

    // Calculate what each person paid and owes
    expenses.forEach((expense) => {
      const paidBy = expense.paidBy;
      const splitAmong = expense.splitAmong;
      const amount = expense.amount;
      
      if (expense.customSplitData) {
        // Handle custom split amounts
        for (const [personId, customAmount] of Object.entries(expense.customSplitData)) {
          if (customAmount > 0 && splitAmong.includes(personId)) {
            if (personId === paidBy) {
              // If the payer is also in the split, they've already covered their portion
              // No need to adjust their balance for their own share
            } else {
              // The payer gets a credit for what others owe
              balances[paidBy] += customAmount;
              
              // Others owe their custom share to the payer
              balances[personId] -= customAmount;
            }
          }
        }
      } else {
        // Calculate individual share for equal split
        const perPersonAmount = Math.round(amount / splitAmong.length);
        
        // For each person who's part of the split
        splitAmong.forEach((person: string) => {
          if (person === paidBy) {
            // If the payer is also in the split, they've already covered their portion
            // No need to adjust their balance for their own share
          } else {
            // The payer gets a credit for what others owe
            balances[paidBy] += perPersonAmount;
            
            // Others owe their share to the payer
            balances[person] -= perPersonAmount;
          }
        });
      }
    });

    // Round all balances to whole numbers (no decimal places for VND)
    Object.keys(balances).forEach((key) => {
      balances[key] = Math.round(balances[key]);
    });

    return balances;
  };

  const calculateTotalOwed = (balances: Record<string, number>): number => {
    // Calculate only what others owe to the current user
    return balances[CURRENT_USER_ID] > 0 ? balances[CURRENT_USER_ID] : 0;
  };

  const calculateTotalOwing = (balances: Record<string, number>): number => {
    // Calculate only what the current user owes to others
    return balances[CURRENT_USER_ID] < 0 ? Math.abs(balances[CURRENT_USER_ID]) : 0;
  };

  const calculateSettlements = (balances: Record<string, number>): Settlement[] => {
    const settlements: Settlement[] = [];
    const debtors = Object.entries(balances)
      .filter(([_, amount]) => amount < 0)
      .sort((a, b) => a[1] - b[1]); // Sort debtors by amount (most negative first)

    const creditors = Object.entries(balances)
      .filter(([_, amount]) => amount > 0)
      .sort((a, b) => b[1] - a[1]); // Sort creditors by amount (most positive first)

    let i = 0;
    let j = 0;

    while (i < debtors.length && j < creditors.length) {
      const [debtor, debtAmount] = debtors[i];
      const [creditor, creditAmount] = creditors[j];

      const absDebt = Math.abs(debtAmount);
      const settleAmount = Math.min(absDebt, creditAmount);

      settlements.push({
        from: debtor,
        to: creditor,
        amount: Math.round(settleAmount),
      });

      debtors[i] = [debtor, debtAmount + settleAmount];
      creditors[j] = [creditor, creditAmount - settleAmount];

      if (absDebt <= creditAmount + 0.01) {
        // Using a small epsilon for floating-point comparison
        i++;
      }

      if (creditAmount <= absDebt + 0.01) {
        j++;
      }
    }

    return settlements;
  };

  // Get display names for participants
  const getDisplayName = (participantId: string): string => {
    if (participantId === CURRENT_USER_ID) {
      return "Bạn";
    }
    return participantId;
  };

  // Calculate current balances
  const balances = calculateBalances();
  const totalOwed = calculateTotalOwed(balances);
  const totalOwing = calculateTotalOwing(balances);
  const settlements = calculateSettlements(balances);

  return {
    // State
    expenses,
    participants,
    expenseCategories,
    modalVisible,
    balances,
    totalOwed,
    totalOwing,
    settlements,
    
    // Actions
    setModalVisible,
    addParticipant,
    removeParticipant,
    addExpense,
    removeExpense,
    
    // Utilities
    getDisplayName,
    currentUserId: CURRENT_USER_ID,
  };
}; 