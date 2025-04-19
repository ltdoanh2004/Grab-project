import React from "react";
import { Card, Typography, Input, Rate } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { DESTINATIONS } from "../../constants/travelPlanConstants";

const { Title, Text } = Typography;

interface DestinationStepProps {
  selectedDestination: string | null;
  onSelectDestination: (destId: string) => void;
  onStartPlan: () => void;
}

export const DestinationStep: React.FC<DestinationStepProps> = ({
  selectedDestination,
  onSelectDestination,
  onStartPlan,
}) => {
  const handleCardClick = (destId: string) => {
    onSelectDestination(destId);
    onStartPlan();
  };

  return (
    <div className="p-8 font-inter">
      <div className="mb-6 text-center">
        <Title level={2} className="mb-4 font-black">
          Trước tiên, bạn muốn đi đâu?
        </Title>
        <Text className="text-gray-600 mb-4">
          Bạn sẽ nhận được các gợi ý cá nhân hóa mà bạn có thể lưu lại và biến
          thành lịch trình du lịch của riêng bạn.
        </Text>
      </div>
      <div className="justify-center flex mb-16">
        <Input
          placeholder="Chọn điểm đến"
          className="w-full max-w-xl mx-auto"
          size="large"
          prefix={<SearchOutlined />}
        />
      </div>
      <div className="flex justify-center flex-col mb-16">
        <p className="text-center font-semibold text-xl mb-4">
          Khám phá địa điểm phổ biến
        </p>
        <div className="grid lg:grid-cols-2 gap-6">
          {DESTINATIONS.map((dest) => (
            <Card
              key={dest.id}
              hoverable
              className={`cursor-pointer ${
                selectedDestination === dest.id
                  ? "border-2 border-blue-500"
                  : ""
              }`}
              onClick={() => handleCardClick(dest.id)}
            >
              <div className="flex items-center">
                <img
                  src={dest.imageUrl}
                  alt={dest.name}
                  className="w-16 h-16 mr-4"
                />
                <div className="flex-1">
                  <div className="flex justify-between items-center">
                    <Title level={4} className="mb-0">
                      {dest.name}
                    </Title>
                    <div className="flex items-center">
                      <Rate defaultValue={dest.rating} disabled allowHalf />
                      <span className="ml-2 text-gray-500">{dest.rating}</span>
                    </div>
                  </div>
                  <Text className="text-gray-600">{dest.description}</Text>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
      <div className="flex justify-center flex-col">
        <p className="text-center font-semibold text-xl mb-4">
          Quay lại với những địa điểm đã chọn
        </p>
        <div className="flex flex-row justify-center gap-4">
          {DESTINATIONS.map((dest) => (
            <Card
              key={dest.id}
              hoverable
              className={`cursor-pointer ${
                selectedDestination === dest.id
                  ? "border-2 border-blue-500"
                  : ""
              }`}
              onClick={() => handleCardClick(dest.id)}
            >
              <div className="flex flex-col">
                <img
                  src={dest.imageUrl}
                  alt={dest.name}
                  className="w-fit h-fit"
                />
                <div className="flex-1 mt-2">
                  <p className="mb-0">{dest.name}</p>
                  <Rate defaultValue={dest.rating} disabled allowHalf />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
