import React, { useState, useEffect } from "react";
import { Modal, List, Input, Button, Avatar, Tooltip, Spin, message, Divider } from "antd";
import {
  UserOutlined,
  RobotOutlined,
  CheckCircleFilled,
  SendOutlined,
} from "@ant-design/icons";
import { createComment, getActivityComments, suggestComment } from "../../../../services/travelPlanApi";
import { ActivityComment } from "../../../../types/apiType";
import { TravelActivity } from "../../../../types/travelPlan";
import { AIActivitySuggestions } from "../AISuggestions";

interface Comment {
  comment_id: string;
  comment_message: string;
  user_id: string;
  user_name: string;
  created_at: string;
}

// AI suggestion type to match the response format
interface AISuggestion {
  activity_id: string;
  id: string;
  type: string;
  name: string;
  description: string;
  address?: string;
  price?: number;
  price_range?: string;
  price_ai_estimate?: number;
  rating?: number;
  image_url?: string;
  start_time?: string;
  end_time?: string;
}

interface AISuggestionResponse {
  message: string;
  data: {
    suggestion_list: AISuggestion[];
    suggestion_type: string;
  };
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
  activityType: string;
}> = ({ open, onClose, activityId, activityType }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [value, setValue] = useState("");
  const [aiMode, setAiMode] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState<number[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { TextArea } = Input;

  const getFakeUsername = (userId: string) => {
    const lastChar = userId.slice(-1);
    const index = parseInt(lastChar, 16) % FAKE_USERNAMES.length;
    return FAKE_USERNAMES[index];
  };

  useEffect(() => {
    if (open && activityId) {
      fetchComments();
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [open, activityId]);

  const fetchComments = async () => {
    if (!activityId) return;

    console.log(`Fetching comments for ${activityType} with ID: ${activityId}`);

    setLoading(true);
    try {
      const response = await getActivityComments(activityId, activityType);
      if (response.data && Array.isArray(response.data)) {
        const transformedComments: Comment[] = response.data.map((comment: any) => ({
          comment_id: comment.comment_id,
          comment_message: comment.comment_message,
          user_id: comment.user_id,
          user_name: getFakeUsername(comment.user_id),
          created_at: comment.created_at || new Date().toISOString() 
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

    console.log(`Adding comment to ${activityType} with ID: ${activityId}`);

    setSubmitting(true);
    try {
      await createComment(activityId, value.trim(), activityType);
      
      const newComment: Comment = {
        comment_id: `temp-${Date.now()}`,
        comment_message: value.trim(),
        user_id: "current-user", 
        user_name: "Bạn",
        created_at: new Date().toISOString()
      };
      
      setComments([...comments, newComment]);
      setValue("");
      
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
    setShowSuggestions(false);
  };

  const handleAICall = async () => {
    if (selectedIdx.length === 0 || aiLoading) return; 
    
    const selectedComments = selectedIdx.map((idx) => ({
      comment_id: comments[idx].comment_id,
      comment_message: comments[idx].comment_message
    }));
    
    console.log(
      "Selected comments:",
      selectedComments
    );

    setAiLoading(true);
    setSuggestions([]);
    setShowSuggestions(false);
    
    try {
      const url = window.location.pathname;
      const tripId = url.split('/trips/')[1] || 'default-trip-id';
      
      console.log('Extracted trip_id from URL:', tripId);
      
      const userInput = JSON.parse(localStorage.getItem(`userInput_${tripId}`) || '{}');
      
      const activity = {
        activity_id: activityId,
        id: activityId, 
        comments: selectedComments,
        type: activityType,
        name: "", 
        description: "",
        start_time: "",
        end_time: "",
        price_ai_estimate: 0
      };
      
      const travelPreference = {
        budget: {
          exact_budget: Number(userInput.budget?.exactBudget) || 0,
          type: userInput.budget?.type || 'moderate'
        },
        destination_id: userInput.destination || 'hanoi',
        people: userInput.people || {
          adults: 1,
          children: 0,
          infants: 0,
          pets: 0
        },
        personal_options: Array.isArray(userInput.personalOptions) ? userInput.personalOptions : [],
        travel_preference_id: 'leisure',
        travel_time: {
          end_date: userInput.travelTime?.endDate || new Date().toISOString().split('T')[0],
          start_date: userInput.travelTime?.startDate || new Date().toISOString().split('T')[0],
          type: userInput.travelTime?.type || 'exact'
        },
        trip_id: tripId 
      };
      
      const payload = {
        activity,
        travel_preference: travelPreference,
        user_input: value.trim() || undefined 
      };
      
      console.log('Sending payload to API:', JSON.stringify(payload));
      
      const response = await suggestComment(payload);
      console.log('AI suggestion response:', response);
      
      if (response && response.data && response.data.suggestion_list) {
        setSuggestions(response.data.suggestion_list);
        setShowSuggestions(true);
        message.success('Gợi ý đã được tạo thành công!');
      } else {
        message.info('Không có gợi ý phù hợp.');
      }
    } catch (error) {
      console.error('Error calling suggest comment API:', error);
      message.error('Không thể tạo gợi ý. Vui lòng thử lại sau.');
    } finally {
      setAiLoading(false);
      setAiMode(false);
      setSelectedIdx([]);
    }
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

  const handleAddSuggestion = (suggestion: AISuggestion | TravelActivity) => {
    console.log('Replacing current activity with:', suggestion);
    
    // Replace the current activity using the same ID
    const replacementActivity = {
      ...suggestion,
      // Ensure we keep the original activity ID
      activity_id: activityId,
      id: activityId
    };
    
    // Here you would add code to update the activity in the trip plan
    // This would typically involve a call to an API or a state update function
    
    message.success(`Đã thay thế bằng ${suggestion.name}`);
    
    // Close the modal after replacing
    onClose();
  };

  return (
    <Modal
      open={open}
      onCancel={() => {
        setAiMode(false);
        setSelectedIdx([]);
        setShowSuggestions(false);
        onClose();
      }}
      footer={null}
      title={showSuggestions ? "Gợi ý từ AI" : "Bình luận hoạt động"}
      centered
      width={showSuggestions ? 700 : 420}
      style={{ paddingTop: 16, paddingBottom: 8 }}
    >
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <Spin size="large" />
        </div>
      ) : (
        <>
          {!showSuggestions ? (
            // Comments section
            <>
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
                    disabled={selectedIdx.length === 0 || aiLoading}
                    loading={aiLoading}
                    onClick={handleAICall}
                  >
                    Xác nhận AI ({selectedIdx.length})
                  </Button>
                )}
              </div>
            </>
          ) : (
            // AI Suggestions section
            <>
              <p className="text-sm text-gray-500 mb-4">
                Dựa trên các bình luận bạn đã chọn, AI gợi ý những địa điểm sau:
              </p>
              
              <AIActivitySuggestions 
                suggestions={suggestions}
                loading={false}
                onSelectActivity={handleAddSuggestion}
              />
              
              <div className="flex justify-between mt-4">
                <Button 
                  onClick={() => setShowSuggestions(false)}
                >
                  Quay lại bình luận
                </Button>
                <Button 
                  type="primary"
                  onClick={onClose}
                >
                  Đóng
                </Button>
              </div>
            </>
          )}
        </>
      )}
    </Modal>
  );
};
