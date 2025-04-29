import React from "react";
import { Typography, Button } from "antd";
import { Budget, NumOfPeople } from "../../types/travelPlan";
import { PeopleSelection } from "./travelBasic/People";
import { BudgetSelection } from "./travelBasic/Budget";

const { Title, Text } = Typography;

interface PeopleBudgetStepProps {
  budget: Budget;
  onBudgetChange: (budget: Budget) => void;
  people: NumOfPeople;
  onPeopleChange: (people: NumOfPeople) => void;
  onNext?: () => void;
  onPrev?: () => void;
}

export const PeopleBudgetStep: React.FC<PeopleBudgetStepProps> = ({
  budget,
  onBudgetChange,
  people,
  onPeopleChange,
  onNext,
  onPrev,
}) => {
  return (
    <div className="p-8 font-inter">
      <div className="flex flex-col gap-4 text-center mb-6">
        <Title level={3}>Thông tin chuyến đi</Title>
        <Text type="secondary">
          Chọn số lượng người và ngân sách cho chuyến đi
        </Text>
      </div>

      <PeopleSelection people={people} onPeopleChange={onPeopleChange} />

      <BudgetSelection budget={budget} onBudgetChange={onBudgetChange} />

      <div className="flex justify-between mt-4">
        <Button className="!rounded-full" onClick={onPrev}>
          Quay lại
        </Button>
        <Button
          type="primary"
          className="!bg-black !rounded-full"
          onClick={onNext}
        >
          Tiếp tục
        </Button>
      </div>
    </div>
  );
};
