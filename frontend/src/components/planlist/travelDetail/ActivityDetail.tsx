import React from "react";
import { Modal, Button, Image, Row, Col, Rate, Typography } from "antd";
import { PhoneOutlined, EnvironmentOutlined } from "@ant-design/icons";
import { TravelActivity } from "../../../types/travelPlan";

const { Paragraph } = Typography;

const DEFAULT_IMAGE = "/hinhnen.jpg";

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
  if (!activity) return null;

  const timeStr =
    activity.start_time && activity.end_time
      ? `${activity.start_time} - ${activity.end_time}`
      : activity.start_time || activity.end_time || "";

  return (
    <Modal
      title={activity.name}
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="back" onClick={onClose}>
          Đóng
        </Button>,
      ]}
      width={700}
      styles={{ body: { padding: "16px" } }}
    >
      <div className="w-full h-72 lg:h-96 rounded-lg overflow-hidden mb-6">
        <Image
          src={activity.image_url || activity.imgUrl || DEFAULT_IMAGE}
          alt={activity.name}
          className="w-full h-full object-cover"
          fallback={DEFAULT_IMAGE}
          preview={true}
        />
      </div>

      <Row gutter={16} className="mb-4">
        <Col span={12}>
          <div className="text-gray-500">Loại hoạt động</div>
          <div className="font-semibold">{activityTypeText[activity.type]}</div>
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
              value={activity.rating}
              disabled
              allowHalf
              className="text-sm"
            />
            <span className="ml-2">{activity.rating}/5</span>
          </div>
        </Col>
        <Col span={12}>
          {activity.price !== undefined && (
            <>
              <div className="text-gray-500">Giá</div>
              <div className="font-semibold">{activity.price}</div>
            </>
          )}
          {activity.price_range && (
            <>
              <div className="text-gray-500">Khoảng giá</div>
              <div className="font-semibold">{activity.price_range}</div>
            </>
          )}
        </Col>
      </Row>

      <div className="mb-4">
        <div className="text-gray-500">Địa điểm</div>
        <div className="font-semibold flex items-center">
          <EnvironmentOutlined className="mr-2" />
          {activity.address || "Không có thông tin"}
        </div>
      </div>

      {activity.duration && (
        <div className="mb-4">
          <div className="text-gray-500">Thời lượng</div>
          <div className="font-semibold">{activity.duration}</div>
        </div>
      )}

      <div className="mb-4">
        <div className="text-gray-500">Mô tả</div>
        <Paragraph>{activity.description}</Paragraph>
      </div>
    </Modal>
  );
};
