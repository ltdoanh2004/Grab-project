import React, { useState } from "react";
import { Card, Typography, Row, Col, Statistic, Button, message, Tooltip } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined, BellOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { BalanceSummaryProps } from "../../../../types/splitBillTypes";
import { CURRENT_USER_ID } from "../../../../hooks/useSplitBill";

const { Title } = Typography;

export const BalanceSummary: React.FC<BalanceSummaryProps & { getDisplayName: (id: string) => string }> = ({
  balances,
  totalOwed,
  totalOwing,
  getDisplayName,
}) => {
  // Track payment status for each person
  const [paidStatus, setPaidStatus] = useState<Record<string, boolean>>({});

  // Handle payment confirmation
  const handleConfirmPayment = (personId: string) => {
    setPaidStatus(prev => ({
      ...prev,
      [personId]: true
    }));
    message.success(`Đã xác nhận thanh toán với ${getDisplayName(personId)}`);
  };

  // Handle reminder (just for display)
  const handleReminder = () => {
    message.info("Đã gửi thông báo nhắc nhở cho những thành viên chưa thanh toán");
  };

  return (
    <Card className="mb-4">
      <Title level={5}>Tổng Quát Chi Phí</Title>
      <Row gutter={16} className="flex justify-center text-center">
        <Col span={12}>
          <Statistic
            title="Tổng số tiền bạn được nhận"
            value={totalOwed}
            precision={0}
            valueStyle={{ color: "#3f8600" }}
            prefix="₫"
            suffix=""
            formatter={(value) => `${value.toLocaleString('vi-VN')}`}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="Tổng số tiền bạn cần trả"
            value={totalOwing}
            precision={0}
            valueStyle={{ color: "#cf1322" }}
            prefix="₫"
            suffix=""
            formatter={(value) => `${value.toLocaleString('vi-VN')}`}
          />
        </Col>
      </Row>
      <div className="mt-4">
        <div className="flex justify-between items-center mb-2">
          <Title level={5} className="m-0">Chi Tiết Số Dư</Title>
          <Button
            icon={<BellOutlined />}
            onClick={handleReminder}
          >
            Nhắc nhở
          </Button>
        </div>
        {Object.entries(balances).map(([personId, amount]) => (
          <div key={personId} className="flex flex-col md:flex-row md:justify-between md:items-center py-3 border-b border-gray-100 last:border-0">
            <div className="flex items-center justify-between mb-2 md:mb-0">
              <span className="font-medium">{getDisplayName(personId)}</span>
              <span
                className={
                  amount > 0
                    ? "text-green-600 font-semibold flex items-center md:ml-4"
                    : amount < 0
                    ? "text-red-600 font-semibold flex items-center md:ml-4"
                    : "flex items-center md:ml-4"
                }
              >
                {amount > 0 ? (
                  <>
                    <ArrowUpOutlined className="mr-1" /> Nhận{" "}
                    {amount.toLocaleString("vi-VN")}₫
                  </>
                ) : amount < 0 ? (
                  <>
                    <ArrowDownOutlined className="mr-1" /> Trả{" "}
                    {Math.abs(amount).toLocaleString("vi-VN")}₫
                  </>
                ) : (
                  "Đã chia đều"
                )}
              </span>
            </div>
            
            {personId !== CURRENT_USER_ID && amount !== 0 && (
              <div>
                {paidStatus[personId] ? (
                  <span className="text-green-600 font-medium flex items-center">
                    <CheckCircleOutlined className="mr-1" /> Đã thanh toán
                  </span>
                ) : (
                  <Button
                    type="primary"
                    size="small"
                    onClick={() => handleConfirmPayment(personId)}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Xác nhận thanh toán
                  </Button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}; 