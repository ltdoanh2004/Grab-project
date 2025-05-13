import React, { useState, useEffect } from "react";
import { List, Card, Button, Skeleton, Empty, Modal, Rate, Tag, Divider, Typography } from "antd";
import { 
  CheckOutlined, 
  EnvironmentOutlined, 
  DollarOutlined, 
  ClockCircleOutlined, 
  InfoCircleOutlined 
} from "@ant-design/icons";
import { TravelDay, TravelActivity } from "../../../types/travelPlan";

const { Title, Paragraph, Text } = Typography;

// Updated format to match API response
interface AISuggestion {
  activity_id: string;
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
}

// Add this function near the top of the file
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

// Update the mock suggestions to use the new images
const MOCK_AI_SUGGESTIONS: AISuggestion[] = [
  {
    activity_id: "s1",
    id: "attr_001",
    type: "attraction",
    name: "Bảo tàng Lịch sử Quốc gia",
    description: "Bảo tàng lớn với nhiều hiện vật quý về lịch sử Việt Nam từ thời tiền sử đến hiện đại.",
    address: "1 Tràng Tiền, Hoàn Kiếm, Hà Nội",
    rating: 4.5,
    price_ai_estimate: 30000,
    image_url: getDefaultImage("attraction")
  },
  {
    activity_id: "s2",
    id: "attr_002",
    type: "attraction",
    name: "Văn Miếu - Quốc Tử Giám",
    description: "Di tích lịch sử văn hóa quan trọng của Hà Nội, đại diện cho nền giáo dục Việt Nam thời phong kiến.",
    address: "58 Quốc Tử Giám, Đống Đa, Hà Nội",
    rating: 4.8,
    price_ai_estimate: 30000,
    image_url: getDefaultImage("attraction")
  },
  {
    activity_id: "s3",
    id: "restaurant_042",
    type: "restaurant",
    name: "Nhà hàng chay An Lạc",
    description: "Nhà hàng chay An Lạc mang đến thực đơn đa dạng với các món ăn chay được chế biến cầu kỳ và bổ dưỡng. Không gian yên tĩnh, thích hợp cho các buổi gặp gỡ.",
    address: "10 Trần Nhật Duật, Q1, TP.HCM",
    rating: 4.3,
    price_ai_estimate: 120000,
    image_url: getDefaultImage("restaurant")
  }
];

interface AIActivitySuggestionsProps {
  day?: TravelDay;
  onSelectActivity: (activity: TravelActivity | AISuggestion) => void;
  suggestions?: AISuggestion[];
  loading?: boolean;
}

export const AIActivitySuggestions: React.FC<AIActivitySuggestionsProps> = ({
  day,
  onSelectActivity,
  suggestions: propSuggestions,
  loading: propLoading,
}) => {
  const [loading, setLoading] = useState(propLoading !== undefined ? propLoading : true);
  const [suggestions, setSuggestions] = useState<AISuggestion[]>(propSuggestions || []);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<AISuggestion | null>(null);

  useEffect(() => {
    if (propSuggestions) {
      setSuggestions(propSuggestions);
      if (propLoading !== undefined) {
        setLoading(propLoading);
      } else {
        setLoading(false);
      }
      return;
    }

    const timer = setTimeout(() => {
      setLoading(false);
      setSuggestions(MOCK_AI_SUGGESTIONS);
    }, 1500);

    return () => clearTimeout(timer);
  }, [propSuggestions, propLoading]);

  const showDetailModal = (suggestion: AISuggestion) => {
    setSelectedSuggestion(suggestion);
    setDetailModalVisible(true);
  };

  const hideDetailModal = () => {
    setDetailModalVisible(false);
  };

  const getActivityTypeColor = (type: string) => {
    const typeColors: Record<string, string> = {
      restaurant: "orange",
      attraction: "blue",
      accommodation: "purple",
      hotel: "purple",
      transport: "green",
      shopping: "red",
      default: "default"
    };
    
    return typeColors[type] || typeColors.default;
  };

  const formatPrice = (suggestion: AISuggestion) => {
    if (suggestion.price) {
      return `${suggestion.price.toLocaleString('vi-VN')} VND`;
    } else if (suggestion.price_range) {
      return suggestion.price_range;
    } else if (suggestion.price_ai_estimate) {
      return `~${suggestion.price_ai_estimate.toLocaleString('vi-VN')} VND`;
    }
    return "Chưa có thông tin";
  };

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
    return <Empty description="Không có hoạt động gợi ý nào" />;
  }

  return (
    <>
      <List
        dataSource={suggestions.slice(0, 3)}
        renderItem={(suggestion) => (
          <List.Item>
            <Card 
              className="w-full hover:shadow-md transition-shadow" 
              hoverable
            >
              <div className="flex">
                <div className="w-24 h-24 mr-4 overflow-hidden rounded-lg shadow-sm flex-shrink-0">
                  <img
                    src={suggestion.image_url || getDefaultImage(suggestion.type)}
                    alt={suggestion.name}
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = getDefaultImage(suggestion.type);
                    }}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-col h-full">
                    <div className="flex justify-between items-start mb-1">
                      <div className="flex-1 mr-2">
                        <div className="flex items-center mb-1">
                          <h3 className="text-lg font-medium m-0 mr-2 truncate">
                            {suggestion.name}
                          </h3>
                          
                        </div>
                        
                        <div className="flex items-center mb-2">
                          {suggestion.rating && (
                            <div className="flex items-center mr-3">
                              <Rate 
                                disabled 
                                defaultValue={suggestion.rating} 
                                allowHalf 
                                className="text-xs" 
                              />
                              <span className="ml-1 text-gray-600 text-sm">
                                {suggestion.rating}
                              </span>
                            </div>
                          )}
                          
                          <Text type="secondary" className="text-sm flex items-center">
                            <DollarOutlined className="mr-1" />
                            {formatPrice(suggestion)}
                          </Text>
                        </div>

                        <div className="mb-1 text-gray-600 text-sm flex items-center">
                          <EnvironmentOutlined className="mr-1 flex-shrink-0" />
                          <span className="truncate">{suggestion.address || "Chưa có địa chỉ"}</span>
                        </div>
                        
                        <Paragraph 
                          className="text-gray-700 text-sm mb-2 line-clamp-2"
                          ellipsis={{ rows: 2, expandable: false }}
                        >
                          {suggestion.description}
                        </Paragraph>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center mt-auto">
                      <Button 
                        type="text" 
                        size="small"
                        icon={<InfoCircleOutlined />} 
                        onClick={(e) => {
                          e.stopPropagation();
                          showDetailModal(suggestion);
                        }}
                      >
                        Xem chi tiết
                      </Button>
                      
                      <Button
                        type="primary"
                        icon={<CheckOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectActivity(suggestion);
                        }}
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        Thêm vào lịch trình
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </List.Item>
        )}
      />

      {suggestions.length > 3 && (
        <div className="text-center mt-2 text-gray-500 text-sm">
          Hiển thị 3/{suggestions.length} gợi ý
        </div>
      )}

      {/* Detail Modal */}
      <Modal
        title="Chi tiết gợi ý"
        open={detailModalVisible}
        onCancel={hideDetailModal}
        footer={[
          <Button key="back" onClick={hideDetailModal}>
            Đóng
          </Button>,
          <Button
            key="select"
            type="primary"
            onClick={() => {
              if (selectedSuggestion) {
                onSelectActivity(selectedSuggestion);
                hideDetailModal();
              }
            }}
          >
            Chọn gợi ý này
          </Button>,
        ]}
        width={600}
      >
        {selectedSuggestion && (
          <div className="flex flex-col md:flex-row">
            <div className="w-full md:w-1/2 pr-0 md:pr-4 mb-4 md:mb-0">
              <div className="rounded-lg overflow-hidden shadow-md h-48 md:h-64">
                <img
                  src={selectedSuggestion.image_url || getDefaultImage(selectedSuggestion.type)}
                  alt={selectedSuggestion.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = getDefaultImage(selectedSuggestion.type);
                  }}
                />
              </div>
            </div>
            <div className="w-full md:w-1/2">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <h3 className="text-xl font-semibold m-0">
                    {selectedSuggestion.name}
                  </h3>
                  <Tag
                    color={getActivityTypeColor(selectedSuggestion.type)}
                    className="ml-2"
                  >
                    {selectedSuggestion.type}
                  </Tag>
                </div>
              </div>
              
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  {selectedSuggestion.rating && (
                    <div className="flex items-center">
                      <Rate 
                        disabled 
                        defaultValue={selectedSuggestion.rating} 
                        allowHalf 
                      />
                      <span className="ml-2 text-gray-600">
                        {selectedSuggestion.rating}
                      </span>
                    </div>
                  )}
                </div>
                <Text type="secondary" className="flex items-center text-lg">
                  <DollarOutlined className="mr-1" />
                  {formatPrice(selectedSuggestion)}
                </Text>
              </div>
              
              {selectedSuggestion.address && (
                <div className="mb-4">
                  <Title level={5}>Địa chỉ:</Title>
                  <div className="flex items-start">
                    <EnvironmentOutlined className="mt-1 mr-2 text-gray-500" />
                    <span>{selectedSuggestion.address}</span>
                  </div>
                </div>
              )}
              
              {(selectedSuggestion.start_time || selectedSuggestion.end_time) && (
                <div className="mb-4">
                  <Title level={5}>Thời gian:</Title>
                  <div className="flex items-start">
                    <ClockCircleOutlined className="mt-1 mr-2 text-gray-500" />
                    <span>
                      {selectedSuggestion.start_time && selectedSuggestion.end_time
                        ? `${selectedSuggestion.start_time} - ${selectedSuggestion.end_time}`
                        : selectedSuggestion.start_time || selectedSuggestion.end_time}
                    </span>
                  </div>
                </div>
              )}
              
              <Divider />
              
              <div>
                <Title level={5}>Mô tả:</Title>
                <Paragraph>{selectedSuggestion.description}</Paragraph>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
};
