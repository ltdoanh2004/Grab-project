import React from "react";
import { Card, Radio, Typography, InputNumber } from "antd";
import { FlexibleTime } from "../../../types/travelPlan";
import { CheckOutlined } from "@ant-design/icons";

const { Text } = Typography;

interface FlexibleTimeComponentProps {
  timeData: FlexibleTime;
  onMonthChange: (month: number) => void;
  onLengthChange: (days: number) => void;
}

export const FlexibleTimeComponent: React.FC<FlexibleTimeComponentProps> = ({
  timeData,
  onMonthChange,
  onLengthChange,
}) => {
  const months = [
    "Tháng 1",
    "Tháng 2",
    "Tháng 3",
    "Tháng 4",
    "Tháng 5",
    "Tháng 6",
    "Tháng 7",
    "Tháng 8",
    "Tháng 9",
    "Tháng 10",
    "Tháng 11",
    "Tháng 12",
  ];

  return (
    <Card>
      <div className="flex flex-col gap-4 text-center">
        <Radio.Group
          onChange={(e) => onMonthChange(e.target.value)}
          value={timeData.month || 0}
          optionType="button"
          buttonStyle="solid"
          className="mx-auto"
        >
          <div className="grid grid-cols-4 gap-2">
            {months.map((month, index) => (
              <Radio.Button
                key={index}
                value={index + 1}
                className={`text-center !rounded-full !h-10 overflow-hidden ${
                  timeData.month === index + 1
                    ? "!bg-green-500 !text-black !font-semibold"
                    : ""
                }`}
                style={{
                  border: "1px solid #d9d9d9",
                  borderRadius: "9999px",
                }}
              >
                {timeData.month === index + 1 && <CheckOutlined className="" />}{" "}
                {month}
              </Radio.Button>
            ))}
          </div>
        </Radio.Group>
      </div>
      <div className="flex flex-row mt-8 justify-between items-center font-inter">
        <Text className="text-sm text-gray-500 mr-2">
          Bạn dự tính đi bao nhiêu ngày?
        </Text>
        <div className="flex items-center text-white">
          <button
            className="px-2 py-2 border rounded-full bg-black cursor-pointer hover:bg-gray-200 hover:text-black"
            onClick={() => {
              const newValue = Math.max(1, (timeData.length || 1) - 1);
              onLengthChange(newValue);
            }}
          >
            -
          </button>
          <InputNumber
            min={1}
            max={30}
            value={timeData.length || 1}
            onChange={(value) => onLengthChange(value ?? 1)}
            disabled={true}
            className="!w-12 !rounded-full !m-2 !border-0 !bg-gray-100 !text-center !text-black"
          />
          <button
            className="px-2 py-2 border rounded-full bg-black cursor-pointer hover:bg-gray-200 hover:text-black"
            onClick={() => {
              const newValue = Math.min(30, (timeData.length || 1) + 1);
              onLengthChange(newValue);
            }}
          >
            +
          </button>
        </div>
      </div>
    </Card>
  );
};
