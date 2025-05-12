import React from "react";
import { Typography, Card, Tag, Divider, Image, Row, Col, Statistic, Progress, Button } from "antd";
import {
  CalendarOutlined,
  TeamOutlined,
  DollarOutlined,
  EnvironmentOutlined,
  BankOutlined,
  TagOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { TravelDetailData } from "../../../types/travelPlan";
import { downloadExcel } from "./SheetExport";

const { Title, Text } = Typography;

const DEFAULT_IMAGE = "/hinhnen.jpg";

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
  const days = calculateDurationDays(
    new Date(travelDetail.start_date),
    new Date(travelDetail.end_date)
  );

  // Function to handle Excel export
  const handleExportExcel = () => {
    downloadExcel(travelDetail);
  };

  return (
    <div className="mb-6">
      <Card 
        className="overflow-hidden rounded-xl shadow-md border-0"
        styles={{ body: { padding: 0 } }}
      >
        <div className="relative">
          {/* Hero Image */}
          <div className="h-64 md:h-80 w-full relative">
            <Image
              src={travelDetail.imageUrl || DEFAULT_IMAGE}
              alt={travelDetail.destination}
              className="w-full h-full object-cover"
              fallback={DEFAULT_IMAGE}
              preview={false}
            />
            <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/70"></div>
            
            {/* Status Badge */}
            <div className="absolute top-4 right-4">
              {getStatusTag(travelDetail.status)}
            </div>
            
            {/* Destination Title - Mobile Only */}
            <div className="md:hidden absolute bottom-0 left-0 w-full p-4 text-white">
              <Title level={2} className="m-0 text-white">
                {travelDetail.destination}
              </Title>
              <div className="flex items-center mt-1">
                <EnvironmentOutlined className="mr-1" />
                <Text className="text-white opacity-90">
                  {travelDetail.notes || "Khám phá và trải nghiệm"}
                </Text>
              </div>
            </div>
          </div>
          
          {/* Content */}
          <div className="bg-white p-6 relative">
            <Row gutter={[24, 16]} align="top">
              {/* Left Column - Title and Dates */}
              <Col xs={24} md={16} className="pr-6">
                {/* Title - Desktop Only */}
                <div className="hidden md:block">
                  <Title level={1} className="mb-3">
                    {travelDetail.destination}
                  </Title>
                  {travelDetail.notes && (
                    <div className="flex items-start mb-4">
                      <EnvironmentOutlined className="mt-1 mr-2 text-gray-500" />
                      <Text className="text-gray-600">{travelDetail.notes}</Text>
                    </div>
                  )}
                </div>
                
                {/* Trip Details */}
                <div className="space-y-3">
                  <div className="flex items-center text-gray-700">
                    <CalendarOutlined className="mr-3 text-gray-500" />
                    <div>
                      <div className="font-medium mb-0.5">{formatDate(new Date(travelDetail.start_date))} - {formatDate(new Date(travelDetail.end_date))}</div>
                      <div className="text-sm text-gray-500">{days} ngày</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-gray-700">
                    <TeamOutlined className="mr-3 text-gray-500" />
                    <div>
                      <div className="font-medium">
                        {travelDetail.adults || 2} người lớn
                        {travelDetail.children && travelDetail.children > 0
                          ? ` + ${travelDetail.children} trẻ em`
                          : ""}
                      </div>
                    </div>
                  </div>
                  
                  {travelDetail.budgetType && (
                    <div className="flex items-center text-gray-700">
                      <TagOutlined className="mr-3 text-gray-500" />
                      <div>
                        <div className="font-medium">
                          Loại ngân sách: {travelDetail.budgetType}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </Col>
              
              {/* Right Column - Budget Info */}
              <Col xs={24} md={8} className="md:border-l md:pl-6">
                <div>
                  <Title level={4} className="mb-4">
                    <BankOutlined className="mr-2" /> Ngân sách
                  </Title>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <Statistic 
                      title="Tổng ngân sách"
                      value={travelDetail.totalBudget && travelDetail.totalBudget > 0 ? travelDetail.totalBudget : 5000000}
                      valueStyle={{ color: '#3f8600' }}
                      formatter={(value) => formatCurrency(value as number)}
                    />
                    
                    <Statistic 
                      title="Đã chi tiêu"
                      value={travelDetail.spentBudget && travelDetail.spentBudget > 0 ? travelDetail.spentBudget : 3000000}
                      valueStyle={{ color: (travelDetail.spentBudget || 3000000) > (travelDetail.totalBudget || 5000000) ? '#cf1322' : '#1677ff' }}
                      formatter={(value) => formatCurrency(value as number)}
                    />
                  </div>
                  
                  <div className="mt-4">
                    <div className="flex justify-between mb-1">
                      <Text className="text-gray-500">Chi tiêu:</Text>
                      <Text strong>
                        {Math.round(((travelDetail.spentBudget || 3000000) / (travelDetail.totalBudget || 5000000)) * 100)}%
                      </Text>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${(travelDetail.spentBudget || 3000000) > (travelDetail.totalBudget || 5000000) ? 'bg-red-500' : 'bg-blue-500'}`}
                        style={{ width: `${Math.min(100, Math.round(((travelDetail.spentBudget || 3000000) / (travelDetail.totalBudget || 5000000)) * 100))}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <Button 
                    type="primary" 
                    icon={<DownloadOutlined />} 
                    onClick={handleExportExcel}
                    className="mt-4 w-full bg-blue-600 hover:bg-blue-700"
                  >
                    Xuất Excel
                  </Button>
                </div>
              </Col>
            </Row>
          </div>
        </div>
      </Card>
    </div>
  );
};
