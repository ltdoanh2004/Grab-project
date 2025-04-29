import React, { useState, useEffect } from "react";
import { Spin, Typography, Card, Row, Col, List, Button } from "antd";
import {
  LoadingOutlined,
  CheckOutlined,
  SyncOutlined,
} from "@ant-design/icons";

const { Title, Text, Paragraph } = Typography;

interface LoadingStepProps {
  destination: string;
  onFinish?: () => void;
}

export const LoadingStep: React.FC<LoadingStepProps> = ({
  destination,
  onFinish,
}) => {
  // State to track progress of loading steps
  const [currentStepIndex, setCurrentStepIndex] = useState(2);
  // Track which steps have been processed
  const [completedSteps, setCompletedSteps] = useState<number[]>([0, 1]);

  const travelTips = [
    "Đừng quên sạc đầy các thiết bị điện tử trước khi khởi hành",
    "Mang theo một phích nước để giữ nước uống luôn mát lạnh",
    "Mang theo một bộ đồ dự phòng trong hành lý xách tay",
    "Chụp ảnh hộ chiếu và giấy tờ quan trọng, lưu trữ trực tuyến",
    "Tải xuống bản đồ ngoại tuyến của điểm đến của bạn",
  ];

  const loadingSteps = [
    { text: "Tìm kiếm địa điểm phù hợp", complete: true },
    { text: "Thiết lập lịch trình", complete: true },
    { text: "Tìm kiếm khách sạn phù hợp", complete: false },
    { text: "Tìm kiếm nhà hàng đặc sắc", complete: false },
    { text: "Hoàn thiện lịch trình", complete: false },
  ];

  // Simulate progressing through steps without ever finishing
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prevIndex) => {
        // Mark current step as completed
        if (!completedSteps.includes(prevIndex)) {
          setCompletedSteps((prev) => [...prev, prevIndex]);
        }

        // Cycle through steps 2-4 to create illusion of progress without completion
        if (prevIndex >= 4) return 2;
        return prevIndex + 1;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [completedSteps]);

  return (
    <div className="p-8 font-inter">
      <div className="flex flex-col items-center justify-center mb-8">
        <Spin
          indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
          className="mb-6"
        />
        <Title level={3}>
          Đang tạo lịch trình du lịch của bạn tại {destination}...
        </Title>
        <Text type="secondary" className="text-center max-w-lg">
          Chúng tôi đang tạo một trải nghiệm du lịch cá nhân hóa dựa trên những
          sở thích của bạn. Quá trình này có thể mất vài phút.
        </Text>
      </div>

      <Row gutter={24} className="mb-8">
        <Col span={12}>
          <Card title="Tiến trình" className="h-full">
            <List
              itemLayout="horizontal"
              dataSource={loadingSteps}
              renderItem={(item, index) => (
                <List.Item>
                  <div className="flex items-center">
                    {completedSteps.includes(index) &&
                    index !== currentStepIndex ? (
                      <div className="w-6 h-6 rounded-full flex items-center justify-center mr-3 bg-green-500">
                        <CheckOutlined className="text-white" />
                      </div>
                    ) : index === currentStepIndex ? (
                      <div className="w-6 h-6 rounded-full flex items-center justify-center mr-3 bg-blue-500">
                        <SyncOutlined spin className="text-white" />
                      </div>
                    ) : (
                      <div className="w-6 h-6 rounded-full flex items-center justify-center mr-3 bg-gray-200">
                        <span className="text-xs text-gray-500">
                          {index + 1}
                        </span>
                      </div>
                    )}

                    <span
                      className={
                        completedSteps.includes(index) &&
                        index !== currentStepIndex
                          ? "text-green-500"
                          : index === currentStepIndex
                          ? "text-blue-500 font-medium"
                          : ""
                      }
                    >
                      {item.text}
                    </span>

                    {index === currentStepIndex && (
                      <Spin size="small" className="ml-2" />
                    )}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Gợi ý hữu ích cho chuyến đi" className="h-full">
            <List
              itemLayout="horizontal"
              dataSource={travelTips}
              renderItem={(item) => (
                <List.Item>
                  <Text>• {item}</Text>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
