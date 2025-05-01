import React from "react";
import { Button, Table, Typography, message } from "antd";
import { ExportOutlined } from "@ant-design/icons";
import { TravelDetailData } from "../../../types/travelPlan";
import * as XLSX from "xlsx";

const { Title } = Typography;

interface SheetExportProps {
  travelDetail: TravelDetailData;
}

export const SheetExport: React.FC<SheetExportProps> = ({ travelDetail }) => {
  const data = travelDetail.days.flatMap((day) =>
    day.activities.map((activity, idx) => ({
      key: `${day.day}-${idx}`,
      day: day.day,
      date: day.date.toLocaleDateString("vi-VN"),
      time: activity.time,
      type: activity.type,
      name: activity.name,
      location: activity.location,
      description: activity.description,
      price: activity.price ?? "",
    }))
  );

  const columns = [
    { title: "Ngày", dataIndex: "day", key: "day" },
    { title: "Ngày tháng", dataIndex: "date", key: "date" },
    { title: "Thời gian", dataIndex: "time", key: "time" },
    { title: "Loại", dataIndex: "type", key: "type" },
    { title: "Tên hoạt động", dataIndex: "name", key: "name" },
    { title: "Địa điểm", dataIndex: "location", key: "location" },
    { title: "Mô tả", dataIndex: "description", key: "description" },
    { title: "Giá", dataIndex: "price", key: "price" },
  ];

  const handleExport = () => {
    const wsData = [
      columns.map((col) => col.title),
      ...data.map((row) =>
        columns.map((col) => row[col.dataIndex as keyof typeof row])
      ),
    ];

    const ws = XLSX.utils.aoa_to_sheet(wsData);

    ws["!cols"] = [
      { wch: 6 },
      { wch: 14 },
      { wch: 14 },
      { wch: 12 },
      { wch: 24 },
      { wch: 24 },
      { wch: 32 },
      { wch: 16 },
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Lịch trình");

    XLSX.writeFile(wb, `lich-trinh-${travelDetail.destination}.xlsx`);
    message.success(
      "Đã xuất file Excel. Mở bằng Excel hoặc Google Sheets để xem định dạng đẹp!"
    );
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <Title level={4}>Xuất lịch trình sang Google Sheets</Title>
        <Button
          icon={<ExportOutlined />}
          type="primary"
          className="!bg-black"
          onClick={handleExport}
        >
          Xuất file Excel
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={data}
        pagination={false}
        bordered
        size="small"
        scroll={{ x: true }}
      />
      <div className="mt-2 text-gray-500 text-sm">
        * Sau khi tải file Excel, bạn có thể mở hoặc nhập vào Google Sheets để
        chỉnh sửa hoặc chia sẻ.
      </div>
    </div>
  );
};
