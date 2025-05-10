import React from "react";
import { Typography } from "antd";
import { BalanceSummary } from "./BalanceSummary";
import { ExpenseList } from "./ExpenseList";
import { ParticipantList } from "./ParticipantList";
import { SettlementSuggestions } from "./SettlementSuggestions";
import { AddExpenseModal } from "./AddExpenseModal";
import { SplitBillProps } from "../../../../types/splitBillTypes";
import { useSplitBill } from "../../../../hooks/useSplitBill";

const { Title } = Typography;

export const SplitBill: React.FC<SplitBillProps> = ({ travelDetail }) => {
  const {
    expenses,
    participants,
    expenseCategories,
    modalVisible,
    balances,
    totalOwed,
    totalOwing,
    settlements,
    setModalVisible,
    addParticipant,
    removeParticipant,
    addExpense,
    removeExpense,
    getDisplayName,
  } = useSplitBill();

  return (
    <div className="p-4">
      <Title level={4}>Chia Chi Phí Cho: {travelDetail.trip_name}</Title>

      <BalanceSummary
        balances={balances}
        totalOwed={totalOwed}
        totalOwing={totalOwing}
        getDisplayName={getDisplayName}
      />

      <ParticipantList
        participants={participants}
        onAddParticipant={addParticipant}
        onRemoveParticipant={removeParticipant}
        getDisplayName={getDisplayName}
      />

      <ExpenseList
        expenses={expenses}
        onRemoveExpense={removeExpense}
        onAddExpense={() => setModalVisible(true)}
        getDisplayName={getDisplayName}
      />

      <SettlementSuggestions 
        settlements={settlements} 
        getDisplayName={getDisplayName}
      />

      <AddExpenseModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        onAddExpense={addExpense}
        participants={participants}
        expenseCategories={expenseCategories}
        getDisplayName={getDisplayName}
      />
    </div>
  );
}; 