import React from "react";
import { Progress } from "antd";

interface StepNavigationProps {
  currentStep: number;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  currentStep,
}) => {
  const steps = ["Thời gian", "Tùy chọn cá nhân", "Chỉnh sửa kế hoạch"];

  const progressPercentage = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="p-4">
      <div className="w-1/2 mx-auto">
        <Progress
          percent={progressPercentage}
          showInfo={false}
          strokeColor="#000000"
          strokeWidth={5}
        />
      </div>
    </div>
  );
};
