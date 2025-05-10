import React, { useState } from "react";
import { Typography, Button, Modal, Input, Form, message } from "antd";
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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customPreference, setCustomPreference] = useState("");
  const [customDescription, setCustomDescription] = useState("");
  const [form] = Form.useForm();

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

  const handleCreatePlan = () => {
    const userInput = {
      destination,
      budget,
      people,
      travelTime,
      personalOptions,
    };

    localStorage.setItem("planUserInput", JSON.stringify(userInput));

    if (onNext) onNext();
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCancel = () => {
    setCustomPreference("");
    setCustomDescription("");
    form.resetFields();
    setIsModalOpen(false);
  };

  const handleAddCustomPreference = () => {
    if (customPreference.trim()) {
      const newOption: PersonalOption = {
        type: "Extra" as any,
        name: customPreference.trim(),
        description: customDescription.trim() || "Sở thích tùy chỉnh",
      };
      onAddOption(newOption);
      setCustomPreference("");
      setCustomDescription("");
      form.resetFields();
      setIsModalOpen(false);
    }
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

        {personalOptions
          .filter((option) => (option.type as any) === "Extra")
          .map((option, index) => (
            <div
              key={`custom-${index}`}
              className="bg-green-500 text-black font-semibold rounded-full h-10 overflow-hidden cursor-pointer flex items-center justify-center px-4"
              onClick={() => onAddOption(option)}
            >
              <CheckOutlined className="mr-1" />
              <span>{option.name}</span>
            </div>
          ))}
      </div>

      <div
        className="overflow-hidden cursor-pointer flex items-center justify-center mb-8"
        onClick={handleOpenModal}
      >
        <div className="border border-gray-300 rounded-full h-10 overflow-hidden cursor-pointer flex items-center px-4">
          <PlusOutlined className="mr-1" />
          <p>Thêm sở thích</p>
        </div>
      </div>

      <Modal
        title="Thêm sở thích cá nhân"
        open={isModalOpen}
        onCancel={handleCancel}
        footer={[
          <Button key="cancel" onClick={handleCancel}>
            Hủy
          </Button>,
          <Button
            key="submit"
            type="primary"
            onClick={handleAddCustomPreference}
            disabled={!customPreference.trim()}
            className="bg-black"
          >
            Thêm
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Sở thích của bạn"
            name="customPreference"
            rules={[{ required: true, message: "Vui lòng nhập sở thích" }]}
          >
            <Input
              placeholder="Ví dụ: Leo núi, Chụp ảnh, Ngắm hoàng hôn..."
              value={customPreference}
              onChange={(e) => setCustomPreference(e.target.value)}
              autoFocus
            />
          </Form.Item>
          <Form.Item label="Mô tả chi tiết" name="customDescription">
            <Input.TextArea
              placeholder="Mô tả chi tiết về sở thích của bạn..."
              value={customDescription}
              onChange={(e) => setCustomDescription(e.target.value)}
              autoSize={{ minRows: 2, maxRows: 4 }}
            />
          </Form.Item>
        </Form>
      </Modal>

      <div className="flex justify-between">
        <Button className="!rounded-full" onClick={onPrev}>
          Quay lại
        </Button>
        <Button
          type="primary"
          className="!bg-black !rounded-full"
          onClick={handleCreatePlan}
        >
          Tạo lịch trình
        </Button>
      </div>
    </div>
  );
};
