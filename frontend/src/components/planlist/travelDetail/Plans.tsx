import React, { useCallback, memo } from "react";
import { Collapse, Typography, Button, Tooltip } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";

import {
  TravelDay,
  TravelActivity,
  ItemTypes,
  DragItem,
} from "../../../types/travelPlan";
import { ActivityCard } from "./ActivityItem/ActivityCard";
import { useActivityDnD } from "../../../hooks/useActivityDnD";
import { useTimeEdit } from "../../../hooks/useTimeEdit";

const { Panel } = Collapse;
const { Text } = Typography;

interface TimelineProps {
  day: TravelDay;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (a: TravelActivity) => void;
  isEditMode: boolean;
  onReplaceActivity?: (d: TravelDay, a: TravelActivity) => void;
  onDeleteActivity?: (d: TravelDay, a: TravelActivity) => void;
  onUpdateActivityTime?: (d: TravelDay, a: TravelActivity, t: string) => void;
  onMove: (dayId: number, from: number, to: number) => void;
}

const Timeline: React.FC<TimelineProps> = memo(
  ({
    day,
    activityTypeColors,
    onActivityClick,
    isEditMode,
    onReplaceActivity,
    onDeleteActivity,
    onUpdateActivityTime,
    onMove,
  }) => {
    const move = useCallback(
      (from: number, to: number) => onMove(day.day, from, to),
      [onMove, day.day]
    );

    return (
      <div className="ml-4 mt-4">
        {day.activities.map((a, idx) => (
          <ActivityCard
            key={a.id}
            day={day}
            activity={a}
            index={idx}
            activityTypeColors={activityTypeColors}
            onActivityClick={onActivityClick}
            isEditMode={isEditMode}
            onReplaceActivity={onReplaceActivity}
            onDeleteActivity={onDeleteActivity}
            onUpdateActivityTime={onUpdateActivityTime}
            moveActivity={move}
          />
        ))}
      </div>
    );
  }
);
Timeline.displayName = "Timeline";

interface ItineraryProps {
  days: TravelDay[];
  formatDate: (d: Date) => string;
  activityTypeColors: Record<TravelActivity["type"], string>;
  onActivityClick: (a: TravelActivity) => void;
  isEditMode?: boolean;
  onReplaceActivity?: (d: TravelDay, a: TravelActivity) => void;
  onDeleteActivity?: (d: TravelDay, a: TravelActivity) => void;
  onUpdateActivityTime?: (d: TravelDay, a: TravelActivity, t: string) => void;
  onAddActivity?: (d: TravelDay) => void;
  onMoveActivity?: (dayId: number, from: number, to: number) => void;
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
  onMoveActivity = () => {},
}) => (
  <DndProvider backend={HTML5Backend}>
    <Collapse defaultActiveKey={["0"]} bordered={false}>
      {days.map((day) => (
        <Panel
          key={day.day}
          header={
            <div className="flex items-center">
              <div className="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3">
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
              <Tooltip title="Thêm hoạt động" placement="left">
                <Button
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddActivity?.(day);
                  }}
                />
              </Tooltip>
            )
          }
        >
          <Timeline
            day={day}
            activityTypeColors={activityTypeColors}
            onActivityClick={onActivityClick}
            isEditMode={isEditMode}
            onReplaceActivity={onReplaceActivity}
            onDeleteActivity={onDeleteActivity}
            onUpdateActivityTime={onUpdateActivityTime}
            onMove={onMoveActivity}
          />
        </Panel>
      ))}
    </Collapse>
  </DndProvider>
);
