import React, { useState, useEffect, useRef } from "react";
import { Spin, Typography, Card, Row, Col, List, Button, message } from "antd";
import {
  LoadingOutlined,
  CheckOutlined,
  SyncOutlined,
} from "@ant-design/icons";
import { getAllSuggestions } from "../../services/travelPlanApi";
import { useNavigate } from "react-router-dom";

const { Title, Text, Paragraph } = Typography;

interface LoadingStepProps {
  destination: string;
  onFinish?: () => void;
}

export const LoadingStep: React.FC<LoadingStepProps> = ({
  destination,
  onFinish,
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(2);
  const [completedSteps, setCompletedSteps] = useState<number[]>([0, 1]);
  const [apiLoadingComplete, setApiLoadingComplete] = useState(false);
  const navigate = useNavigate();
  const apiRequestInitiated = useRef(false);

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

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (apiRequestInitiated.current) return;
      apiRequestInitiated.current = true;
      
      try {
        const suggestionsData = await getAllSuggestions();
        console.log(suggestionsData);
        console.log("API response:", suggestionsData.data);
        
        if (!suggestionsData.data.plan_by_day || suggestionsData.data.plan_by_day.length === 0) {
          message.error("Không nhận được dữ liệu lịch trình");
          return;
        }
        
        const tripId = suggestionsData.data.trip_id || "trip123";
        
        localStorage.setItem(
          `tripPlan_${tripId}`,
          JSON.stringify(suggestionsData.data)
        );
        
        setApiLoadingComplete(true);
        navigate(`/trips/${tripId}`);
      } catch (error) {
        console.error("Failed to fetch data:", error);
        if (
          typeof error === "object" &&
          error !== null &&
          "response" in error
        ) {
          const err = error as { response?: { data?: any } };
          console.error("Error response:", err.response?.data);
          message.error(
            `Lỗi: ${err.response?.data?.message || "Không thể tải dữ liệu"}`
          );
        } else {
          message.error("Không thể tải dữ liệu. Vui lòng thử lại sau.");
        }
      }
    };

    fetchSuggestions();
  }, [navigate]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prevIndex) => {
        if (!completedSteps.includes(prevIndex)) {
          setCompletedSteps((prev) => [...prev, prevIndex]);
        }

        if (prevIndex >= 4) return 2;
        return prevIndex + 1;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [completedSteps]);

  useEffect(() => {
    if (apiLoadingComplete && onFinish) {
      const timer = setTimeout(() => {
        onFinish();
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [apiLoadingComplete, onFinish]);

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
