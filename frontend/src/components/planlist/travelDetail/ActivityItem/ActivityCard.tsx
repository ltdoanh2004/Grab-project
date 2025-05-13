import React, { memo, useRef } from "react";
import {
  Card,
  Tag,
  Typography,
  Rate,
  Button,
  Tooltip,
  TimePicker,
  Space,
  Image,
  Badge,
} from "antd";
import {
  SwapOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  DragOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  RightOutlined,
  MessageOutlined,
  DollarOutlined,
} from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../../types/travelPlan";
import { useDrag, useDrop } from "react-dnd";
import { ItemTypes } from "../../../../types/travelPlan";
import { useTimeEdit } from "../../../../hooks/useTimeEdit";
import { ActivityCommentModal } from "./Comment";

const { Title, Text } = Typography;

interface ActivityCardProps {
  day: TravelDay;
  activity: TravelActivity;
  index: number;
  dayIndex: number;
  segment: string;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (a: TravelActivity) => void;
  isEditMode: boolean;
  onReplaceActivity?: (d: TravelDay, a: TravelActivity) => void;
  onDeleteActivity?: (d: TravelDay, a: TravelActivity) => void;
  onUpdateActivityTime?: (d: TravelDay, a: TravelActivity, t: string) => void;
  moveActivity: (
    fromIndex: number,
    toIndex: number,
    fromDayId: number,
    toDayId: number,
    fromSegment: string,
    toSegment: string
  ) => void;
}

// Activity drag item type
interface DragItem {
  id: string;
  index: number;
  dayIndex: number;
  segment: string;
}

const DEFAULT_IMAGE = "/notfound.png";
const HOTEL_IMAGE = "/hotel.jpg";
const PLACE_IMAGE = "/place.jpg";
const RESTAURANT_IMAGE = "/restaurant.jpg";

export const ActivityCard: React.FC<ActivityCardProps> = memo(
  ({
    day,
    activity,
    index,
    dayIndex,
    segment,
    activityTypeColors,
    onActivityClick,
    isEditMode,
    onReplaceActivity,
    onDeleteActivity,
    onUpdateActivityTime,
    moveActivity,
  }) => {
    const ref = useRef<HTMLDivElement>(null);
    const [showCommentModal, setShowCommentModal] = React.useState(false);
    
    const getDefaultImage = (type: string) => {
      if (type === "hotel" || type === "accommodation") {
        return HOTEL_IMAGE;
      } else if (type === "attraction" || type === "place") {
        return PLACE_IMAGE;
      } else if (type === "restaurant") {
        return RESTAURANT_IMAGE;
      }
      return DEFAULT_IMAGE;
    };
    
    const imageUrl = activity.type === "hotel" || activity.type === "accommodation" 
      ? HOTEL_IMAGE 
      : (activity.image_url || activity.imgUrl || getDefaultImage(activity.type));
    
    // Simple drag implementation
    const [{ isDragging }, drag] = useDrag({
      type: ItemTypes.ACTIVITY,
      item: (): DragItem => ({
        id: activity.id,
        index,
        dayIndex,
        segment
      }),
      canDrag: () => isEditMode,
      collect: (monitor) => ({
        isDragging: !!monitor.isDragging()
      })
    });
    
    // Drop implementation to handle swapping
    const [{ isOver }, drop] = useDrop({
      accept: ItemTypes.ACTIVITY,
      collect: (monitor) => ({
        isOver: !!monitor.isOver()
      }),
      drop: (item: DragItem) => {
        // Don't do anything if dropping onto itself
        if (item.index === index && item.dayIndex === dayIndex && item.segment === segment) {
          return;
        }
        
        // Call the moveActivity function to swap the items
        moveActivity(
          item.index,
          index,
          item.dayIndex,
          dayIndex,
          item.segment,
          segment
        );
      },
      canDrop: () => isEditMode
    });
    
    // Apply the drag and drop refs
    drag(drop(ref));

    const timeEdit = useTimeEdit(
      `${activity.start_time} - ${activity.end_time}`,
      (newTime) => {
        onUpdateActivityTime?.(day, activity, newTime);
      }
    );

    const cardClick = isEditMode ? undefined : () => onActivityClick(activity);

    const formatTime = (time: string) => {
      if (!time) return "";
      return time.replace(":", "h") + "p";
    };

    const displayTime = activity.start_time && activity.end_time
      ? `${formatTime(activity.start_time)} - ${formatTime(activity.end_time)}`
      : "Chưa có thời gian";

    const typeColor = activityTypeColors[activity.type] || "blue";
    
    return (
      <div
        ref={ref}
        className={`mb-4 flex items-center group transition-all duration-300 ${
          isDragging ? "opacity-40" : "opacity-100"
        } ${isOver ? "bg-blue-50 rounded-lg" : ""}`}
        style={{
          cursor: isEditMode ? "move" : "pointer",
          border: isOver ? "1px dashed #1890ff" : undefined,
        }}
      >
        <Card
          hoverable={!isEditMode}
          onClick={cardClick}
          className="flex-1 transition-all duration-300 hover:shadow-lg border border-gray-100 overflow-hidden"
          styles={{ body: { padding: "16px" } }}
        >
          <div className="flex">
            {isEditMode && (
              <div className="mr-3 flex items-center text-gray-400">
                <DragOutlined className="text-lg" />
              </div>
            )}

            <div className="relative w-32 h-24 md:w-36 md:h-28 mr-4 rounded-lg overflow-hidden shadow-md flex-shrink-0">
              <Image
                src={imageUrl}
                alt={activity.name}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                fallback={DEFAULT_IMAGE}
                preview={false}
              />
            </div>

            <div className="flex-1 min-w-0">
              {timeEdit.editing ? (
                <Space className="mb-3" onClick={(e) => e.stopPropagation()}>
                  <TimePicker
                    value={timeEdit.startTime}
                    format="HH:mm"
                    minuteStep={5}
                    size="small"
                    onChange={(v) => timeEdit.setStartTime(v!)}
                    className="hover:border-blue-500"
                  />
                  <span className="text-gray-400">-</span>
                  <TimePicker
                    value={timeEdit.endTime}
                    format="HH:mm"
                    minuteStep={5}
                    size="small"
                    onChange={(v) => timeEdit.setEndTime(v!)}
                    className="hover:border-blue-500"
                  />
                  <Button
                    size="small"
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={timeEdit.commit}
                    className="bg-blue-500 hover:bg-blue-600"
                  />
                </Space>
              ) : (
                <Tag
                  color={typeColor}
                  className="mb-3 px-3 py-1 text-sm font-medium rounded-full"
                >
                  <ClockCircleOutlined className="mr-1" />
                  {displayTime}
                  {isEditMode && (
                    <EditOutlined
                      className="ml-2 cursor-pointer hover:text-blue-500 transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        timeEdit.begin();
                      }}
                    />
                  )}
                </Tag>
              )}

              <div className="flex items-center justify-between mb-2">
                <Title level={5} className="m-0 text-lg font-semibold text-gray-800 truncate pr-4">
                  {activity.name}
                </Title>
                
                {activity.rating && !isEditMode && (
                  <div className="flex items-center">
                    <Rate
                      disabled
                      allowHalf
                      value={activity.rating}
                      className="text-xs scale-75 origin-right"
                    />
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <Text className="flex items-center text-gray-600 text-sm">
                  <EnvironmentOutlined className="mr-2 text-gray-400" />
                  <span className="truncate">
                    {activity.address ? activity.address : (
                      <span className="text-gray-500 italic">Hiện chưa cập nhật địa chỉ</span>
                    )}
                  </span>
                </Text>

                {activity.description && (
                  <Text className="block text-gray-500 text-sm line-clamp-2">
                    {activity.description}
                  </Text>
                )}

                <Text className="flex items-center text-sm font-medium text-green-600">
                  <DollarOutlined className="mr-1" />
                  {activity.price_range ? activity.price_range :
                    activity.price && activity.price > 50000 ? `${activity.price.toLocaleString()} VND` :
                    activity.price_ai_estimate && activity.price_ai_estimate > 0 ? `${activity.price_ai_estimate.toLocaleString()} VND` :
                    <span className="text-gray-500 italic font-normal">Hiện chưa cập nhật giá tiền</span>
                  }
                </Text>
              </div>
            </div>

            <div className="flex items-start justify-end ml-3">
              {isEditMode ? (
                <Space direction="vertical" size="small">
                  <Tooltip title="Thay thế bằng gợi ý từ AI">
                    <Button
                      icon={<SwapOutlined />}
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onReplaceActivity?.(day, activity);
                      }}
                      className="hover:bg-blue-50 hover:text-blue-500"
                    />
                  </Tooltip>
                  <Tooltip title="Xoá hoạt động">
                    <Button
                      danger
                      icon={<DeleteOutlined />}
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteActivity?.(day, activity);
                      }}
                      className="hover:bg-red-50"
                    />
                  </Tooltip>
                </Space>
              ) : (
                <div className="flex flex-col items-end justify-between h-full">
                  <RightOutlined className="text-gray-300 group-hover:text-gray-400 transition-colors mt-1" />
                </div>
              )}
            </div>
          </div>
        </Card>

        <div className="flex flex-col items-center justify-center h-full mx-2">
          <Tooltip title="Bình luận">
            <Button
              type="text"
              icon={
                <MessageOutlined
                  className={`text-lg transition-colors duration-200 ${
                    showCommentModal ? "text-blue-500" : "text-gray-400"
                  }`}
                />
              }
              onClick={(e) => {
                e.stopPropagation();
                setShowCommentModal(true);
              }}
              className={`flex items-center justify-center h-8 w-8 rounded-full transition-all duration-200 ${
                showCommentModal
                  ? "bg-blue-50 ring-2 ring-blue-500"
                  : "bg-gray-50 hover:bg-gray-100"
              }`}
            />
          </Tooltip>
        </div>

        <ActivityCommentModal
          open={showCommentModal}
          onClose={() => setShowCommentModal(false)}
          activityId={activity.activity_id || activity.id}
          activityType={activity.type}
        />
      </div>
    );
  }
);

ActivityCard.displayName = "ActivityCard";
