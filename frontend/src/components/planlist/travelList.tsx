import React, { useState } from "react";
import {
  Typography,
  Card,
  Tabs,
  List,
  Tag,
  Button,
  Empty,
  Dropdown,
  Menu,
} from "antd";
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  CalendarOutlined,
  MoreOutlined,
} from "@ant-design/icons";
import {
  MOCK_TRAVEL_PLANS,
  TRAVEL_PLAN_TABS,
  ACTION_MENU_ITEMS,
  formatDate,
} from "../../constants/travelPlanConstants";
import { TravelDetail } from "./travelDetail";

const { Title, Text, Paragraph } = Typography;

export const TravelPlanListTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("upcoming");
  const [selectedTravelId, setSelectedTravelId] = useState<string | null>(null);

  const handleViewDetails = (travelId: string) => {
    setSelectedTravelId(travelId);
  };

  if (selectedTravelId) {
    return (
      <TravelDetail
        travelId={selectedTravelId}
        onBack={() => setSelectedTravelId(null)}
      />
    );
  }

  const getStatusTag = (status: string) => {
    if (status === "upcoming") {
      return <Tag color="blue">Sắp tới</Tag>;
    } else if (status === "completed") {
      return <Tag color="green">Đã hoàn thành</Tag>;
    } else {
      return <Tag color="orange">Đang diễn ra</Tag>;
    }
  };

  function renderTravelPlanItem(item: (typeof MOCK_TRAVEL_PLANS)[0]) {
    const actionMenu = <Menu items={ACTION_MENU_ITEMS} />;

    return (
      <List.Item>
        <Card hoverable className="w-full mb-4">
          <div className="flex flex-col md:flex-row">
            <div className="md:w-1/4 h-48 md:h-auto overflow-hidden rounded-lg">
              <img
                src={item.imageUrl}
                alt={`${item.destination}`}
                className="w-full h-full object-cover"
              />
            </div>

            <div className="md:w-3/4 md:pl-4 pt-3 md:pt-0 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <Title level={4} className="mb-1">
                      {item.destination}
                    </Title>
                    <div className="flex items-center text-gray-600 mb-3">
                      <CalendarOutlined className="mr-2" />
                      <Text>
                        {formatDate(item.startDate)} -{" "}
                        {formatDate(item.endDate)}
                      </Text>
                      <Text className="mx-2">•</Text>
                      <TeamOutlined className="mr-1" />
                      <Text>
                        {item.adults +
                          (item.children > 0
                            ? ` + ${item.children} trẻ em`
                            : "")}
                      </Text>
                      <Text className="mx-2">•</Text>
                      <DollarOutlined className="mr-1" />
                      <Text>{item.budgetType}</Text>
                    </div>
                  </div>
                  <div className="flex">
                    {getStatusTag(item.status)}
                    <Dropdown
                      menu={{ items: ACTION_MENU_ITEMS }}
                      trigger={["click"]}
                    >
                      <Button
                        type="text"
                        icon={<MoreOutlined />}
                        className="ml-2"
                      />
                    </Dropdown>
                  </div>
                </div>

                <Paragraph className="mb-2 text-gray-600">
                  <EnvironmentOutlined className="mr-2" />
                  Hoạt động: {item.activities.join(", ")}
                </Paragraph>
              </div>

              <div className="flex justify-between items-center mt-4">
                <div className="flex">
                  <ClockCircleOutlined className="mr-2 text-gray-500" />
                  <Text type="secondary">
                    {Math.round(
                      (item.endDate.getTime() - item.startDate.getTime()) /
                        (1000 * 60 * 60 * 24)
                    )}{" "}
                    ngày
                  </Text>
                </div>

                <div className="space-x-2">
                  <Button
                    type="primary"
                    className="!bg-black"
                    onClick={() => handleViewDetails(item.id)}
                  >
                    Chi tiết
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </List.Item>
    );
  }

  const tabItems = TRAVEL_PLAN_TABS(renderTravelPlanItem, MOCK_TRAVEL_PLANS);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <Title level={3} className="mb-0">
          Kế hoạch du lịch của bạn
        </Title>
        <Button type="primary" className="!bg-black !rounded-full">
          + Tạo kế hoạch mới
        </Button>
      </div>

      <Card className="shadow-sm">
        <Tabs
          defaultActiveKey="upcoming"
          items={tabItems}
          onChange={setActiveTab}
          className="travel-plan-tabs"
        />
      </Card>
    </div>
  );
};
