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
      <div
        className="mb-16 relative rounded-2xl overflow-hidden
  bg-[url('/hinhnen.jpg')] bg-cover bg-center p-12 pb-24 shadow-lg before:content-[''] before:absolute before:inset-0
   before:bg-gradient-to-b before:from-black/50 before:via-black/30 before:to-black/20 after:content-[''] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-20 after:bg-gradient-to-t after:from-white after:to-transparent after:blur-sm"
      >
        <div className="relative z-10 text-center">
          <p className="mb-4 font-semibold text-white text-3xl">
            Trước tiên, bạn muốn đi đâu?
          </p>
          <p className="text-gray-200 font-extralight mb-8 text-sm">
            Bạn sẽ nhận được các gợi ý cá nhân hóa mà bạn có thể lưu lại và biến
            thành lịch trình du lịch của riêng bạn.
          </p>

          <div className="relative z-20 max-w-xl mx-auto transform translate-y-12">
            <Input
              placeholder="Chọn điểm đến"
              className="w-full shadow-lg rounded-full py-3"
              size="large"
              prefix={<SearchOutlined className="ml-2" />}
            />
          </div>
        </div>
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
