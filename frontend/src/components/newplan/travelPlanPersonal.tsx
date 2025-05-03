import React from "react";
import { Typography, Button } from "antd";
import { PERSONAL_OPTIONS } from "../../constants/travelPlanConstants";
import { PersonalOption } from "../../types/travelPlan";
import { CheckOutlined, PlusOutlined } from "@ant-design/icons";

const { Text, Title } = Typography;

interface PersonalStepProps {
  personalOptions?: PersonalOption[];
  onAddOption: (option: PersonalOption) => void;
  onNext?: () => void;
  onPrev?: () => void;
  destination?: string;
  budget?: any;
  people?: any;
  travelTime?: any;
}

export const PersonalStep: React.FC<PersonalStepProps> = ({
  personalOptions = [],
  onAddOption,
  onNext,
  onPrev,
  destination,
  budget,
  people,
  travelTime,
}) => {
  const isOptionSelected = (option: PersonalOption) => {
    return personalOptions?.some(
      (item) => item.type === option.type && item.name === option.name
    );
  };

  const allOptions = [
    ...PERSONAL_OPTIONS.places,
    ...PERSONAL_OPTIONS.activities,
    ...PERSONAL_OPTIONS.food,
    ...PERSONAL_OPTIONS.transportation,
    ...PERSONAL_OPTIONS.accommodation,
  ];

  const handleCreateItinerary = () => {
    const userInput = {
      destination,
      budget,
      people,
      travelTime,
      personalOptions,
    };

    console.log("userInput:", JSON.stringify(userInput, null, 2));

    if (onNext) onNext();
  };

  return (
    <div className="p-8 font-inter">
      <div className="font-inter flex flex-col gap-4 text-center mb-8">
        <Title level={3}>Tùy chọn cá nhân</Title>
        <Text type="secondary">
          Chọn tất cả các mục phù hợp với sở thích của bạn
        </Text>
      </div>

      <div className="font-light text-sm grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mb-8">
        {allOptions.map((option, index) => (
          <div
            key={index}
            className={`rounded-full h-10 overflow-hidden cursor-pointer flex items-center justify-center px-4 ${
              isOptionSelected(option)
                ? "bg-green-500 text-black font-semibold"
                : "border border-gray-300"
            }`}
            onClick={() => onAddOption(option)}
          >
            {isOptionSelected(option) && <CheckOutlined className="mr-1" />}
            <span>{option.name}</span>
          </div>
        ))}
      </div>
      <div className="overflow-hidden cursor-pointer flex items-center justify-center">
        <div className="border border-gray-300 rounded-full h-10 overflow-hidden cursor-pointer flex items-center px-4">
          <PlusOutlined className="mr-1" />
          <p>Thêm sở thích</p>
        </div>
      </div>

      <div className="flex justify-between">
        <Button className="!rounded-full" onClick={onPrev}>
          Quay lại
        </Button>
        <Button
          type="primary"
          className="!bg-black !rounded-full"
          onClick={handleCreateItinerary}
        >
          Tạo lịch trình
        </Button>
      </div>
    </div>
  );
};
