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
  Spin,
  Alert,
} from "antd";
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  CalendarOutlined,
  MoreOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import {
  TRAVEL_PLAN_TABS,
  ACTION_MENU_ITEMS,
  formatDate,
} from "../../constants/travelPlanConstants";
import { TravelDetail } from "./travelDetail";
import { useTravelPlans } from "../../hooks/useTravelPlans";

const { Title, Text, Paragraph } = Typography;

export const TravelPlanListTab: React.FC = () => {
  const { travelPlans, loading, error, refetch } = useTravelPlans();
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
    if (status === "planning") {
      return <Tag color="blue">Đang lên kế hoạch</Tag>;
    } else if (status === "completed") {
      return <Tag color="green">Đã hoàn thành</Tag>;
    } else {
      return <Tag color="orange">Đang diễn ra</Tag>;
    }
  };

  function renderTravelPlanItem(item: any) {
    const actionMenu = <Menu items={ACTION_MENU_ITEMS} />;
    const startDate = item.start_date ? new Date(item.start_date) : new Date();
    const endDate = item.end_date ? new Date(item.end_date) : new Date();
    const tripDuration = Math.round(
      (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    );

    return (
      <List.Item>
        <Card hoverable className="w-full mb-4">
          <div className="flex flex-col md:flex-row">
            <div className="md:w-1/4 h-48 md:h-auto overflow-hidden rounded-lg">
              <img
                src="https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg"
                alt={item.trip_name || item.destination_id}
                className="w-full h-full object-cover"
              />
            </div>

            <div className="md:w-3/4 md:pl-4 pt-3 md:pt-0 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <Title level={4} className="mb-1">
                      {item.trip_name || `Trip to ${item.destination_id}`}
                    </Title>
                    <div className="flex items-center text-gray-600 mb-3">
                      <CalendarOutlined className="mr-2" />
                      <Text>
                        {formatDate(startDate)} - {formatDate(endDate)}
                      </Text>
                      {item.destination_id && (
                        <>
                          <Text className="mx-2">•</Text>
                          <EnvironmentOutlined className="mr-1" />
                          <Text>{item.destination_id}</Text>
                        </>
                      )}
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

                {item.plan_by_day && item.plan_by_day.length > 0 && (
                  <Paragraph className="mb-2 text-gray-600">
                    <EnvironmentOutlined className="mr-2" />
                    Hoạt động: {item.plan_by_day.reduce((acc: string[], day: any) => {
                      day.segments.forEach((segment: any) => {
                        segment.activities.forEach((activity: any) => {
                          if (activity.name && !acc.includes(activity.name)) {
                            acc.push(activity.name);
                          }
                        });
                      });
                      return acc;
                    }, []).slice(0, 3).join(", ")}
                    {item.plan_by_day.reduce((acc: string[], day: any) => {
                      day.segments.forEach((segment: any) => {
                        segment.activities.forEach((activity: any) => {
                          if (activity.name && !acc.includes(activity.name)) {
                            acc.push(activity.name);
                          }
                        });
                      });
                      return acc;
                    }, []).length > 3 ? '...' : ''}
                  </Paragraph>
                )}
              </div>

              <div className="flex justify-between items-center mt-4">
                <div className="flex">
                  <ClockCircleOutlined className="mr-2 text-gray-500" />
                  <Text type="secondary">
                    {tripDuration} ngày
                  </Text>
                </div>

                <div className="space-x-2">
                  <Button
                    type="primary"
                    className="!bg-black"
                    onClick={() => handleViewDetails(item.trip_id)}
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

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 flex justify-center">
        <Spin size="large" tip="Đang tải..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          action={
            <Button onClick={() => refetch()} icon={<ReloadOutlined />}>
              Thử lại
            </Button>
          }
        />
      </div>
    );
  }

  // Filter travel plans by status
  const upcomingTrips = travelPlans.filter(
    (trip) => trip.status === "planning"
  );
  const ongoingTrips = travelPlans.filter(
    (trip) => trip.status === "ongoing"
  );
  const completedTrips = travelPlans.filter(
    (trip) => trip.status === "completed"
  );

  const renderTripList = (trips: any[]) => {
    if (trips.length === 0) {
      return <Empty description="Không có chuyến đi nào" />;
    }
    return (
      <List
        dataSource={trips}
        renderItem={renderTravelPlanItem}
        pagination={trips.length > 5 ? { pageSize: 5 } : false}
      />
    );
  };

  const tabItems = [
    {
      key: "upcoming",
      label: "Sắp tới",
      children: renderTripList(upcomingTrips)
    },
    {
      key: "ongoing",
      label: "Đang diễn ra",
      children: renderTripList(ongoingTrips)
    },
    {
      key: "completed",
      label: "Đã hoàn thành",
      children: renderTripList(completedTrips)
    },
    {
      key: "all",
      label: "Tất cả",
      children: renderTripList(travelPlans)
    }
  ];

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
