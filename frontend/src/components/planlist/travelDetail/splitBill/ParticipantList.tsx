import React, { useState } from "react";
import { Card, Typography, Button, Input, Space, Avatar, List, Tag } from "antd";
import {
  PlusOutlined,
  DeleteOutlined,
  UserOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { ParticipantListProps } from "../../../../types/splitBillTypes";
import { CURRENT_USER_ID } from "../../../../hooks/useSplitBill";

const { Title, Text } = Typography;

const getAvatarColor = (name: string): string => {
  const colors = [
    "#f56a00",
    "#7265e6",
    "#ffbf00",
    "#00a2ae",
    "#87d068",
    "#1890ff",
    "#722ed1",
    "#eb2f96",
  ];
  const index = name
    .split("")
    .reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
  return colors[index];
};

export const ParticipantList: React.FC<ParticipantListProps> = ({
  participants,
  onAddParticipant,
  onRemoveParticipant,
  getDisplayName,
}) => {
  const [newParticipant, setNewParticipant] = useState("");

  const handleAddParticipant = () => {
    if (newParticipant && !participants.includes(newParticipant)) {
      onAddParticipant(newParticipant);
      setNewParticipant("");
    }
  };

  return (
    <Card className="mb-4">
      <div className="flex justify-between items-center mb-4">
        <Title level={5} className="flex items-center m-0">
          <TeamOutlined className="mr-2" /> Danh Sách Bạn Bè
        </Title>
        <Text type="secondary">
          {participants.length} người tham gia
        </Text>
      </div>

      <div className="mb-4">
        <Input
          placeholder="Thêm bạn mới"
          value={newParticipant}
          onChange={(e) => setNewParticipant(e.target.value)}
          style={{ width: "100%" }}
          suffix={
            <Button
              type="text"
              icon={<PlusOutlined />}
              onClick={handleAddParticipant}
            />
          }
          onPressEnter={handleAddParticipant}
        />
      </div>

      <List
        dataSource={participants}
        renderItem={(participant) => (
          <List.Item
            key={participant}
            actions={[
              participant !== CURRENT_USER_ID && (
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => onRemoveParticipant(participant)}
                />
              ),
            ]}
          >
            <List.Item.Meta
              avatar={
                <Avatar
                  style={{
                    backgroundColor: getAvatarColor(participant),
                  }}
                >
                  {getDisplayName(participant).charAt(0).toUpperCase()}
                </Avatar>
              }
              title={
                <div>
                  {getDisplayName(participant)}
                  {participant === CURRENT_USER_ID && (
                    <Tag color="blue" className="ml-2">
                      Chính bạn
                    </Tag>
                  )}
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}; 