import React from "react";
import { Button, Typography, Space } from "antd";
import { TravelTime } from "../../types/travelPlan";
import { ExactTimeComponent } from "./travelTime/exactTime";
import { FlexibleTimeComponent } from "./travelTime/flexibleTime";

const { Title } = Typography;

interface TimeStepProps {
  travelTime: TravelTime;
  onSwitchTimeType: (type: "exact" | "flexible") => void;
  onDateChange: (dates: any) => void;
  onMonthChange: (month: number) => void;
  onLengthChange: (days: number) => void;
  onNext: () => void;
  onPrev: () => void;
}

export const TimeStep: React.FC<TimeStepProps> = ({
  travelTime,
  onSwitchTimeType,
  onDateChange,
  onMonthChange,
  onLengthChange,
  onNext,
  onPrev,
}) => {
  const isNextDisabled =
    travelTime.type === "exact"
      ? !travelTime.startDate || !travelTime.endDate
      : !travelTime.month || !travelTime.length;

  const isExactTime = travelTime.type === "exact";

  return (
    <div className="p-8">
      <Title level={2} className="text-center mb-8">
        {isExactTime ? "Chọn ngày đi cụ thể" : "Lên kế hoạch linh hoạt"}
      </Title>

      <div className="flex justify-center mb-8 flex-col">
        {isExactTime ? (
          <ExactTimeComponent
            timeData={travelTime}
            onDateChange={onDateChange}
          />
        ) : (
          <FlexibleTimeComponent
            timeData={travelTime}
            onMonthChange={onMonthChange}
            onLengthChange={onLengthChange}
          />
        )}
        <div className="flex justify-center mt-8">
          <Button
            onClick={() => onSwitchTimeType(isExactTime ? "flexible" : "exact")}
          >
            {isExactTime
              ? "Tôi chưa biết lịch trình cụ thể"
              : "Chọn ngày chính xác"}
          </Button>
        </div>
      </div>

      <div className="mt-8 flex justify-between">
        <Space>
          <Button onClick={onPrev}>Quay lại</Button>
        </Space>
        <Button
          type="primary"
          disabled={isNextDisabled}
          onClick={onNext}
          className="px-8"
        >
          Tiếp tục
        </Button>
      </div>
    </div>
  );
};
