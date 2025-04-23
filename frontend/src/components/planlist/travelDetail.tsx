import React, { useState } from "react";
import { Button, Card, Tabs, Tag } from "antd";
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  StarOutlined,
  ArrowLeftOutlined,
} from "@ant-design/icons";
import {
  MOCK_TRAVEL_DETAIL,
  formatDate,
} from "../../constants/travelPlanConstants";
import { TravelActivity, TravelDetailData } from "../../types/travelPlan";
import { ActivityModal } from "./travelDetail/ActivityDetail";
import { TravelHeader } from "./travelDetail/Header";
import { TravelItinerary } from "./travelDetail/Plans";

interface TravelDetailProps {
  travelId: string;
  onBack: () => void;
}

const ACTIVITY_TYPE_COLORS: Record<TravelActivity["type"], string> = {
  attraction: "blue",
  restaurant: "green",
  hotel: "red",
  transport: "default",
};

const ACTIVITY_TYPE_TEXT: Record<TravelActivity["type"], string> = {
  attraction: "Tham quan",
  restaurant: "Nhà hàng",
  hotel: "Khách sạn",
  transport: "Di chuyển",
};

export const TravelDetail: React.FC<TravelDetailProps> = ({
  travelId,
  onBack,
}) => {
  const travelDetail: TravelDetailData = MOCK_TRAVEL_DETAIL;
  const [activeTab, setActiveTab] = useState<string>("itinerary");
  const [activityModalVisible, setActivityModalVisible] = useState(false);
  const [selectedActivity, setSelectedActivity] =
    useState<TravelActivity | null>(null);

  const showActivityDetail = (activity: TravelActivity) => {
    setSelectedActivity(activity);
    setActivityModalVisible(true);
  };

  const getActivityIcon = (type: TravelActivity["type"]) => {
    switch (type) {
      case "attraction":
        return <StarOutlined className="text-yellow-500" />;
      case "restaurant":
        return <DollarOutlined className="text-red-500" />;
      case "hotel":
        return <TeamOutlined className="text-blue-500" />;
      case "transport":
        return <ClockCircleOutlined className="text-green-500" />;
      default:
        return <EnvironmentOutlined />;
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const calculateDurationDays = (start: Date, end: Date): number => {
    return Math.round(
      (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
    );
  };

  const getStatusTag = (status: TravelDetailData["status"]) => {
    let color = "";
    let text = "";

    switch (status) {
      case "planning":
      case "confirmed":
        color = "orange";
        text = "Đang diễn ra";
        break;
      case "completed":
        color = "green";
        text = "Đã hoàn thành";
        break;
      case "canceled":
        color = "red";
        text = "Đã hủy";
        break;
      default:
        color = "default";
        text = "Không xác định";
    }

    return (
      <Tag color={color} className="text-sm py-1 px-3">
        {text}
      </Tag>
    );
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={onBack}
        className="mb-4"
        type="text"
      >
        Quay lại danh sách kế hoạch
      </Button>

      <TravelHeader
        travelDetail={travelDetail}
        formatDate={formatDate}
        calculateDurationDays={calculateDurationDays}
        formatCurrency={formatCurrency}
        getStatusTag={getStatusTag}
      />

      <Card className="shadow-sm">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          className="travel-detail-tabs"
          items={[
            {
              key: "itinerary",
              label: "Lịch trình",
              children: (
                <TravelItinerary
                  days={travelDetail.days}
                  formatDate={formatDate}
                  getActivityIcon={getActivityIcon}
                  activityTypeColors={ACTIVITY_TYPE_COLORS}
                  onActivityClick={showActivityDetail}
                />
              ),
            },
            {
              key: "budget",
              label: "Tổng quát và xuất lịch",
            },
          ]}
        />
      </Card>

      <ActivityModal
        activity={selectedActivity}
        visible={activityModalVisible}
        onClose={() => setActivityModalVisible(false)}
        activityTypeText={ACTIVITY_TYPE_TEXT}
      />
    </div>
  );
};
