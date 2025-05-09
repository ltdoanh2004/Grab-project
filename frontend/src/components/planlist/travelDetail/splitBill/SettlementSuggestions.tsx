import React, { useState } from "react";
import { Card, Typography, List, Empty, Button, Input, Modal, Image } from "antd";
import { SwapRightOutlined, ArrowRightOutlined, QrcodeOutlined } from "@ant-design/icons";
import { SettlementSuggestionsProps } from "../../../../types/splitBillTypes";
import { CURRENT_USER_ID } from "../../../../hooks/useSplitBill";
import axios from "axios";

const { Title, Text } = Typography;

export const SettlementSuggestions: React.FC<SettlementSuggestionsProps> = ({
  settlements,
  getDisplayName,
}) => {
  const [qrModalVisible, setQrModalVisible] = useState(false);
  const [selectedSettlement, setSelectedSettlement] = useState<{from: string, to: string, amount: number} | null>(null);
  const [accountNumber, setAccountNumber] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const generateQrCode = async () => {
    if (!selectedSettlement || !accountNumber) return;
    
    setLoading(true);
    try {
      const response = await axios.post('https://api.vietqr.io/v2/generate', {
        accountNo: accountNumber,
        accountName: "Vua du lịch", // Default account name
        acqId: "970415", // Default bank ID for Vietcombank
        addInfo: `${getDisplayName(selectedSettlement.from)} thanh toán tiền du lịch ${getDisplayName(selectedSettlement.to)}`,
        amount: `${selectedSettlement.amount}`,
        template: "print"
      }, {
        headers: {
          'x-client-id': '148d00b1-2d9f-43db-9ec0-de4e8a1dd8b6',
          'x-api-key': '9a45a49f-2b4c-4b76-adbe-bcdaec019460',
          'Content-Type': 'application/json'
        }
      });
      
      setQrCodeUrl(response.data.data.qrDataURL);
    } catch (error) {
      console.error("Error generating QR code:", error);
    } finally {
      setLoading(false);
    }
  };

  const showQrModal = (settlement: {from: string, to: string, amount: number}) => {
    setSelectedSettlement(settlement);
    setQrModalVisible(true);
  };

  if (settlements.length === 0) {
    return (
      <Card className="mb-4">
        <Title level={5}>Đề Xuất Thanh Toán</Title>
        <Empty description="Không có đề xuất thanh toán" />
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <Title level={5}>Đề Xuất Thanh Toán</Title>
      <Text type="secondary" className="mb-4 block">
        Đây là cách hiệu quả nhất để giải quyết các khoản nợ trong nhóm
      </Text>
      <List
        itemLayout="horizontal"
        dataSource={settlements}
        renderItem={(settlement, index) => (
          <List.Item
            actions={[
              <Button 
                type="primary" 
                icon={<QrcodeOutlined />} 
                onClick={() => showQrModal(settlement)}
                size="small"
              >
                Tạo QR
              </Button>
            ]}
          >
            <div className="flex items-center w-full justify-between">
              <div className="flex items-center">
                <div className="bg-blue-100 text-blue-800 rounded-full h-8 w-8 flex items-center justify-center mr-3">
                  {index + 1}
                </div>
                <div>
                  <span className="font-medium">{getDisplayName(settlement.from)}</span>{" "}
                  {settlement.to === CURRENT_USER_ID ? (
                    <ArrowRightOutlined className="mx-2 text-green-600" />
                  ) : settlement.from === CURRENT_USER_ID ? (
                    <ArrowRightOutlined className="mx-2 text-red-600" />
                  ) : (
                    <SwapRightOutlined className="mx-2 text-gray-400" />
                  )}{" "}
                  <span className="font-medium">{getDisplayName(settlement.to)}</span>
                </div>
              </div>
              <div className="font-bold text-lg">
                {settlement.amount.toLocaleString("vi-VN")}₫
              </div>
            </div>
          </List.Item>
        )}
      />

      <Modal
        title="Tạo mã QR thanh toán"
        open={qrModalVisible}
        onCancel={() => setQrModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setQrModalVisible(false)}>
            Đóng
          </Button>,
          <Button 
            key="generate" 
            type="primary" 
            onClick={generateQrCode}
            loading={loading}
            disabled={!accountNumber}
          >
            Tạo mã QR
          </Button>
        ]}
      >
        {selectedSettlement && (
          <div>
            <div className="mb-4">
              <Text>
                <strong>{getDisplayName(selectedSettlement.from)}</strong> cần thanh toán{" "}
                <strong>{selectedSettlement.amount.toLocaleString("vi-VN")}₫</strong> cho{" "}
                <strong>{getDisplayName(selectedSettlement.to)}</strong>
              </Text>
            </div>
            
            <div className="mb-4">
              <Text>Nhập số tài khoản ngân hàng của bạn:</Text>
              <Input 
                className="mt-2"
                placeholder="Nhập số tài khoản" 
                value={accountNumber}
                onChange={(e) => setAccountNumber(e.target.value)}
              />
            </div>

            {qrCodeUrl && (
              <div className="text-center">
                <Image src={qrCodeUrl} alt="QR Code" style={{ maxWidth: 200, margin: '0 auto' }} />
                <Text className="block mt-2">Quét mã QR để chuyển khoản</Text>
              </div>
            )}
          </div>
        )}
      </Modal>
    </Card>
  );
}; 