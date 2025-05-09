import React from "react";
import {
  Card,
  Typography,
  Button,
  Table,
  Tag,
  Empty,
  Space,
  Tooltip,
} from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  BankOutlined,
  CalendarOutlined,
  UserOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { ExpenseListProps } from "../../../../types/splitBillTypes";

const { Title, Text } = Typography;

// Helper function to get category color
const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    "Ăn uống": "green",
    "Di chuyển": "blue",
    "Chỗ ở": "purple",
    "Hoạt động": "orange",
    "Mua sắm": "pink",
    "Khác": "default",
  };
  return colorMap[category] || "default";
};

export const ExpenseList: React.FC<ExpenseListProps> = ({
  expenses,
  onRemoveExpense,
  onAddExpense,
  getDisplayName,
}) => {
  const columns = [
    {
      title: "Mô tả",
      dataIndex: "description",
      key: "description",
      render: (text: string) => <span className="font-medium">{text}</span>,
    },
    {
      title: "Loại",
      dataIndex: "category",
      key: "category",
      render: (category: string) => (
        <Tag color={getCategoryColor(category)}>{category}</Tag>
      ),
    },
    {
      title: "Ngày",
      dataIndex: "date",
      key: "date",
      render: (date: string) => (
        <span className="flex items-center">
          <CalendarOutlined className="mr-1" /> {date}
        </span>
      ),
    },
    {
      title: "Số tiền",
      dataIndex: "amount",
      key: "amount",
      render: (amount: number) => (
        <span className="font-bold">
          {Math.round(amount).toLocaleString("vi-VN")}₫
        </span>
      ),
    },
    {
      title: "Người trả",
      dataIndex: "paidBy",
      key: "paidBy",
      render: (paidBy: string) => (
        <span className="flex items-center">
          <UserOutlined className="mr-1" /> {getDisplayName(paidBy)}
        </span>
      ),
    },
    {
      title: "Chia cho",
      dataIndex: "splitAmong",
      key: "splitAmong",
      render: (splitAmong: string[]) => (
        <Tooltip title={splitAmong.map(getDisplayName).join(", ")}>
          <span className="flex items-center">
            <TeamOutlined className="mr-1" /> {splitAmong.length} người
          </span>
        </Tooltip>
      ),
    },
    {
      title: "Hành động",
      key: "action",
      render: (_: any, record: { id: string }) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => onRemoveExpense(record.id)}
        />
      ),
    },
  ];

  return (
    <Card className="mb-4">
      <div className="flex justify-between items-center mb-4">
        <Title level={5} className="flex items-center m-0">
          <BankOutlined className="mr-2" /> Danh Sách Chi Phí
        </Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onAddExpense}
        >
          Thêm Chi Phí
        </Button>
      </div>

      {expenses.length > 0 ? (
        <Table
          dataSource={expenses}
          columns={columns}
          rowKey="id"
          pagination={false}
        />
      ) : (
        <Empty description="Chưa có chi phí nào được thêm" />
      )}
    </Card>
  );
}; 