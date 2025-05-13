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
  List,
  Rate,
  Tag,
} from "antd";
import {
  ArrowLeftOutlined,
  EditOutlined,
  SaveOutlined,
  ShareAltOutlined,
  CheckCircleFilled,
  PlusOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  PlusCircleOutlined,
} from "@ant-design/icons";
import { SplitBill } from "./travelDetail/splitBill";

import {
  formatDate,
  ACTIVITY_TYPE_COLORS,
  ACTIVITY_TYPE_TEXT,
  formatCurrency,
  calculateDurationDays,
  getStatusTag,
  MOCK_AI_SUGGESTIONS,
} from "../../constants/travelPlanConstants";
import { ActivityModal } from "./travelDetail/ActivityDetail";
import { TravelHeader } from "./travelDetail/Header";
import { TravelItinerary } from "./travelDetail/Plans";
import { AIActivitySuggestions } from "./travelDetail/AISuggestions";
import { useTravelDetail } from "../../hooks/useTravelDetail";
import { TravelActivity } from "../../types/travelPlan";

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
    handleSelectAISuggestion: originalHandleSelectAISuggestion,
    handleDeleteActivity,
    handleUpdateActivityTime,
    handleMoveActivity,
    openAddActivityModal,
    handleAddCustomActivity,
    setTravelDetail,
  } = useTravelDetail(travelId);

  const [showCopyNotification, setShowCopyNotification] = useState(false);
  const [searchResults, setSearchResults] = useState<typeof MOCK_AI_SUGGESTIONS>([]);
  const [searchValue, setSearchValue] = useState('');

  React.useEffect(() => {
    const handleReplaceActivityEvent = (event: CustomEvent<{
      activityId: string;
      replacementActivity: TravelActivity;
    }>) => {
      if (!travelDetail) return;
      
      const { activityId, replacementActivity } = event.detail;
      
      const updatedTravelDetail = {
        ...travelDetail,
        plan_by_day: travelDetail.plan_by_day.map(day => {
          return {
            ...day,
            segments: day.segments.map(segment => {
              return {
                ...segment,
                activities: segment.activities.map(act => {
                  if (act.id === activityId) {
                    console.log(`Found activity to replace: ${act.name} -> ${replacementActivity.name}`);
                    return {
                      ...replacementActivity,
                      id: act.id,
                      start_time: act.start_time || replacementActivity.start_time,
                      end_time: act.end_time || replacementActivity.end_time
                    };
                  }
                  return act;
                })
              };
            })
          };
        })
      };
      
      setTravelDetail(updatedTravelDetail);
    };

    window.addEventListener('replaceActivity', handleReplaceActivityEvent as EventListener);

    return () => {
      window.removeEventListener('replaceActivity', handleReplaceActivityEvent as EventListener);
    };
  }, [travelDetail, setTravelDetail]);

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

  const handleSelectAISuggestion = (activity: TravelActivity | {
    activity_id?: string;
    id: string;
    type: string;
    name: string;
    description: string;
    address?: string;
    price?: number;
    price_range?: string;
    price_ai_estimate?: number;
    rating?: number;
    image_url?: string;
    start_time?: string;
    end_time?: string;
  }) => {
    // Ensure activity has required properties of TravelActivity
    const travelActivity: TravelActivity = {
      ...activity,
      id: activity.id,
      type: activity.type,
      name: activity.name,
      description: activity.description || '',
      start_time: activity.start_time || '08:00',
      end_time: activity.end_time || '09:00',
      image_url: activity.image_url || getDefaultImage(activity.type)
    };
    
    if (currentDay && activityToReplace && travelDetail) {
      const updatedTravelDetail = {
        ...travelDetail,
        plan_by_day: travelDetail.plan_by_day.map(day => {
          if (day.date !== currentDay.date) {
            return day;
          }
          
          return {
            ...day,
            segments: day.segments.map(segment => {
              return {
                ...segment,
                activities: segment.activities.map(act => {
                  if (act.id === activityToReplace.id) {
                    return {
                      ...travelActivity,
                      id: act.id,
                      start_time: act.start_time || travelActivity.start_time,
                      end_time: act.end_time || travelActivity.end_time
                    };
                  }
                  return act;
                })
              };
            })
          };
        })
      };
      
      // Update the state
      setTravelDetail(updatedTravelDetail);
      
      setShowAISuggestions(false);
      
      message.success(`Đã thay thế ${activityToReplace.name} bằng ${travelActivity.name}`);
      
      return;
    }
    
    originalHandleSelectAISuggestion(travelActivity);
  };

  const handleSearch = (value: string) => {
    setSearchValue(value);
    
    if (!value.trim()) {
      setSearchResults([]);
      return;
    }
    
    const filteredResults = MOCK_AI_SUGGESTIONS.filter(item => 
      item.name.toLowerCase().includes(value.toLowerCase()) ||
      item.description.toLowerCase().includes(value.toLowerCase()) ||
      (item.address && item.address.toLowerCase().includes(value.toLowerCase())) ||
      item.type.toLowerCase().includes(value.toLowerCase())
    );
    
    setSearchResults(filteredResults);
  };
  
  const getDefaultImage = (type: string) => {
    switch (type) {
      case 'place':
      case 'attraction':
        return "/place.jpg";
      case 'hotel':
      case 'accommodation':
        return "/hotel.jpg";
      case 'restaurant':
        return "/restaurant.jpg";
      default:
        return "/place.jpg"; // Fallback to place.jpg for unknown types
    }
  };

  const handleSelectSearchResult = (activity: (typeof MOCK_AI_SUGGESTIONS)[0]) => {
    if (travelDetail && dayForNewActivity) {
      const newActivity: TravelActivity = {
        id: `custom-${Date.now()}`,
        type: activity.type,
        name: activity.name,
        start_time: activity.start_time,
        end_time: activity.end_time,
        description: activity.description,
        address: activity.address,
        rating: activity.rating,
        price: activity.price,
        image_url: activity.image_url || getDefaultImage(activity.type),
        duration: activity.duration,
      };
      
      const updatedTravelDetail = { ...travelDetail };
      updatedTravelDetail.plan_by_day = updatedTravelDetail.plan_by_day.map(
        (d) => {
          if (d.date !== dayForNewActivity.date) return d;
          return {
            ...d,
            segments: d.segments.map((segment, idx) =>
              idx === 0
                ? {
                    ...segment,
                    activities: [...segment.activities, newActivity],
                  }
                : segment
            ),
          };
        }
      );
      
      setTravelDetail(updatedTravelDetail);
      setActivitySearchModalVisible(false);
      setSearchResults([]);
      setSearchValue('');
      
      message.success(`Đã thêm ${activity.name} vào lịch trình`);
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
                      const fromStartTime = fromActivity.start_time;
                      const fromEndTime = fromActivity.end_time;
                      const toStartTime = toActivity.start_time;
                      const toEndTime = toActivity.end_time;

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
    <div className="max-w-6xl mx-auto pb-28 relative">
      {/* Custom Notification */}
      {showCopyNotification && (
        <div className="fixed top-4 right-4 bg-green-500 text-white py-2 px-4 rounded-lg shadow-lg flex items-center z-50 animate-fade-in-down">
          <CheckCircleFilled className="mr-2" />
          Đã copy đường dẫn lịch trình
        </div>
      )}

      <Affix offsetTop={0} className="z-10">
        <div className="flex items-center py-3 px-4 bg-white shadow-sm">
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={onBack}
            type="text"
            className="hover:bg-gray-50 flex items-center"
          >
            <span className="ml-1">Quay lại</span>
          </Button>
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

      {/* Edit and Share buttons at the bottom right */}
      <div className="fixed right-6 bottom-6 flex flex-col space-y-3">
        <Tooltip title={isEditMode ? "Lưu thay đổi" : "Chỉnh sửa lịch trình"}>
          <Button
            type="primary"
            shape="circle"
            size="large"
            icon={isEditMode ? <SaveOutlined /> : <EditOutlined />}
            onClick={toggleEditMode}
            className={`h-14 w-14 flex items-center justify-center shadow-lg ${
              isEditMode
                ? "bg-green-600 hover:bg-green-700"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          />
        </Tooltip>
        
        <Tooltip title="Chia sẻ lịch trình">
          <Button
            shape="circle"
            size="large"
            icon={<ShareAltOutlined />}
            onClick={handleShare}
            className="h-14 w-14 flex items-center justify-center border-gray-300 hover:border-blue-500 hover:text-blue-500 shadow-lg"
          />
        </Tooltip>
      </div>

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
        onCancel={() => {
          setActivitySearchModalVisible(false);
          setSearchResults([]);
          setSearchValue('');
        }}
        footer={null}
        width={600}
        className="custom-activity-modal"
      >
        <p className="mb-4">
          Tìm kiếm hoạt động để thêm vào lịch trình ngày {dayForNewActivity ? formatDate(dayForNewActivity.date) : ''}.
        </p>
        <Search
          placeholder="Tìm địa điểm, hoạt động..."
          className="mb-4"
          value={searchValue}
          onChange={(e) => handleSearch(e.target.value)}
          onSearch={handleSearch}
        />
        <div className="max-h-96 overflow-y-auto">
          {searchResults.length > 0 ? (
            <List
              dataSource={searchResults}
              renderItem={(item) => (
                <List.Item
                  className="cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => handleSelectSearchResult(item)}
                >
                  <div className="flex w-full">
                    <div className="w-16 h-16 mr-3 rounded-lg overflow-hidden">
                      <img
                        src={item.image_url || getDefaultImage(item.type)}
                        alt={item.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = getDefaultImage(item.type);
                        }}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="text-base font-medium m-0">{item.name}</h4>
                        <Tag color={ACTIVITY_TYPE_COLORS[item.type] || 'blue'}>
                          {ACTIVITY_TYPE_TEXT[item.type] || item.type}
                        </Tag>
                      </div>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        {item.address && (
                          <span className="flex items-center mr-3">
                            <EnvironmentOutlined className="mr-1" />
                            {item.address.substring(0, 30)}{item.address.length > 30 ? '...' : ''}
                          </span>
                        )}
                        {item.price && (
                          <span className="flex items-center mr-3">
                            <DollarOutlined className="mr-1" />
                            {formatCurrency(item.price)}
                          </span>
                        )}
                        {item.rating && (
                          <Rate
                            disabled
                            allowHalf
                            defaultValue={item.rating}
                            style={{ fontSize: 12 }}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          ) : searchValue ? (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500">Không tìm thấy kết quả phù hợp</p>
            </div>
          ) : (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500">Nhập từ khóa để tìm kiếm hoạt động</p>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};
