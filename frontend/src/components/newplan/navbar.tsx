import React from "react";
import { Typography, Progress, Space } from "antd";

const { Title } = Typography;

interface StepNavigationProps {
  currentStep: number;
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  currentStep,
}) => {
  const steps = ["Thời gian", "Tùy chọn cá nhân", "Chỉnh sửa kế hoạch"];

  const progressPercentage = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="p-4 border-b">
      <div className="w-full px-2">
        <Progress
          percent={progressPercentage}
          showInfo={false}
          strokeColor={{
            "0%": "#108ee9",
            "100%": "#87d068",
          }}
          strokeWidth={10}
        />

        <div className="flex justify-between mt-1 text-xs text-gray-500">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`${
                currentStep >= index ? "text-blue-600 font-medium" : ""
              }`}
            >
              {index + 1}. {step}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
