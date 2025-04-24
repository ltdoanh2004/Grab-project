import React from "react";
import {
  Collapse,
  Timeline,
  Card,
  Tag,
  Typography,
  Rate,
  Button,
  Tooltip,
} from "antd";
import {
  RightOutlined,
  EnvironmentOutlined,
  DeleteOutlined,
  SwapOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../types/travelPlan";

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface TravelDayTimelineProps {
  day: TravelDay;
  getActivityIcon: (type: TravelActivity["type"]) => React.ReactNode;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (activity: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (day: TravelDay, activity: TravelActivity) => void;
  onDeleteActivity?: (day: TravelDay, activity: TravelActivity) => void;
}

export const TravelDayTimeline: React.FC<TravelDayTimelineProps> = ({
  day,
  getActivityIcon,
  activityTypeColors,
  onActivityClick,
  isEditMode = false,
  onReplaceActivity,
  onDeleteActivity,
}) => {
  return (
    <Timeline className="ml-4 mt-4">
      {day.activities.map((activity) => (
        <Timeline.Item
          key={activity.id}
          dot={getActivityIcon(activity.type)}
          color={activityTypeColors[activity.type]}
        >
          <Card
            hoverable={!isEditMode}
            className="mb-4"
            onClick={isEditMode ? undefined : () => onActivityClick(activity)}
          >
            <div className="flex">
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
                    <Tag
                      color={activityTypeColors[activity.type]}
                      className="mb-1"
                    >
                      {activity.time}
                    </Tag>
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
                            onClick={() =>
                              onReplaceActivity &&
                              onReplaceActivity(day, activity)
                            }
                          />
                        </Tooltip>
                        <Tooltip title="Xóa hoạt động">
                          <Button
                            danger
                            icon={<DeleteOutlined />}
                            size="small"
                            onClick={() =>
                              onDeleteActivity &&
                              onDeleteActivity(day, activity)
                            }
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
        </Timeline.Item>
      ))}
    </Timeline>
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
  onAddActivity?: (day: TravelDay) => void;
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
  onAddActivity,
}) => {
  return (
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
          />
        </Panel>
      ))}
    </Collapse>
  );
};
