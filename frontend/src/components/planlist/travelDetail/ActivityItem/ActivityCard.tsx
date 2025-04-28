import React, { memo } from "react";
import {
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
  SwapOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  DragOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  RightOutlined,
} from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../../types/travelPlan";
import { useActivityDnD } from "../../../../hooks/useActivityDnD";
import { useTimeEdit } from "../../../../hooks/useTimeEdit";

const { Title, Text } = Typography;

interface ActivityCardProps {
  day: TravelDay;
  activity: TravelActivity;
  index: number;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (a: TravelActivity) => void;
  isEditMode: boolean;
  onReplaceActivity?: (d: TravelDay, a: TravelActivity) => void;
  onDeleteActivity?: (d: TravelDay, a: TravelActivity) => void;
  onUpdateActivityTime?: (d: TravelDay, a: TravelActivity, t: string) => void;
  moveActivity: (from: number, to: number, dayId: number) => void;
}

export const ActivityCard: React.FC<ActivityCardProps> = memo(
  ({
    day,
    activity,
    index,
    activityTypeColors,
    onActivityClick,
    isEditMode,
    onReplaceActivity,
    onDeleteActivity,
    onUpdateActivityTime,
    moveActivity,
  }) => {
    const { ref, isDragging, isOver } = useActivityDnD(
      isEditMode,
      index,
      day.day,
      moveActivity
    );

    const timeEdit = useTimeEdit(activity.time, (newTime) => {
      onUpdateActivityTime?.(day, activity, newTime);
    });

    const cardClick = isEditMode ? undefined : () => onActivityClick(activity);

    return (
      <div
        ref={ref}
        className="mb-4"
        style={{
          opacity: isDragging ? 0.4 : 1,
          cursor: isEditMode ? "move" : "pointer",
          background: isOver ? "#f0f8ff" : undefined,
          border: isOver ? "1px dashed #1890ff" : undefined,
          transition: "all .2s ease",
        }}
      >
        <Card hoverable={!isEditMode} onClick={cardClick}>
          <div className="flex">
            {isEditMode && (
              <div className="mr-2 flex items-center text-gray-500">
                <DragOutlined />
              </div>
            )}

            <img
              src={activity.imageUrl}
              alt={activity.name}
              className="w-20 h-20 mr-4 rounded object-cover"
            />

            <div className="flex-1">
              {timeEdit.editing ? (
                <Space className="mb-2" onClick={(e) => e.stopPropagation()}>
                  <TimePicker
                    value={timeEdit.startTime}
                    format="HH:mm"
                    minuteStep={5}
                    size="small"
                    onChange={(v) => timeEdit.setStartTime(v!)}
                  />
                  <span>-</span>
                  <TimePicker
                    value={timeEdit.endTime}
                    format="HH:mm"
                    minuteStep={5}
                    size="small"
                    onChange={(v) => timeEdit.setEndTime(v!)}
                  />
                  <Button
                    size="small"
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={timeEdit.commit}
                  />
                </Space>
              ) : (
                <Tag color={activityTypeColors[activity.type]} className="mb-1">
                  <ClockCircleOutlined className="mr-1" />
                  {activity.time}
                  {isEditMode && (
                    <EditOutlined
                      className="ml-2 cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        timeEdit.begin();
                      }}
                    />
                  )}
                </Tag>
              )}

              <Title level={5} className="m-0">
                {activity.name}
              </Title>
              <Text type="secondary">
                <EnvironmentOutlined className="mr-1" /> {activity.location}
              </Text>
            </div>

            <div className="flex items-start">
              {isEditMode ? (
                <Space>
                  <Tooltip title="Thay thế bằng gợi ý từ AI">
                    <Button
                      icon={<SwapOutlined />}
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onReplaceActivity?.(day, activity);
                      }}
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
                    />
                  </Tooltip>
                </Space>
              ) : (
                <>
                  <Rate
                    disabled
                    allowHalf
                    value={activity.rating}
                    className="text-xs"
                  />
                  <RightOutlined className="ml-2 text-gray-400" />
                </>
              )}
            </div>
          </div>
        </Card>
      </div>
    );
  }
);

ActivityCard.displayName = "ActivityCard";
