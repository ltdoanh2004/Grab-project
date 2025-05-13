import React, { useEffect, useState } from "react";
import { Modal, Button, Image, Row, Col, Rate, Typography, Spin, Space } from "antd";
import { PhoneOutlined, EnvironmentOutlined, LeftOutlined, RightOutlined } from "@ant-design/icons";
import { TravelActivity } from "../../../types/travelPlan";
import { getActivityDetail } from "../../../services/travelPlanApi";
import { ActivityDetail } from "../../../types/apiType";

const { Paragraph } = Typography;

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

interface ActivityModalProps {
  activity: TravelActivity | null;
  visible: boolean;
  onClose: () => void;
  activityTypeText: Record<TravelActivity["type"], string>;
}

export const ActivityModal: React.FC<ActivityModalProps> = ({
  activity,
  visible,
  onClose,
  activityTypeText,
}) => {
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [activityDetails, setActivityDetails] = useState<ActivityDetail | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const fetchActivityDetails = async () => {
      if (!activity || !visible) return;
      
      if (
        activity.name && 
        (activity.image_urls || activity.image_url) && 
        activity.address
      ) {
        return;
      }
      
      try {
        setLoading(true);
        const details = await getActivityDetail(activity.type, activity.id);
        setActivityDetails(details);
      } catch (error) {
        console.error("Error fetching activity details:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchActivityDetails();
    setCurrentImageIndex(0);
    setImageLoading(false);
  }, [activity, visible]);

  if (!activity) return null;

  const displayData = {
    ...activity,
    name: activity.name || activityDetails?.name || "",
    description: activity.description || activityDetails?.description || "",
    rating: activity.rating || activityDetails?.rating || 0,
    address: activity.address || activityDetails?.address || "",
    opening_hours: activity.opening_hours || activityDetails?.opening_hours,
    image_urls: activity.image_urls || activityDetails?.image_urls,
    additional_info: activity.additional_info || activityDetails?.additional_info,
    url: activity.url || activityDetails?.url
  };

  const timeStr =
    displayData.start_time && displayData.end_time
      ? `${displayData.start_time} - ${displayData.end_time}`
      : displayData.start_time || displayData.end_time || "";

  const images = (displayData.image_urls && displayData.image_urls.length > 0) 
      ? displayData.image_urls 
      : [displayData.image_url || displayData.imgUrl || getDefaultImage(activity.type)].filter(Boolean);

  const currentImage = images[currentImageIndex] || getDefaultImage(activity.type);

  const nextImage = () => {
    setImageLoading(true);
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setImageLoading(true);
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (index: number) => {
    if (index !== currentImageIndex) {
      setImageLoading(true);
      setCurrentImageIndex(index);
    }
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  return (
    <Modal
      title={displayData.name}
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="back" onClick={onClose}>
          Đóng
        </Button>,
        displayData.url && (
          <Button 
            key="link" 
            type="primary"
            href={displayData.url} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Truy cập website
          </Button>
        )
      ]}
      width={700}
      styles={{ body: { padding: "16px" } }}
    >
      {loading ? (
        <div className="flex justify-center items-center p-8">
          <Spin size="large" />
        </div>
      ) : (
        <>
          <div className="w-full h-72 lg:h-96 rounded-lg overflow-hidden mb-6 relative">
            {imageLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-50 z-10">
                <Spin size="large" />
              </div>
            )}
            <Image
              src={currentImage}
              alt={displayData.name}
              className="w-full h-full object-cover"
              fallback={getDefaultImage(activity.type)}
              preview={false}
              onLoad={handleImageLoad}
            />
            {images.length > 1 && (
              <>
                <Button 
                  icon={<LeftOutlined />} 
                  onClick={prevImage}
                  className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white shadow-md hover:bg-white z-20"
                  shape="circle"
                  size="large"
                />
                <Button 
                  icon={<RightOutlined />} 
                  onClick={nextImage}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white shadow-md hover:bg-white z-20"
                  shape="circle"
                  size="large"
                />
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
                  <Space size={2}>
                    {images.map((_, index) => (
                      <Button 
                        key={index} 
                        size="small" 
                        type={index === currentImageIndex ? "primary" : "default"}
                        shape="circle"
                        style={{ width: '8px', height: '8px', padding: 0, minWidth: '8px' }}
                        onClick={() => goToImage(index)}
                      />
                    ))}
                  </Space>
                </div>
              </>
            )}
          </div>

          {images.length > 1 && (
            <div className="mb-6 overflow-x-auto">
              <div className="flex space-x-2">
                {images.map((img, index) => (
                  <div 
                    key={index}
                    className={`h-16 w-24 cursor-pointer rounded overflow-hidden transition-all duration-200 flex items-center justify-center bg-gray-100 ${
                      index === currentImageIndex ? 'ring-2 ring-blue-500' : 'opacity-70 hover:opacity-100'
                    }`}
                    onClick={() => goToImage(index)}
                    style={{ minWidth: '6rem' }}
                  >
                    <div className="w-full h-full flex items-center justify-center">
                      <img
                        src={img}
                        alt={`${displayData.name} - ảnh ${index + 1}`}
                        className="max-h-full max-w-full object-cover"
                        onError={(e) => {
                          e.currentTarget.src = getDefaultImage(activity.type);
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Row gutter={16} className="mb-4">
            <Col span={12}>
              <div className="text-gray-500">Loại hoạt động</div>
              <div className="font-semibold">{activityTypeText[displayData.type]}</div>
            </Col>
            <Col span={12}>
              <div className="text-gray-500">Thời gian</div>
              <div className="font-semibold">{timeStr}</div>
            </Col>
          </Row>

          <Row gutter={16} className="mb-4">
            <Col span={12}>
              <div className="text-gray-500">Đánh giá</div>
              <div className="font-semibold flex items-center">
                <Rate
                  value={displayData.rating}
                  disabled
                  allowHalf
                  className="text-sm"
                />
                <span className="ml-2">{displayData.rating}/5</span>
              </div>
            </Col>
            <Col span={12}>
              {displayData.price !== undefined && displayData.price > 0 ? (
                <>
                  <div className="text-gray-500">Giá</div>
                  <div className="font-semibold">{displayData.price.toLocaleString('vi-VN')} VND</div>
                </>
              ) : displayData.price_range ? (
                <>
                  <div className="text-gray-500">Khoảng giá</div>
                  <div className="font-semibold">{displayData.price_range}</div>
                </>
              ) : displayData.price_ai_estimate && displayData.price_ai_estimate > 0 ? (
                <>
                  <div className="text-gray-500">Ước tính giá</div>
                  <div className="font-semibold">{displayData.price_ai_estimate.toLocaleString('vi-VN')} VND</div>
                </>
              ) : (
                <>
                  <div className="text-gray-500">Giá</div>
                  <div className="font-semibold text-gray-500 italic">Hiện chưa cập nhật giá tiền</div>
                </>
              )}
            </Col>
          </Row>

          <div className="mb-4">
            <div className="text-gray-500">Địa điểm</div>
            <div className="font-semibold flex items-center">
              <EnvironmentOutlined className="mr-2" />
              {displayData.address ? displayData.address : (
                <span className="text-gray-500 italic">Hiện chưa cập nhật địa chỉ</span>
              )}
            </div>
          </div>

          {displayData.opening_hours && (
            <div className="mb-4">
              <div className="text-gray-500">Giờ mở cửa</div>
              <div className="font-semibold">{displayData.opening_hours}</div>
            </div>
          )}

          {displayData.duration && (
            <div className="mb-4">
              <div className="text-gray-500">Thời lượng</div>
              <div className="font-semibold">{displayData.duration}</div>
            </div>
          )}

          <div className="mb-4">
            <div className="text-gray-500">Mô tả</div>
            <Paragraph>{displayData.description}</Paragraph>
          </div>

          {displayData.additional_info && (
            <div className="mb-4">
              <div className="text-gray-500">Thông tin thêm</div>
              <Paragraph>{displayData.additional_info}</Paragraph>
            </div>
          )}
        </>
      )}
    </Modal>
  );
};
