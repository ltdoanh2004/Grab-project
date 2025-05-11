import React, { useState, useEffect } from "react";
import { Modal, List, Input, Button, Avatar, Tooltip, Spin, message } from "antd";
import {
  UserOutlined,
  RobotOutlined,
  CheckCircleFilled,
  SendOutlined,
} from "@ant-design/icons";
import { createComment, getActivityComments } from "../../../../services/travelPlanApi";
import { ActivityComment } from "../../../../types/apiType";

interface Comment {
  comment_id: string;
  comment_message: string;
  user_id: string;
  user_name: string;
  created_at: string;
}

// Fake usernames to display
const FAKE_USERNAMES = [
  'Nguyễn Văn A',
  'Trần Thị B',
  'Lê Hoàng C',
  'Phạm Minh D',
  'Vũ Thành E',
  'Đỗ Hương F',
  'Hoàng Lan G',
  'Đinh Tuấn H',
];

export const ActivityCommentModal: React.FC<{
  open: boolean;
  onClose: () => void;
  activityId: string;
  activityType: string; // Add activity type prop
}> = ({ open, onClose, activityId, activityType }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [value, setValue] = useState("");
  const [aiMode, setAiMode] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState<number[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { TextArea } = Input;

  // Get a random fake username based on user ID to keep consistent names
  const getFakeUsername = (userId: string) => {
    // Use the last character of the user ID to select a username
    const lastChar = userId.slice(-1);
    const index = parseInt(lastChar, 16) % FAKE_USERNAMES.length;
    return FAKE_USERNAMES[index];
  };

  useEffect(() => {
    if (open && activityId) {
      fetchComments();
    }
  }, [open, activityId]);

  const fetchComments = async () => {
    if (!activityId) return;

    // Log the activity ID for debugging
    console.log(`Fetching comments for ${activityType} with ID: ${activityId}`);

    setLoading(true);
    try {
      const response = await getActivityComments(activityId, activityType);
      if (response.data && Array.isArray(response.data)) {
        // Transform the API response to match our Comment interface
        const transformedComments: Comment[] = response.data.map((comment: any) => ({
          comment_id: comment.comment_id,
          comment_message: comment.comment_message,
          user_id: comment.user_id,
          user_name: getFakeUsername(comment.user_id),
          created_at: comment.created_at || new Date().toISOString() // Use API timestamp if available
        }));
        setComments(transformedComments);
      }
    } catch (error) {
      console.error("Error fetching comments:", error);
      message.error("Không thể tải bình luận. Vui lòng thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!value.trim()) return;

    // Log the activity ID for debugging
    console.log(`Adding comment to ${activityType} with ID: ${activityId}`);

    setSubmitting(true);
    try {
      // Pass the correct activity type
      await createComment(activityId, value.trim(), activityType);
      
      // Optimistically add the comment to the UI
      const newComment: Comment = {
        comment_id: `temp-${Date.now()}`,
        comment_message: value.trim(),
        user_id: "current-user", 
        user_name: "Bạn",
        created_at: new Date().toISOString()
      };
      
      setComments([...comments, newComment]);
      setValue("");
      
      // Refresh comments from server to get the proper IDs
      fetchComments();
    } catch (error) {
      console.error("Error adding comment:", error);
      message.error("Không thể gửi bình luận. Vui lòng thử lại sau.");
    } finally {
      setSubmitting(false);
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

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('vi-VN', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return '';
    }
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
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <Spin size="large" />
        </div>
      ) : (
        <List
          dataSource={comments}
          locale={{ emptyText: "Chưa có bình luận nào" }}
          renderItem={(item, idx) => (
            <List.Item
              key={item.comment_id}
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
                title={
                  <div className="flex justify-between">
                    <span>{item.user_name || 'Người dùng'}</span>
                    <span className="text-xs text-gray-400">{formatDate(item.created_at)}</span>
                  </div>
                }
                description={item.comment_message}
              />
            </List.Item>
          )}
          style={{ marginBottom: 8, maxHeight: 180, overflowY: "auto" }}
        />
      )}
      
      <TextArea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Viết bình luận..."
        autoSize={{ minRows: 1, maxRows: 3 }}
        onPressEnter={(e) => {
          e.preventDefault();
          if (!submitting) handleAdd();
        }}
        className="mb-2"
        disabled={aiMode || submitting}
      />
      <div className="flex justify-between items-center mt-2">
        <Button
          type="primary"
          icon={<SendOutlined />}
          size="small"
          onClick={handleAdd}
          loading={submitting}
          disabled={!value.trim() || aiMode || submitting}
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
