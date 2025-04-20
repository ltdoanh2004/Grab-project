import React, { useState } from "react";
import { Typography, Card, Radio, InputNumber, Switch } from "antd";
import { Budget } from "../../../types/travelPlan";
import { DollarOutlined } from "@ant-design/icons";
import { BUDGET_RANGES } from "../../../constants/travelPlanConstants";

const { Title, Text } = Typography;

interface BudgetSelectionProps {
  budget: Budget;
  onBudgetChange: (budget: Budget) => void;
}

export const BudgetSelection: React.FC<BudgetSelectionProps> = ({
  budget,
  onBudgetChange,
}) => {
  const [showRanges, setShowRanges] = useState(!budget.exactBudget);
  const [exactBudget, setExactBudget] = useState(budget.exactBudget || 5000000);

  const findBudgetType = (
    amount: number
  ): "$" | "$$" | "$$$" | "$$$$" | "$$$$$" => {
    const entry = Object.entries(BUDGET_RANGES).find(
      ([_, range]) => amount >= range.min && amount < range.max
    );
    return (entry?.[0] as "$" | "$$" | "$$$" | "$$$$" | "$$$$$") || "$$";
  };

  const handleExactBudget = (value: number | null) => {
    const newValue = value || 0;
    setExactBudget(newValue);
    const type = findBudgetType(newValue);

    onBudgetChange({
      type,
      exactBudget: newValue,
    });
  };

  const handleBudgetType = (type: "$" | "$$" | "$$$" | "$$$$" | "$$$$$") => {
    const range = BUDGET_RANGES[type];
    const midValue = Math.min(
      range.min + (range.max - range.min) / 2,
      100000000
    );
    setExactBudget(midValue);

    onBudgetChange({
      type,
      exactBudget: midValue,
    });
  };

  const toggleBudgetMode = (checked: boolean) => {
    setShowRanges(checked);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Card className="mb-6 shadow-sm rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <Title level={4} className="m-0">
          Ngân sách cho chuyến đi
        </Title>
        <div className="flex items-center">
          <Text className="mr-2 text-gray-500">Chọn theo mức</Text>
          <Switch
            checked={showRanges}
            onChange={toggleBudgetMode}
            className={showRanges ? "bg-black" : ""}
          />
        </div>
      </div>

      {!showRanges ? (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <Text className="text-lg font-medium flex items-center">
              <DollarOutlined className="mr-2" />
              Ngân sách cụ thể
            </Text>
            <div className="bg-gray-100 px-4 py-1.5 rounded-full">
              <Text strong className="text-lg">
                {formatCurrency(exactBudget)}
              </Text>
            </div>
          </div>

          <div className="flex justify-between mt-6">
            <InputNumber
              min={1000000}
              value={exactBudget}
              onChange={handleExactBudget}
              className="w-full"
              addonBefore="VND"
            />
          </div>

          {budget.type && (
            <div className="flex items-center mt-4 bg-gray-50 p-3 rounded-md">
              <div
                className={`text-xl mr-2 ${
                  budget.type === "$"
                    ? "text-green-500"
                    : budget.type === "$$"
                    ? "text-blue-500"
                    : budget.type === "$$$"
                    ? "text-yellow-500"
                    : budget.type === "$$$$"
                    ? "text-purple-500"
                    : "text-red-500"
                }`}
              >
                {budget.type}
              </div>
              <Text className="text-gray-600">
                Mức ngân sách của bạn thuộc loại{" "}
                <strong>{BUDGET_RANGES[budget.type].description}</strong>
              </Text>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center">
          <Radio.Group
            value={budget.type}
            onChange={(e) => handleBudgetType(e.target.value)}
            optionType="button"
            buttonStyle="solid"
            size="large"
            className="flex justify-between"
          >
            {(["$", "$$", "$$$", "$$$$", "$$$$$"] as const).map((type) => (
              <Radio.Button
                key={type}
                value={type}
                className={`flex-1 text-center ${
                  budget.type === type
                    ? "!bg-black !text-white !border-black"
                    : ""
                }`}
              >
                {type}
              </Radio.Button>
            ))}
          </Radio.Group>
        </div>
      )}
    </Card>
  );
};
