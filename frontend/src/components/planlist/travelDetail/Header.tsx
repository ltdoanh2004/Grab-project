import React from "react";
import { Typography, Card, Tag, Divider } from "antd";
import {
  CalendarOutlined,
  TeamOutlined,
  DollarOutlined,
} from "@ant-design/icons";
import { TravelDetailData } from "../../../types/travelPlan";

const { Title, Text } = Typography;

interface TravelHeaderProps {
  travelDetail: TravelDetailData;
  formatDate: (date: Date) => string;
  calculateDurationDays: (start: Date, end: Date) => number;
  formatCurrency: (value: number) => string;
  getStatusTag: (status: TravelDetailData["status"]) => React.ReactNode;
}

export const TravelHeader: React.FC<TravelHeaderProps> = ({
  travelDetail,
  formatDate,
  calculateDurationDays,
  formatCurrency,
  getStatusTag,
}) => {
  return (
    <Card className="shadow-sm mb-6">
      <div className="flex flex-col md:flex-row">
        <div className="md:w-1/3 h-56 md:h-auto overflow-hidden rounded-lg">
          <img
            src={travelDetail.imageUrl}
            alt={travelDetail.destination}
            className="w-full h-full object-cover"
          />
        </div>

        <div className="md:w-2/3 md:pl-6 pt-4 md:pt-0">
          <div className="flex justify-between items-start">
            <div>
              <Title level={2} className="mb-2">
                {travelDetail.destination}
              </Title>
              <div className="flex items-center text-gray-600 mb-2">
                <CalendarOutlined className="mr-2" />
                <Text>
                  {formatDate(travelDetail.startDate)} -{" "}
                  {formatDate(travelDetail.endDate)} (
                  {calculateDurationDays(
                    travelDetail.startDate,
                    travelDetail.endDate
                  )}{" "}
                  ngày)
                </Text>
              </div>
              <div className="flex items-center text-gray-600">
                <TeamOutlined className="mr-2" />
                <Text>
                  {travelDetail.adults} người lớn
                  {travelDetail.children > 0
                    ? ` + ${travelDetail.children} trẻ em`
                    : ""}
                </Text>
                <Divider type="vertical" />
                <DollarOutlined className="mr-2" />
                <Text>{travelDetail.budgetType}</Text>
              </div>
            </div>

            {getStatusTag(travelDetail.status)}
          </div>

          <Divider className="my-4" />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Text type="secondary">Tổng ngân sách:</Text>
              <div className="font-semibold text-lg">
                {formatCurrency(travelDetail.totalBudget)}
              </div>
            </div>
            <div>
              <Text type="secondary">Đã chi tiêu:</Text>
              <div className="font-semibold text-lg">
                {formatCurrency(travelDetail.spentBudget)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
