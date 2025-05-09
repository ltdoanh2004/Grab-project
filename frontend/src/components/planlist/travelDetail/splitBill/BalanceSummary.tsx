import React from "react";
import { Card, Typography, Row, Col, Statistic } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";
import { BalanceSummaryProps } from "../../../../types/splitBillTypes";
import { CURRENT_USER_ID } from "../../../../hooks/useSplitBill";

const { Title } = Typography;

export const BalanceSummary: React.FC<BalanceSummaryProps & { getDisplayName: (id: string) => string }> = ({
  balances,
  totalOwed,
  totalOwing,
  getDisplayName,
}) => {
  return (
    <Card className="mb-4">
      <Title level={5}>Tổng Quát Chi Phí</Title>
      <Row gutter={16}>
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
        <Title level={5}>Chi Tiết Số Dư</Title>
        {Object.entries(balances).map(([personId, amount]) => (
          <div key={personId} className="flex justify-between items-center py-2">
            <span>{getDisplayName(personId)}</span>
            <span
              className={
                amount > 0
                  ? "text-green-600 font-semibold flex items-center"
                  : amount < 0
                  ? "text-red-600 font-semibold flex items-center"
                  : "flex items-center"
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
                "Đã cân bằng"
              )}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}; 