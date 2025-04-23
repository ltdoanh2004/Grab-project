import React from "react";
import { Modal, Button, Image, Row, Col, Rate, Typography } from "antd";
import { PhoneOutlined, EnvironmentOutlined } from "@ant-design/icons";
import { TravelActivity } from "../../../types/travelPlan";

const { Paragraph } = Typography;

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
    >
      <Image
        src={activity.imageUrl}
        alt={activity.name}
        className="w-full h-64 object-cover rounded mb-4"
      />

      <Row gutter={16} className="mb-4">
        <Col span={12}>
          <div className="text-gray-500">Loại hoạt động</div>
          <div className="font-semibold">{activityTypeText[activity.type]}</div>
        </Col>
        <Col span={12}>
          <div className="text-gray-500">Thời gian</div>
          <div className="font-semibold">{activity.time}</div>
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
        </Col>
      </Row>

      <div className="mb-4">
        <div className="text-gray-500">Địa điểm</div>
        <div className="font-semibold flex items-center">
          <EnvironmentOutlined className="mr-2" />
          {activity.location}
        </div>
      </div>

      {activity.duration !== undefined && (
        <div className="mb-4">
          <div className="text-gray-500">Thời lượng</div>
          <div className="font-semibold">{activity.duration}</div>
        </div>
      )}

      <div className="mb-4">
        <div className="text-gray-500">Mô tả</div>
        <Paragraph>{activity.description}</Paragraph>
      </div>

      <div className="flex flex-wrap">
        {activity.contactInfo && (
          <Button
            icon={<PhoneOutlined />}
            className="mr-2 mb-2"
            href={`tel:${activity.contactInfo}`}
          >
            {activity.contactInfo}
          </Button>
        )}

        <Button icon={<EnvironmentOutlined />} className="mb-2">
          Xem bản đồ
        </Button>
      </div>
    </Modal>
  );
};
