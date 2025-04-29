import React, { useState } from "react";
import { Button, Card, Tabs, Modal, Input } from "antd";
import {
  ArrowLeftOutlined,
  EditOutlined,
  SaveOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import {
  MOCK_TRAVEL_DETAIL,
  formatDate,
  ACTIVITY_TYPE_COLORS,
  ACTIVITY_TYPE_TEXT,
  getActivityIcon,
  formatCurrency,
  calculateDurationDays,
  getStatusTag,
} from "../../constants/travelPlanConstants";
import {
  TravelActivity,
  TravelDetailData,
  TravelDay,
} from "../../types/travelPlan";
import { ActivityModal } from "./travelDetail/ActivityDetail";
import { TravelHeader } from "./travelDetail/Header";
import { TravelItinerary } from "./travelDetail/Plans";
import { AIActivitySuggestions } from "./travelDetail/AISuggestions";

const { Search } = Input;

interface TravelDetailProps {
  travelId: string;
  onBack: () => void;
}

export const TravelDetail: React.FC<TravelDetailProps> = ({
  travelId,
  onBack,
}) => {
  const [travelDetail, setTravelDetail] =
    useState<TravelDetailData>(MOCK_TRAVEL_DETAIL);
  const [activeTab, setActiveTab] = useState<string>("itinerary");
  const [activityModalVisible, setActivityModalVisible] = useState(false);
  const [selectedActivity, setSelectedActivity] =
    useState<TravelActivity | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [currentDay, setCurrentDay] = useState<TravelDay | null>(null);
  const [activityToReplace, setActivityToReplace] =
    useState<TravelActivity | null>(null);
  const [activitySearchModalVisible, setActivitySearchModalVisible] =
    useState(false);
  const [dayForNewActivity, setDayForNewActivity] = useState<TravelDay | null>(
    null
  );

  const showActivityDetail = (activity: TravelActivity) => {
    setSelectedActivity(activity);
    setActivityModalVisible(true);
  };

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode);
    setShowAISuggestions(false);
    setActivitySearchModalVisible(false);
  };

  const handleReplaceActivity = (day: TravelDay, activity: TravelActivity) => {
    setCurrentDay(day);
    setActivityToReplace(activity);
    setShowAISuggestions(true);
  };

  const handleSelectAISuggestion = (newActivity: TravelActivity) => {
    if (currentDay && activityToReplace) {
      const updatedTravelDetail = { ...travelDetail };

      const dayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === currentDay.day
      );

      if (dayIndex !== -1) {
        const activityIndex = updatedTravelDetail.days[
          dayIndex
        ].activities.findIndex((a) => a.id === activityToReplace.id);

        if (activityIndex !== -1) {
          updatedTravelDetail.days[dayIndex].activities[activityIndex] = {
            ...newActivity,
            id: activityToReplace.id,
            time: activityToReplace.time,
          };

          setTravelDetail(updatedTravelDetail);
        }
      }

      setShowAISuggestions(false);
    }
  };

  const handleDeleteActivity = (day: TravelDay, activity: TravelActivity) => {
    const updatedTravelDetail = { ...travelDetail };

    const dayIndex = updatedTravelDetail.days.findIndex(
      (d) => d.day === day.day
    );

    if (dayIndex !== -1) {
      updatedTravelDetail.days[dayIndex].activities = updatedTravelDetail.days[
        dayIndex
      ].activities.filter((a) => a.id !== activity.id);

      setTravelDetail(updatedTravelDetail);
    }
  };

  const handleUpdateActivityTime = (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => {
    const updatedTravelDetail = { ...travelDetail };

    const dayIndex = updatedTravelDetail.days.findIndex(
      (d) => d.day === day.day
    );

    if (dayIndex !== -1) {
      const activityIndex = updatedTravelDetail.days[
        dayIndex
      ].activities.findIndex((a) => a.id === activity.id);

      if (activityIndex !== -1) {
        updatedTravelDetail.days[dayIndex].activities[activityIndex].time =
          newTime;
        setTravelDetail(updatedTravelDetail);
      }
    }
  };

  const handleMoveActivity = (
    dayId: number,
    fromIndex: number,
    toIndex: number
  ) => {
    try {
      // Log what we're trying to do to help debug
      console.log(
        `Moving in day ${dayId} from index ${fromIndex} to ${toIndex}`
      );

      // Make a safe copy of the travel detail
      const updatedTravelDetail = {
        ...travelDetail,
        days: travelDetail.days.map((day) => ({
          ...day,
          activities: [...day.activities],
        })),
      };

      const dayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === dayId
      );

      if (dayIndex !== -1) {
        const activities = updatedTravelDetail.days[dayIndex].activities;

        const sourceActivity = { ...activities[fromIndex] };
        const targetActivity = { ...activities[toIndex] };

        const sourceTime = sourceActivity.time;

        updatedTravelDetail.days[dayIndex].activities.splice(fromIndex, 1);
        updatedTravelDetail.days[dayIndex].activities.splice(
          toIndex,
          0,
          sourceActivity
        );

        const sortedTimes = activities
          .map((activity) => activity.time)
          .sort((a, b) => {
            // Extract start times and convert to minutes for comparison
            const aStart = a.split(" - ")[0];
            const bStart = b.split(" - ")[0];
            const aHours = parseInt(aStart.split(":")[0]);
            const aMinutes = parseInt(aStart.split(":")[1]);
            const bHours = parseInt(bStart.split(":")[0]);
            const bMinutes = parseInt(bStart.split(":")[1]);

            return aHours * 60 + aMinutes - (bHours * 60 + bMinutes);
          });

        updatedTravelDetail.days[dayIndex].activities.forEach(
          (activity, index) => {
            activity.time = sortedTimes[index];
          }
        );

        // Update the state
        setTravelDetail(updatedTravelDetail);
        console.log("Timeline updated successfully with reordered times");
      }
    } catch (error) {
      console.error("Error in handleMoveActivity:", error);
    }
  };
  const openAddActivityModal = (day: TravelDay) => {
    setDayForNewActivity(day);
    setActivitySearchModalVisible(true);
  };

  const handleAddCustomActivity = (searchValue: string) => {
    if (dayForNewActivity && searchValue.trim()) {
      const newActivity: TravelActivity = {
        id: `custom-${Date.now()}`,
        time: "12:00 - 14:00",
        type: "attraction",
        name: searchValue,
        location: "Địa điểm tùy chỉnh",
        description: "Hoạt động do người dùng tự thêm",
        imageUrl:
          "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
        rating: 5,
        price: "Chưa có thông tin",
      };

      const updatedTravelDetail = { ...travelDetail };

      const dayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === dayForNewActivity.day
      );

      if (dayIndex !== -1) {
        updatedTravelDetail.days[dayIndex].activities.push(newActivity);
        setTravelDetail(updatedTravelDetail);
      }

      setActivitySearchModalVisible(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-4">
        <Button icon={<ArrowLeftOutlined />} onClick={onBack} type="text">
          Quay lại danh sách kế hoạch
        </Button>

        <Button
          type="primary"
          icon={isEditMode ? <SaveOutlined /> : <EditOutlined />}
          onClick={toggleEditMode}
          className="!bg-black"
        >
          {isEditMode ? "Lưu thay đổi" : "Chỉnh sửa lịch trình"}
        </Button>
      </div>

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
                  isEditMode={isEditMode}
                  onReplaceActivity={handleReplaceActivity}
                  onDeleteActivity={handleDeleteActivity}
                  onUpdateActivityTime={handleUpdateActivityTime}
                  onAddActivity={openAddActivityModal}
                  onMoveActivity={handleMoveActivity}
                />
              ),
            },
            {
              key: "budget",
              label: "Tổng quát và xuất lịch",
              children: (
                <div className="p-4">
                  <h2>Tổng quan ngân sách</h2>
                  <p>
                    Tổng ngân sách: {formatCurrency(travelDetail.totalBudget)}
                  </p>
                  <p>Đã chi: {formatCurrency(travelDetail.spentBudget)}</p>
                  <p>
                    Còn lại:{" "}
                    {formatCurrency(
                      travelDetail.totalBudget - travelDetail.spentBudget
                    )}
                  </p>
                </div>
              ),
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

      {/* AI Suggestions Modal */}
      <Modal
        title="Gợi ý thay thế từ AI"
        open={showAISuggestions}
        onCancel={() => setShowAISuggestions(false)}
        footer={null}
        width={800}
      >
        {currentDay && (
          <AIActivitySuggestions
            day={currentDay}
            onSelectActivity={handleSelectAISuggestion}
          />
        )}
      </Modal>

      {/* Custom Activity Search Modal */}
      <Modal
        title="Thêm hoạt động tùy chỉnh"
        open={activitySearchModalVisible}
        onCancel={() => setActivitySearchModalVisible(false)}
        footer={null}
      >
        <p className="mb-4">
          Tìm kiếm địa điểm hoặc hoạt động bạn muốn thêm vào lịch trình:
        </p>
        <Search
          placeholder="Nhập tên địa điểm hoặc hoạt động..."
          enterButton="Thêm"
          size="large"
          onSearch={handleAddCustomActivity}
        />
      </Modal>
    </div>
  );
};
