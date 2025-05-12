import React, { useState, useRef } from "react";
import { Card, Typography, List, Empty, Button, Input, Modal, Image, Divider } from "antd";
import { SwapRightOutlined, ArrowRightOutlined, QrcodeOutlined, FileTextOutlined, DownloadOutlined, ShareAltOutlined } from "@ant-design/icons";
import { SettlementSuggestionsProps } from "../../../../types/splitBillTypes";
import { CURRENT_USER_ID } from "../../../../hooks/useSplitBill";
import axios from "axios";
import html2canvas from 'html2canvas';

const { Title, Text } = Typography;

export const SettlementSuggestions: React.FC<SettlementSuggestionsProps> = ({
  settlements,
  getDisplayName,
}) => {
  const [qrModalVisible, setQrModalVisible] = useState(false);
  const [accountNumber, setAccountNumber] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const qrContentRef = useRef<HTMLDivElement>(null);

  const generateQrCode = async () => {
    if (!accountNumber) return;
    
    setLoading(true);
    try {
      const response = await axios.post('https://api.vietqr.io/v2/generate', {
        accountNo: accountNumber,
        accountName: "Vua du lịch", 
        acqId: "970415", 
        addInfo: "Thanh toán chi phí du lịch",
        amount: `${settlements.reduce((sum, s) => sum + s.amount, 0)}`,
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

  const captureAndDownload = async () => {
    if (qrContentRef.current) {
      try {
        // Apply explicit styles with standard colors before capturing
        const elements = qrContentRef.current.querySelectorAll('.bg-blue-100');
        elements.forEach(el => {
          (el as HTMLElement).style.backgroundColor = '#dbeafe'; // Standard hex for light blue
          (el as HTMLElement).style.color = '#1e40af'; // Standard hex for dark blue
        });
        
        const canvas = await html2canvas(qrContentRef.current, {
          backgroundColor: '#ffffff',
          logging: false,
          scale: 2, // Higher resolution
          useCORS: true
        });
        
        const image = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = image;
        link.download = 'thanh-toan-chi-phi.png';
        link.click();
      } catch (error) {
        console.error("Error capturing screenshot:", error);
        Modal.error({
          title: 'Không thể tải xuống',
          content: 'Có lỗi xảy ra khi tạo ảnh. Vui lòng thử lại hoặc chụp màn hình thủ công.',
        });
      }
    }
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
      <div className="flex justify-between items-center mb-4">
        <Title level={5} className="m-0">Đề Xuất Thanh Toán</Title>
        <Button 
          type="primary" 
          icon={<QrcodeOutlined />} 
          onClick={() => setQrModalVisible(true)}
        >
          Tạo QR
        </Button>
      </div>
      <Text type="secondary" className="mb-4 block">
        Đây là cách hiệu quả nhất để giải quyết các khoản nợ trong nhóm
      </Text>
      <List
        itemLayout="horizontal"
        dataSource={settlements}
        renderItem={(settlement, index) => (
          <List.Item>
            <div className="flex items-center">
              <div 
                className="flex items-center justify-center mr-3 rounded-full"
                style={{ 
                  backgroundColor: '#dbeafe', 
                  color: '#1e40af',
                  width: '32px',
                  height: '32px' 
                }}
              >
                {index + 1}
              </div>
              <div>
                <span className="font-medium">{getDisplayName(settlement.from)}</span>{" "}
                {settlement.to === CURRENT_USER_ID ? (
                  <ArrowRightOutlined className="mx-2" style={{ color: '#16a34a' }} />
                ) : settlement.from === CURRENT_USER_ID ? (
                  <ArrowRightOutlined className="mx-2" style={{ color: '#dc2626' }} />
                ) : (
                  <SwapRightOutlined className="mx-2" style={{ color: '#9ca3af' }} />
                )}{" "}
                <span className="font-medium">{getDisplayName(settlement.to)}</span>
              </div>
            </div>
            <div className="font-bold text-lg">
              {settlement.amount.toLocaleString("vi-VN")}₫
            </div>
          </List.Item>
        )}
      />

      <Modal
        title="Chia sẻ thanh toán"
        open={qrModalVisible}
        onCancel={() => {
          setQrModalVisible(false);
          setQrCodeUrl("");
          setAccountNumber("");
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setQrModalVisible(false);
            setQrCodeUrl("");
            setAccountNumber("");
          }}>
            Đóng
          </Button>,
          !qrCodeUrl ? (
            <Button 
              key="generate" 
              type="primary" 
              onClick={generateQrCode}
              loading={loading}
              disabled={!accountNumber}
            >
              Tạo mã QR
            </Button>
          ) : (
            <Button 
              key="share" 
              type="primary" 
              icon={<DownloadOutlined />}
              onClick={captureAndDownload}
            >
              Tải xuống
            </Button>
          )
        ]}
        width={600}
      >
        {!qrCodeUrl ? (
          <div className="mb-4">
            <Text>Nhập số tài khoản ngân hàng của bạn:</Text>
            <Input 
              className="mt-2"
              placeholder="Nhập số tài khoản" 
              value={accountNumber}
              onChange={(e) => setAccountNumber(e.target.value)}
            />
          </div>
        ) : (
          <div ref={qrContentRef} className="p-4 bg-white">
            <div className="text-center mb-4">
              <Image src={qrCodeUrl} alt="QR Code" style={{ maxWidth: 200, margin: '0 auto' }} preview={false} />
              <Text className="block mt-2 font-medium">Quét mã QR để chuyển khoản</Text>
              <Text type="secondary" className="block mt-1">
                Tổng số tiền: {settlements.reduce((sum, s) => sum + s.amount, 0).toLocaleString("vi-VN")}₫
              </Text>
            </div>
            
            <Divider style={{ borderColor: '#e5e7eb' }} />
            
            <Title level={5} className="mb-3">Danh sách thanh toán</Title>
            {settlements.map((settlement, index) => (
              <div key={index} className="flex justify-between items-center py-2" style={{ borderBottom: index < settlements.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
                <div className="flex items-center">
                  <div 
                    className="flex items-center justify-center mr-2 text-xs rounded-full"
                    style={{ 
                      backgroundColor: '#dbeafe', 
                      color: '#1e40af',
                      width: '24px',
                      height: '24px' 
                    }}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <span className="font-medium">{getDisplayName(settlement.from)}</span>{" "}
                    <ArrowRightOutlined className="mx-1" style={{ color: '#9ca3af' }} />{" "}
                    <span className="font-medium">{getDisplayName(settlement.to)}</span>
                  </div>
                </div>
                <div className="font-bold">
                  {settlement.amount.toLocaleString("vi-VN")}₫
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </Card>
  );
}; 