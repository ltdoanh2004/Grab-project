import React, { useState } from "react";
import {
  Collapse,
  Typography,
  Button,
  Tooltip,
  Tag,
  Divider,
  Card,
  Empty,
  Modal,
  List,
  Space,
} from "antd";
import { PlusOutlined, ClockCircleOutlined, BulbOutlined } from "@ant-design/icons";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { ActivityCard } from "./ActivityItem/ActivityCard";
import {
  TravelDay,
  TravelActivity,
  TravelSegment,
} from "../../../types/travelPlan";

const { Panel } = Collapse;
const { Text, Title } = Typography;

const TIME_OF_DAY_LABELS: Record<string, string> = {
  morning: "Buổi sáng",
  afternoon: "Buổi chiều",
  evening: "Buổi tối",
};

interface ItineraryProps {
  days: TravelDay[];
  formatDate: (d: string) => string;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (a: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (d: TravelDay, a: TravelActivity) => void;
  onDeleteActivity?: (d: TravelDay, a: TravelActivity) => void;
  onUpdateActivityTime?: (d: TravelDay, a: TravelActivity, t: string) => void;
  onAddActivity?: (d: TravelDay, segment?: TravelSegment) => void;
  onMoveActivity?: (
    fromDayIndex: number,
    fromSegment: string,
    fromActivityIndex: number,
    toDayIndex: number,
    toSegment: string,
    toActivityIndex: number
  ) => void;
}

export const TravelItinerary: React.FC<ItineraryProps> = ({
  days,
  formatDate,
  activityTypeColors,
  onActivityClick,
  isEditMode = false,
  onReplaceActivity,
  onDeleteActivity,
  onUpdateActivityTime,
  onAddActivity,
  onMoveActivity,
}) => {
  const [activeKeys, setActiveKeys] = useState<string[]>(days.map(day => day.date));
  const [tipsModalVisible, setTipsModalVisible] = useState(false);
  const [currentDayTips, setCurrentDayTips] = useState<{ title: string, tips: string[] }>({ title: "", tips: [] });

  if (!days || days.length === 0) {
    return (
      <Empty
        description="Chưa có lịch trình nào"
        className="my-8"
      />
    );
  }

  const handleMoveActivity = (
    fromActivityIndex: number,
    toActivityIndex: number,
    fromDayIndex: number,
    toDayIndex: number,
    fromSegment: string,
    toSegment: string
  ) => {
    // Call parent's onMoveActivity if provided
    if (onMoveActivity) {
      onMoveActivity(
        fromDayIndex,
        fromSegment,
        fromActivityIndex,
        toDayIndex,
        toSegment,
        toActivityIndex
      );
    }
  };

  const showDailyTips = (day: TravelDay, dayIdx: number) => {
    if (day.daily_tips && day.daily_tips.length > 0) {
      setCurrentDayTips({ 
        title: day.day_title || `Ngày ${dayIdx + 1}`, 
        tips: day.daily_tips 
      });
      setTipsModalVisible(true);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <Collapse 
        activeKey={activeKeys}
        onChange={(keys) => setActiveKeys(keys as string[])}
        bordered={false}
        className="travel-itinerary"
      >
        {days.map((day, dayIdx) => (
          <Panel
            key={day.date}
            header={
              <div className="flex justify-between items-center w-full">
                <div className="flex items-center">
                  <div className="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3">
                    {dayIdx + 1}
                  </div>
                  <div>
                    <Text strong className="text-lg">
                      {day.day_title || `Ngày ${dayIdx + 1}`}
                    </Text>
                    <div className="text-gray-500 text-sm">
                      {formatDate(day.date)}
                    </div>
                  </div>
                </div>
                {day.daily_tips && day.daily_tips.length > 0 && (
                  <Tooltip title="Xem các mẹo cho ngày này">
                    <Button 
                      icon={<BulbOutlined />} 
                      type="text"
                      className="text-yellow-500 hover:text-yellow-600"
                      onClick={(e) => {
                        e.stopPropagation();
                        showDailyTips(day, dayIdx);
                      }}
                    />
                  </Tooltip>
                )}
              </div>
            }
            className="mb-4 bg-white rounded-lg shadow-sm"
          >
            {day.segments.map((segment) => (
              <div key={segment.time_of_day} className="mb-6 last:mb-0">
                <div className="flex items-center mb-3">
                  <ClockCircleOutlined className="mr-2 text-gray-500" />
                  <Text strong className="text-base">
                    {TIME_OF_DAY_LABELS[segment.time_of_day] ||
                      segment.time_of_day}
                  </Text>
                  {isEditMode && (
                    <Tooltip
                      title="Thêm hoạt động vào khung giờ này"
                      placement="left"
                    >
                      <Button
                        size="small"
                        icon={<PlusOutlined />}
                        className="ml-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          onAddActivity?.(day, segment);
                        }}
                      />
                    </Tooltip>
                  )}
                </div>
                <Divider className="my-2" />
                {segment.activities.length === 0 ? (
                  <div className="text-gray-400 italic mb-4 ml-2">
                    Chưa có hoạt động nào
                  </div>
                ) : (
                  <div className="space-y-4">
                    {segment.activities.map((activity, activityIdx) => (
                      <ActivityCard
                        key={activity.id}
                        day={day}
                        activity={activity}
                        index={activityIdx}
                        dayIndex={dayIdx}
                        segment={segment.time_of_day}
                        activityTypeColors={activityTypeColors}
                        onActivityClick={onActivityClick}
                        isEditMode={isEditMode}
                        onReplaceActivity={onReplaceActivity}
                        onDeleteActivity={onDeleteActivity}
                        onUpdateActivityTime={onUpdateActivityTime}
                        moveActivity={handleMoveActivity}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </Panel>
        ))}
      </Collapse>

      <Modal
        title={
          <Space>
            <BulbOutlined className="text-yellow-500" />
            <span>Mẹo cho {currentDayTips.title}</span>
          </Space>
        }
        open={tipsModalVisible}
        onCancel={() => setTipsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTipsModalVisible(false)}>
            Đóng
          </Button>
        ]}
      >
        <List
          dataSource={currentDayTips.tips}
          renderItem={(tip, index) => (
            <List.Item>
              <div className="flex items-start">
                <div className="bg-yellow-100 text-yellow-800 rounded-full w-6 h-6 flex items-center justify-center mr-3 mt-0.5">
                  {index + 1}
                </div>
                <Text>{tip}</Text>
              </div>
            </List.Item>
          )}
        />
      </Modal>
    </DndProvider>
  );
};
