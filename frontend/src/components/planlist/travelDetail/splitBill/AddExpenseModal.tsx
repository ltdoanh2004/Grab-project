import React, { useState, useEffect } from "react";
import {
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Row,
  Col,
  DatePicker,
  Radio,
  Space,
  Typography,
  Divider,
} from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { AddExpenseModalProps, Expense } from "../../../../types/splitBillTypes";
import dayjs from "dayjs";

const { Option } = Select;
const { Text } = Typography;

export const AddExpenseModal: React.FC<AddExpenseModalProps> = ({
  visible,
  onClose,
  onAddExpense,
  participants,
  expenseCategories,
  getDisplayName,
}) => {
  const [form] = Form.useForm();
  const [splitType, setSplitType] = useState<"equal" | "custom">("equal");
  const [totalAmount, setTotalAmount] = useState<number>(0);
  const [customAmounts, setCustomAmounts] = useState<Record<string, number>>({});
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>(participants);

  // Reset the form and state when the modal visibility changes
  useEffect(() => {
    if (visible) {
      setSplitType("equal");
      setTotalAmount(0);
      setCustomAmounts({});
      setSelectedParticipants(participants);
      
      // Initialize all participants with 0 amount
      const initialAmounts: Record<string, number> = {};
      participants.forEach(p => {
        initialAmounts[p] = 0;
      });
      setCustomAmounts(initialAmounts);
    }
  }, [visible, participants]);

  // Update selected participants when splitAmong changes
  const handleSplitAmongChange = (value: string[]) => {
    setSelectedParticipants(value);
    
    // If switching participants in custom mode, update custom amounts
    if (splitType === "custom") {
      const newCustomAmounts = { ...customAmounts };
      participants.forEach(p => {
        if (!value.includes(p)) {
          newCustomAmounts[p] = 0;
        } else if (newCustomAmounts[p] === undefined) {
          newCustomAmounts[p] = 0;
        }
      });
      setCustomAmounts(newCustomAmounts);
    }
  };

  const handleTotalAmountChange = (value: number | null) => {
    const amount = value || 0;
    setTotalAmount(amount);
    
    // If in equal split mode, update form values
    if (splitType === "equal" && selectedParticipants.length > 0) {
      const perPersonAmount = Math.round(amount / selectedParticipants.length);
      
      // Initialize equal amounts for all participants
      const newCustomAmounts: Record<string, number> = {};
      participants.forEach(p => {
        newCustomAmounts[p] = selectedParticipants.includes(p) ? perPersonAmount : 0;
      });
      setCustomAmounts(newCustomAmounts);
    }
  };

  const handleCustomAmountChange = (participant: string, value: number | null) => {
    const amount = value || 0;
    setCustomAmounts({
      ...customAmounts,
      [participant]: amount,
    });
  };

  // Calculate the sum of all custom amounts
  const calculateCustomTotal = (): number => {
    return Object.values(customAmounts).reduce((sum, amount) => sum + (amount || 0), 0);
  };

  // Validate if the custom amounts sum matches the total expense
  const validateCustomAmounts = (): boolean => {
    const customTotal = calculateCustomTotal();
    return Math.abs(customTotal - totalAmount) < 10; // Allow for small rounding discrepancies
  };

  const handleSubmit = () => {
    form.validateFields().then((values) => {
      // Create split data based on the split type
      let finalSplitAmong = values.splitAmong;
      let customSplitData: Record<string, number> | undefined = undefined;
      
      if (splitType === "custom") {
        if (!validateCustomAmounts()) {
          // Show an error if the amounts don't match
          return;
        }
        
        // Only include participants with amounts > 0
        finalSplitAmong = selectedParticipants.filter(p => customAmounts[p] > 0);
        
        // Create custom split data object
        customSplitData = { ...customAmounts };
      }

      const newExpense: Omit<Expense, "id"> = {
        description: values.description,
        amount: values.amount,
        paidBy: values.paidBy,
        splitAmong: finalSplitAmong,
        category: values.category,
        date: values.date ? values.date.format("YYYY-MM-DD") : new Date().toISOString().split("T")[0],
        customSplitData, // Add the custom split data if it exists
      };
      
      onAddExpense(newExpense);
      form.resetFields();
      onClose();
    });
  };

  // Get the remaining difference between total and sum of custom amounts
  const getRemainingAmount = (): number => {
    return totalAmount - calculateCustomTotal();
  };

  return (
    <Modal
      title="Thêm Chi Phí Mới"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="back" onClick={onClose}>
          Hủy
        </Button>,
        <Button
          key="submit"
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleSubmit}
          disabled={splitType === "custom" && !validateCustomAmounts()}
        >
          Thêm Chi Phí
        </Button>,
      ]}
      width={700}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          paidBy: participants[0], // Default to current user
          splitAmong: participants,
          category: "Ăn uống",
          date: dayjs(),
          splitType: "equal",
        }}
      >
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="description"
              label="Mô tả"
              rules={[{ required: true, message: "Vui lòng nhập mô tả" }]}
            >
              <Input placeholder="Ví dụ: Bữa tối tại nhà hàng" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="amount"
              label="Số tiền"
              rules={[{ required: true, message: "Vui lòng nhập số tiền" }]}
            >
              <InputNumber
                prefix="₫"
                min={0}
                step={1000}
                precision={0}
                style={{ width: "100%" }}
                placeholder="0"
                formatter={(value) =>
                  `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
                }
                onChange={handleTotalAmountChange}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="date"
              label="Ngày"
              rules={[{ required: true, message: "Vui lòng chọn ngày" }]}
            >
              <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="paidBy"
              label="Người trả tiền"
              rules={[
                { required: true, message: "Vui lòng chọn người trả tiền" },
              ]}
            >
              <Select placeholder="Chọn người trả tiền">
                {participants.map((participant) => (
                  <Option key={participant} value={participant}>
                    {getDisplayName(participant)}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="category"
              label="Loại chi phí"
              rules={[
                { required: true, message: "Vui lòng chọn loại chi phí" },
              ]}
            >
              <Select placeholder="Chọn loại chi phí">
                {expenseCategories.map((category) => (
                  <Option key={category} value={category}>
                    {category}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="splitAmong"
              label="Chia giữa"
              rules={[
                {
                  required: true,
                  message: "Vui lòng chọn người cùng chia",
                },
              ]}
            >
              <Select
                mode="multiple"
                placeholder="Chọn người cùng chia"
                style={{ width: "100%" }}
                onChange={handleSplitAmongChange}
              >
                {participants.map((participant) => (
                  <Option key={participant} value={participant}>
                    {getDisplayName(participant)}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="splitType"
              label="Cách chia"
            >
              <Radio.Group 
                onChange={e => setSplitType(e.target.value)} 
                value={splitType}
              >
                <Radio value="equal">Chia đều</Radio>
                <Radio value="custom">Chia chi tiết</Radio>
              </Radio.Group>
            </Form.Item>
          </Col>
        </Row>

        {splitType === "custom" && selectedParticipants.length > 0 && totalAmount > 0 && (
          <>
            <Divider orientation="left">Chi tiết số tiền</Divider>
            
            <div className="mb-2">
              <Space direction="horizontal">
                <Text>Tổng số tiền: {totalAmount.toLocaleString("vi-VN")}₫</Text>
                <Text>Đã chia: {calculateCustomTotal().toLocaleString("vi-VN")}₫</Text>
                <Text type={validateCustomAmounts() ? "success" : "danger"}>
                  Còn lại: {getRemainingAmount().toLocaleString("vi-VN")}₫
                </Text>
              </Space>
            </div>
            
            <Row gutter={[16, 16]}>
              {selectedParticipants.map(participant => (
                <Col span={12} key={participant}>
                  <Form.Item label={getDisplayName(participant)}>
                    <InputNumber
                      prefix="₫"
                      min={0}
                      step={1000}
                      precision={0}
                      style={{ width: "100%" }}
                      value={customAmounts[participant] || 0}
                      formatter={(value) =>
                        `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
                      }
                      onChange={(value) => handleCustomAmountChange(participant, value)}
                    />
                  </Form.Item>
                </Col>
              ))}
            </Row>
          </>
        )}
      </Form>
    </Modal>
  );
}; 