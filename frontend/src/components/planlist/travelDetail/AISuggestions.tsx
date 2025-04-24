import React, { useState, useEffect } from "react";
import { List, Card, Button, Skeleton, Empty } from "antd";
import { CheckOutlined, EnvironmentOutlined } from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../types/travelPlan";
import { MOCK_AI_SUGGESTIONS } from "../../../constants/travelPlanConstants";

interface AIActivitySuggestionsProps {
  day: TravelDay;
  onSelectActivity: (activity: TravelActivity) => void;
}

export const AIActivitySuggestions: React.FC<AIActivitySuggestionsProps> = ({
  day,
  onSelectActivity,
}) => {
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState<TravelActivity[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
      setSuggestions(MOCK_AI_SUGGESTIONS);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="space-y-4 p-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="w-full">
            <Skeleton active avatar paragraph={{ rows: 2 }} />
          </Card>
        ))}
      </div>
    );
  }

  if (!suggestions.length) {
    return <Empty description="Không có hoạt động gợi ý nào cho ngày này" />;
  }

  return (
    <List
      dataSource={suggestions}
      renderItem={(activity) => (
        <List.Item>
          <Card className="w-full hover:shadow-md transition-shadow" hoverable>
            <div className="flex">
              <div className="w-24 h-24 mr-4 overflow-hidden rounded">
                <img
                  src={activity.imageUrl}
                  alt={activity.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium mb-1">
                      {activity.name}
                    </h3>
                    <div className="flex items-center text-gray-500 mb-1">
                      <EnvironmentOutlined className="mr-1" />
                      <span>{activity.location}</span>
                    </div>
                    <div className="mb-2">
                      <span className="text-sm">{activity.rating}/5</span>
                    </div>
                    <p className="text-gray-700 text-sm line-clamp-2">
                      {activity.description}
                    </p>
                  </div>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={() => onSelectActivity(activity)}
                    className="!bg-black"
                  >
                    Thêm vào lịch trình
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </List.Item>
      )}
    />
  );
};
