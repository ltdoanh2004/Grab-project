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
} from "antd";
import {
  ArrowLeftOutlined,
  EditOutlined,
  SaveOutlined,
  ShareAltOutlined,
  CheckCircleFilled,
} from "@ant-design/icons";
import { SheetExport } from "./travelDetail/SheetExport";

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

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 relative">
      {/* Custom Notification */}
      {showCopyNotification && (
        <div
          style={{
            position: "fixed",
            top: "16px",
            right: "16px",
            backgroundColor: "#52c41a",
            color: "white",
            padding: "10px 16px",
            borderRadius: "4px",
            boxShadow:
              "0 3px 6px -4px rgba(0,0,0,.12), 0 6px 16px 0 rgba(0,0,0,.08)",
            display: "flex",
            alignItems: "center",
            zIndex: 9999,
          }}
        >
          <CheckCircleFilled style={{ marginRight: 8 }} />
          Đã copy đường dẫn lịch trình
        </div>
      )}

      <div className="flex justify-between items-center mb-4">
        <Button icon={<ArrowLeftOutlined />} onClick={onBack} type="text">
          Quay lại danh sách kế hoạch
        </Button>
        <div className="flex gap-2">
          <Tooltip title="Chia sẻ kế hoạch">
            <Button
              icon={<ShareAltOutlined />}
              onClick={handleShare}
              className="!rounded-full"
            >
              Chia sẻ
            </Button>
          </Tooltip>
          <Button
            type="primary"
            icon={isEditMode ? <SaveOutlined /> : <EditOutlined />}
            onClick={toggleEditMode}
            className="!bg-black"
          >
            {isEditMode ? "Lưu thay đổi" : "Chỉnh sửa lịch trình"}
          </Button>
        </div>
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
              key: "sheet",
              label: "Xuất Google Sheet",
              children: <SheetExport travelDetail={travelDetail} />,
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
