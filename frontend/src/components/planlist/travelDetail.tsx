import React, { useState } from "react";
import {
  Button,
  Card,
  Tabs,
  Modal,
  Input,
  message,
  Tooltip,
  Spin,
  notification,
  Result,
  Affix,
} from "antd";
import {
  ArrowLeftOutlined,
  EditOutlined,
  SaveOutlined,
  ShareAltOutlined,
  CheckCircleFilled,
  PlusOutlined,
} from "@ant-design/icons";
import { SheetExport } from "./travelDetail/SheetExport";
import { SplitBill } from "./travelDetail/splitBill";

import {
  formatDate,
  ACTIVITY_TYPE_COLORS,
  ACTIVITY_TYPE_TEXT,
  formatCurrency,
  calculateDurationDays,
  getStatusTag,
} from "../../constants/travelPlanConstants";
import { ActivityModal } from "./travelDetail/ActivityDetail";
import { TravelHeader } from "./travelDetail/Header";
import { TravelItinerary } from "./travelDetail/Plans";
import { AIActivitySuggestions } from "./travelDetail/AISuggestions";
import { useTravelDetail } from "../../hooks/useTravelDetail";

const { Search } = Input;

interface TravelDetailProps {
  travelId: string;
  onBack: () => void;
}

export const TravelDetail: React.FC<TravelDetailProps> = ({
  travelId,
  onBack,
}) => {
  const {
    travelDetail,
    loading,
    notFound,
    activeTab,
    setActiveTab,
    activityModalVisible,
    setActivityModalVisible,
    selectedActivity,
    isEditMode,
    toggleEditMode,
    showAISuggestions,
    setShowAISuggestions,
    currentDay,
    activityToReplace,
    activitySearchModalVisible,
    setActivitySearchModalVisible,
    dayForNewActivity,
    showActivityDetail,
    handleReplaceActivity,
    handleSelectAISuggestion,
    handleDeleteActivity,
    handleUpdateActivityTime,
    handleMoveActivity,
    openAddActivityModal,
    handleAddCustomActivity,
    setTravelDetail,
  } = useTravelDetail(travelId);

  const [showCopyNotification, setShowCopyNotification] = useState(false);

  const handleShare = async () => {
    if (!travelDetail) return;
    const shareUrl = `${window.location.origin}/trips/${travelDetail.id}`;
    try {
      await navigator.clipboard.writeText(shareUrl);

      setShowCopyNotification(true);
      setTimeout(() => {
        setShowCopyNotification(false);
      }, 3000);

      message.success("Đã copy đường dẫn lịch trình");
    } catch {
      message.error("Không thể sao chép liên kết.");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spin size="large" />
      </div>
    );
  }

  if (notFound || !travelDetail) {
    return (
      <Result
        status="404"
        title="Không tìm thấy kế hoạch"
        subTitle="Kế hoạch du lịch này không tồn tại hoặc đã bị xóa."
        extra={
          <Button type="primary" onClick={onBack}>
            Quay lại danh sách
          </Button>
        }
      />
    );
  }

  const tabItems = [
    {
      key: "itinerary",
      label: "Lịch trình",
      children: (
        <div className="min-h-[200px]">
          <TravelItinerary
            days={travelDetail.plan_by_day}
            formatDate={formatDate}
            activityTypeColors={ACTIVITY_TYPE_COLORS}
            onActivityClick={showActivityDetail}
            isEditMode={isEditMode}
            onReplaceActivity={handleReplaceActivity}
            onDeleteActivity={handleDeleteActivity}
            onUpdateActivityTime={handleUpdateActivityTime}
            onAddActivity={openAddActivityModal}
            onMoveActivity={(
              fromDayIndex,
              fromSegment,
              fromActivityIndex,
              toDayIndex,
              toSegment,
              toActivityIndex
            ) => {
              const fromDay = travelDetail.plan_by_day[fromDayIndex];
              const toDay = travelDetail.plan_by_day[toDayIndex];

              if (fromDay && toDay) {
                // Find activities in both segments
                const fromSegmentObj = fromDay.segments.find(
                  (s) => s.time_of_day === fromSegment
                );
                const toSegmentObj = toDay.segments.find(
                  (s) => s.time_of_day === toSegment
                );

                if (fromSegmentObj && toSegmentObj) {
                  // Get activities to swap
                  const fromActivity =
                    fromSegmentObj.activities[fromActivityIndex];
                  const toActivity = toSegmentObj.activities[toActivityIndex];

                  if (fromActivity && toActivity) {
                    // Create a deep copy of the travel detail
                    const updatedTravelDetail = {
                      ...travelDetail,
                      plan_by_day: [
                        ...travelDetail.plan_by_day.map((day) => ({
                          ...day,
                          segments: day.segments.map((segment) => ({
                            ...segment,
                            activities: [...segment.activities],
                          })),
                        })),
                      ],
                    };

                    // Get references to the updated days and segments
                    const updatedFromDay =
                      updatedTravelDetail.plan_by_day[fromDayIndex];
                    const updatedToDay =
                      updatedTravelDetail.plan_by_day[toDayIndex];
                    const updatedFromSegment = updatedFromDay.segments.find(
                      (s) => s.time_of_day === fromSegment
                    );
                    const updatedToSegment = updatedToDay.segments.find(
                      (s) => s.time_of_day === toSegment
                    );

                    if (updatedFromSegment && updatedToSegment) {
                      // Extract time information from both activities
                      const fromStartTime = fromActivity.start_time;
                      const fromEndTime = fromActivity.end_time;
                      const toStartTime = toActivity.start_time;
                      const toEndTime = toActivity.end_time;

                      // Create copies of the activities with swapped times
                      const fromActivityCopy = {
                        ...fromActivity,
                        start_time: toStartTime,
                        end_time: toEndTime,
                      };

                      const toActivityCopy = {
                        ...toActivity,
                        start_time: fromStartTime,
                        end_time: fromEndTime,
                      };

                      // Perform the swap
                      updatedFromSegment.activities[fromActivityIndex] =
                        toActivityCopy;
                      updatedToSegment.activities[toActivityIndex] =
                        fromActivityCopy;

                      // Update the state
                      setTravelDetail(updatedTravelDetail);
                    }
                  }
                }
              }
            }}
          />
        </div>
      ),
    },
    {
      key: "sheet",
      label: "Xuất Google Sheet",
      children: (
        <div className="min-h-[200px]">
          <SheetExport travelDetail={travelDetail} />
        </div>
      ),
    },
    {
      key: "splitbill",
      label: "Chia chi phí",
      children: (
        <div className="min-h-[200px]">
          <SplitBill travelDetail={travelDetail} />
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-6xl mx-auto pb-20 relative">
      {/* Custom Notification */}
      {showCopyNotification && (
        <div className="fixed top-4 right-4 bg-green-500 text-white py-2 px-4 rounded-lg shadow-lg flex items-center z-50 animate-fade-in-down">
          <CheckCircleFilled className="mr-2" />
          Đã copy đường dẫn lịch trình
        </div>
      )}

      <Affix offsetTop={0} className="z-10">
        <div className="flex justify-between items-center py-3 px-4 bg-white shadow-sm">
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={onBack}
            type="text"
            className="hover:bg-gray-50 flex items-center"
          >
            <span className="ml-1">Quay lại</span>
          </Button>
          <div className="flex items-center gap-2">
            <Button
              icon={<ShareAltOutlined />}
              onClick={handleShare}
              className="border-gray-300 hover:border-blue-500 hover:text-blue-500 rounded-full"
            >
              Chia sẻ
            </Button>
            <Button
              type="primary"
              icon={isEditMode ? <SaveOutlined /> : <EditOutlined />}
              onClick={toggleEditMode}
              className={
                isEditMode
                  ? "bg-green-600 hover:bg-green-700"
                  : "bg-blue-600 hover:bg-blue-700"
              }
            >
              {isEditMode ? "Lưu thay đổi" : "Chỉnh sửa lịch trình"}
            </Button>
          </div>
        </div>
      </Affix>

      <div className="px-4">
        <TravelHeader
          travelDetail={travelDetail}
          formatDate={formatDate}
          calculateDurationDays={calculateDurationDays}
          formatCurrency={formatCurrency}
          getStatusTag={getStatusTag}
        />

        <Card
          className="rounded-xl shadow-sm overflow-hidden mb-6 border-0"
          styles={{ body: { padding: 0 } }}
        >
          <div className="travel-tabs-container">
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              className="travel-detail-tabs"
              tabBarStyle={{
                margin: 0,
                padding: "0 16px",
              }}
              items={tabItems}
              size="large"
              tabBarGutter={24}
            />
          </div>
        </Card>
      </div>

      {/* FAB for adding activity in edit mode */}
      {isEditMode && (
        <div className="fixed right-6 bottom-6">
          <Button
            type="primary"
            shape="circle"
            size="large"
            icon={<PlusOutlined />}
            onClick={() => setActivitySearchModalVisible(true)}
            className="h-14 w-14 flex items-center justify-center bg-blue-600 hover:bg-blue-700 shadow-lg"
          />
        </div>
      )}

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
        className="ai-suggestion-modal"
        styles={{ body: { maxHeight: "70vh", overflowY: "auto" } }}
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
        width={600}
        className="custom-activity-modal"
      >
        <p className="mb-4">
          Chọn ngày và nhập thông tin để thêm hoạt động mới vào lịch trình của
          bạn.
        </p>
        <Search
          placeholder="Tìm địa điểm, hoạt động..."
          className="mb-4"
          onSearch={handleAddCustomActivity}
        />
        <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
          <p className="text-gray-400">Kết quả tìm kiếm sẽ hiển thị ở đây</p>
        </div>
      </Modal>
    </div>
  );
};
