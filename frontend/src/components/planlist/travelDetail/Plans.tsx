import React, { useState, useRef, useCallback } from "react";
import {
  Collapse,
  Card,
  Tag,
  Typography,
  Rate,
  Button,
  Tooltip,
  TimePicker,
  Space,
} from "antd";
import {
  RightOutlined,
  EnvironmentOutlined,
  DeleteOutlined,
  SwapOutlined,
  PlusOutlined,
  EditOutlined,
  CheckOutlined,
  ClockCircleOutlined,
  DragOutlined,
} from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../types/travelPlan";
import dayjs from "dayjs";
import { useDrag, useDrop, DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

const { Title, Text } = Typography;
const { Panel } = Collapse;

// Item type for drag and drop
const ItemTypes = {
  ACTIVITY: "activity",
};

interface DragItem {
  type: string;
  id: string;
  dayId: number;
  index: number;
}

interface ActivityItemProps {
  day: TravelDay;
  activity: TravelActivity;
  index: number;
  getActivityIcon: (type: TravelActivity["type"]) => React.ReactNode;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (activity: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onDeleteActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onUpdateActivityTime?: (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => void;
  moveActivity: (dragIndex: number, hoverIndex: number, dayId: number) => void;
}

const ActivityItem: React.FC<ActivityItemProps> = ({
  day,
  activity,
  index,
  getActivityIcon,
  activityTypeColors,
  onActivityClick,
  isEditMode = false,
  onReplaceActivity,
  onDeleteActivity,
  onUpdateActivityTime,
  moveActivity,
}) => {
  const [editingActivity, setEditingActivity] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<dayjs.Dayjs | null>(null);
  const [endTime, setEndTime] = useState<dayjs.Dayjs | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  const handleTimeEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    const [start, end] = activity.time.split(" - ");
    setStartTime(dayjs(start, "HH:mm"));
    setEndTime(dayjs(end, "HH:mm"));
    setEditingActivity(activity.id);
  };

  const handleTimeSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (startTime && endTime && onUpdateActivityTime) {
      const formattedStartTime = startTime.format("HH:mm");
      const formattedEndTime = endTime.format("HH:mm");
      const newTimeValue = `${formattedStartTime} - ${formattedEndTime}`;
      onUpdateActivityTime(day, activity, newTimeValue);
    }
    setEditingActivity(null);
  };

  // Implement drag source
  const [{ isDragging }, drag] = useDrag(
    () => ({
      type: ItemTypes.ACTIVITY,
      item: {
        id: activity.id,
        index,
        dayId: day.day,
        type: ItemTypes.ACTIVITY,
      },
      collect: (monitor) => ({
        isDragging: monitor.isDragging(),
      }),
      canDrag: () => isEditMode,
    }),
    [index, activity.id, day.day, isEditMode]
  );

  const [{ isOver }, drop] = useDrop<DragItem, void, { isOver: boolean }>(
    () => ({
      accept: ItemTypes.ACTIVITY,
      collect: (monitor) => ({
        isOver: monitor.isOver(),
      }),
      hover: (item: DragItem, monitor) => {
        if (!ref.current || !isEditMode) {
          return;
        }

        const dragIndex = item.index;
        const hoverIndex = index;
        const dragDayId = item.dayId;

        if (dragIndex === hoverIndex && dragDayId === day.day) {
          return;
        }

        if (dragDayId !== day.day) {
          return;
        }

        moveActivity(dragIndex, hoverIndex, day.day);

        item.index = hoverIndex;
      },
      canDrop: () => isEditMode,
    }),
    [index, day.day, isEditMode, moveActivity]
  );

  drag(drop(ref));

  const cardClickHandler = isEditMode
    ? undefined
    : () => onActivityClick(activity);

  return (
    <div
      ref={ref}
      className="mb-4"
      style={{
        opacity: isDragging ? 0.4 : 1,
        cursor: isEditMode ? "move" : "pointer",
        backgroundColor: isOver ? "#f0f8ff" : "transparent",
        border: isOver ? "1px dashed #1890ff" : "none",
        transition: "all 0.2s ease",
      }}
    >
      <Card
        hoverable={!isEditMode}
        onClick={cardClickHandler}
        className="transition-all duration-200"
      >
        <div className="flex">
          {isEditMode && (
            <div className="mr-2 flex items-center text-gray-500">
              <DragOutlined className="text-lg" />
            </div>
          )}
          <div className="w-20 h-20 mr-4 overflow-hidden rounded">
            <img
              src={activity.imageUrl}
              alt={activity.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-start">
              <div>
                {editingActivity === activity.id ? (
                  <div className="flex items-center mb-2">
                    <Space>
                      <TimePicker
                        format="HH:mm"
                        value={startTime}
                        onChange={(value) => setStartTime(value)}
                        placeholder="Start time"
                        size="small"
                        use12Hours={false}
                        minuteStep={5}
                        allowClear={false}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <span>-</span>
                      <TimePicker
                        format="HH:mm"
                        value={endTime}
                        onChange={(value) => setEndTime(value)}
                        placeholder="End time"
                        size="small"
                        use12Hours={false}
                        minuteStep={5}
                        allowClear={false}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <Button
                        type="primary"
                        icon={<CheckOutlined />}
                        size="small"
                        className="!bg-green-500"
                        onClick={handleTimeSave}
                      />
                    </Space>
                  </div>
                ) : (
                  <Tag
                    color={activityTypeColors[activity.type]}
                    className="mb-1"
                  >
                    <ClockCircleOutlined className="mr-1" />
                    {activity.time}
                    {isEditMode && (
                      <EditOutlined
                        className="ml-2 cursor-pointer"
                        onClick={handleTimeEdit}
                      />
                    )}
                  </Tag>
                )}
                <Title level={5} className="m-0">
                  {activity.name}
                </Title>
                <Text type="secondary">
                  <EnvironmentOutlined className="mr-1" />
                  {activity.location}
                </Text>
              </div>
              <div className="flex items-center">
                {isEditMode ? (
                  <div className="flex space-x-2">
                    <Tooltip title="Thay thế bằng gợi ý từ AI">
                      <Button
                        type="primary"
                        icon={<SwapOutlined />}
                        size="small"
                        className="!bg-blue-500"
                        onClick={(e) => {
                          e.stopPropagation();
                          onReplaceActivity && onReplaceActivity(day, activity);
                        }}
                      />
                    </Tooltip>
                    <Tooltip title="Xóa hoạt động">
                      <Button
                        danger
                        icon={<DeleteOutlined />}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteActivity && onDeleteActivity(day, activity);
                        }}
                      />
                    </Tooltip>
                  </div>
                ) : (
                  <>
                    <Rate
                      value={activity.rating}
                      disabled
                      allowHalf
                      className="text-xs"
                    />
                    <RightOutlined className="ml-2 text-gray-400" />
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

interface TravelDayTimelineProps {
  day: TravelDay;
  getActivityIcon: (type: TravelActivity["type"]) => React.ReactNode;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (activity: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onDeleteActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onUpdateActivityTime?: (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => void;
  onMoveActivity: (dayId: number, fromIndex: number, toIndex: number) => void;
}

export const TravelDayTimeline: React.FC<TravelDayTimelineProps> = ({
  day,
  getActivityIcon,
  activityTypeColors,
  onActivityClick,
  isEditMode = false,
  onReplaceActivity,
  onDeleteActivity,
  onUpdateActivityTime,
  onMoveActivity,
}) => {
  const moveActivity = useCallback(
    (dragIndex: number, hoverIndex: number, dayId: number) => {
      if (isEditMode) {
        console.log(
          `Moving from ${dragIndex} to ${hoverIndex} in day ${dayId}`
        );
        onMoveActivity(dayId, dragIndex, hoverIndex);
      }
    },
    [isEditMode, onMoveActivity]
  );

  return (
    <div className="ml-4 mt-4">
      {day.activities.map((activity, index) => (
        <ActivityItem
          key={`${activity.id}-${index}`}
          day={day}
          activity={activity}
          index={index}
          getActivityIcon={getActivityIcon}
          activityTypeColors={activityTypeColors}
          onActivityClick={onActivityClick}
          isEditMode={isEditMode}
          onReplaceActivity={onReplaceActivity}
          onDeleteActivity={onDeleteActivity}
          onUpdateActivityTime={onUpdateActivityTime}
          moveActivity={moveActivity}
        />
      ))}
    </div>
  );
};

interface TravelItineraryProps {
  days: TravelDay[];
  formatDate: (date: Date) => string;
  getActivityIcon: (type: TravelActivity["type"]) => React.ReactNode;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (activity: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onDeleteActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onUpdateActivityTime?: (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => void;
  onAddActivity?: (day: TravelDay) => void;
  onMoveActivity?: (dayId: number, fromIndex: number, toIndex: number) => void;
}

export const TravelItinerary: React.FC<TravelItineraryProps> = ({
  days,
  formatDate,
  getActivityIcon,
  activityTypeColors,
  onActivityClick,
  isEditMode = false,
  onReplaceActivity,
  onDeleteActivity,
  onUpdateActivityTime,
  onAddActivity,
  onMoveActivity,
}) => {
  const handleMoveActivity = useCallback(
    (dayId: number, fromIndex: number, toIndex: number) => {
      if (onMoveActivity) {
        onMoveActivity(dayId, fromIndex, toIndex);
      }
    },
    [onMoveActivity]
  );

  return (
    <DndProvider backend={HTML5Backend}>
      <Collapse
        defaultActiveKey={["0"]}
        className="border-none shadow-none"
        expandIconPosition="end"
      >
        {days.map((day, index) => (
          <Panel
            key={index.toString()}
            header={
              <div className="flex items-center">
                <div className="bg-black text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">
                  {day.day}
                </div>
                <div>
                  <Text strong className="text-lg">
                    Ngày {day.day}
                  </Text>
                  <div className="text-gray-500 text-sm">
                    {formatDate(day.date)} • {day.activities.length} hoạt động
                  </div>
                </div>
              </div>
            }
            extra={
              isEditMode && (
                <Tooltip title="Thêm hoạt động mới" placement="left">
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    size="small"
                    className="!bg-green-500"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAddActivity && onAddActivity(day);
                    }}
                  />
                </Tooltip>
              )
            }
          >
            <TravelDayTimeline
              day={day}
              getActivityIcon={getActivityIcon}
              activityTypeColors={activityTypeColors}
              onActivityClick={onActivityClick}
              isEditMode={isEditMode}
              onReplaceActivity={onReplaceActivity}
              onDeleteActivity={onDeleteActivity}
              onUpdateActivityTime={onUpdateActivityTime}
              onMoveActivity={handleMoveActivity}
            />
          </Panel>
        ))}
      </Collapse>
    </DndProvider>
  );
};
