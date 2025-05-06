import React, { useState } from "react";
import { Modal, List, Input, Button, Avatar, Tooltip, Spin } from "antd";
import {
  UserOutlined,
  RobotOutlined,
  CheckCircleFilled,
} from "@ant-design/icons";

export const ActivityCommentModal: React.FC<{
  open: boolean;
  onClose: () => void;
  activityId: string;
}> = ({ open, onClose, activityId }) => {
  const [comments, setComments] = useState<{ user: string; text: string }[]>([
    { user: "Nguyễn Văn A", text: "Tui mun an chay!" },
    { user: "Trần Thị B", text: "Tui muốn bò vui vẻ." },
  ]);
  const [value, setValue] = useState("");
  const [aiMode, setAiMode] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState<number[]>([]);
  const [aiLoading, setAiLoading] = useState(false);

  const handleAdd = () => {
    if (value.trim()) {
      setComments([...comments, { user: "Bạn", text: value.trim() }]);
      setValue("");
    }
  };

  const handleAIMode = () => {
    setAiMode(true);
    setSelectedIdx([]);
  };

  const handleAICall = () => {
    // Log the selected comments
    console.log(
      "Selected comments:",
      selectedIdx.map((idx) => comments[idx])
    );

    setAiLoading(true);
    setTimeout(() => {
      setAiLoading(false);
      setAiMode(false);
      setSelectedIdx([]);
    }, 1500);
  };

  const handleSelect = (idx: number) => {
    setSelectedIdx((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]
    );
  };

  return (
    <Modal
      open={open}
      onCancel={() => {
        setAiMode(false);
        setSelectedIdx([]);
        onClose();
      }}
      footer={null}
      title="Bình luận hoạt động"
      centered
      width={420}
      style={{ paddingTop: 16, paddingBottom: 8 }}
    >
      <List
        dataSource={comments}
        locale={{ emptyText: "Chưa có bình luận nào" }}
        renderItem={(item, idx) => (
          <List.Item
            key={idx}
            style={
              aiMode
                ? {
                    background: selectedIdx.includes(idx)
                      ? "#e6f7ff"
                      : undefined,
                    cursor: "pointer",
                    borderRadius: "6px",
                    padding: "8px",
                    border: selectedIdx.includes(idx)
                      ? "1px solid #1890ff"
                      : "1px solid transparent",
                    transition: "all 0.2s",
                  }
                : {}
            }
            onClick={aiMode ? () => handleSelect(idx) : undefined}
            className={aiMode ? "hover:bg-gray-50" : ""}
          >
            {aiMode && selectedIdx.includes(idx) && (
              <div className="flex items-center mr-2">
                <CheckCircleFilled
                  style={{ color: "#1890ff", marginLeft: "4px" }}
                />
              </div>
            )}
            <List.Item.Meta
              avatar={<Avatar icon={<UserOutlined />} />}
              title={item.user}
              description={item.text}
            />
          </List.Item>
        )}
        style={{ marginBottom: 8, maxHeight: 180, overflowY: "auto" }}
      />
      <Input.TextArea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Viết bình luận..."
        autoSize={{ minRows: 1, maxRows: 3 }}
        onPressEnter={handleAdd}
        className="mb-2"
        disabled={aiMode}
      />
      <div className="flex justify-between items-center mt-2">
        <Button
          type="primary"
          size="small"
          onClick={handleAdd}
          disabled={!value.trim() || aiMode}
        >
          Gửi
        </Button>
        {!aiMode ? (
          <Button
            icon={<RobotOutlined />}
            size="small"
            type="dashed"
            onClick={handleAIMode}
          >
            Gọi AI
          </Button>
        ) : (
          <Button
            icon={aiLoading ? <Spin size="small" /> : <RobotOutlined />}
            size="small"
            type="primary"
            disabled={selectedIdx.length === 0}
            loading={aiLoading}
            onClick={handleAICall}
          >
            Xác nhận AI ({selectedIdx.length})
          </Button>
        )}
      </div>
    </Modal>
  );
};
