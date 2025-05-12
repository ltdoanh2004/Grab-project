import React, { useState, useRef, useEffect } from "react";
import { Card, Typography, Input, Rate, List, Avatar, Empty } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { DESTINATIONS } from "../../constants/travelPlanConstants";

const { Title, Text } = Typography;

interface DestinationStepProps {
  selectedDestination: string | null;
  onSelectDestination: (destId: string) => void;
  onStartPlan: () => void;
}

export const DestinationStep: React.FC<DestinationStepProps> = ({
  selectedDestination,
  onSelectDestination,
  onStartPlan,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showSearchResults, setShowSearchResults] = useState(false);
  const searchInputRef = useRef<HTMLDivElement>(null);
  const searchResultsRef = useRef<HTMLDivElement>(null);

  // Handle click outside to close search results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchResultsRef.current && 
        searchInputRef.current && 
        !searchResultsRef.current.contains(event.target as Node) &&
        !searchInputRef.current.contains(event.target as Node)
      ) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleCardClick = (destId: string) => {
    onSelectDestination(destId);
    onStartPlan();
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setShowSearchResults(value.length > 0);
  };

  const handleSelectSearchResult = (destId: string) => {
    setSearchTerm("");
    setShowSearchResults(false);
    onSelectDestination(destId);
    onStartPlan();
  };

  const filteredDestinations = DESTINATIONS.filter(
    (dest) =>
      dest.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      dest.country.toLowerCase().includes(searchTerm.toLowerCase()) ||
      dest.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 font-inter">
      <div
        className="mb-16 relative rounded-2xl overflow-hidden
  bg-[url('/hinhnen.jpg')] bg-cover bg-center p-12 pb-24 shadow-lg before:content-[''] before:absolute before:inset-0
   before:bg-gradient-to-b before:from-black/50 before:via-black/30 before:to-black/20 after:content-[''] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-20 after:bg-gradient-to-t after:from-white after:to-transparent after:blur-sm"
      >
        <div className="relative z-10 text-center">
          <p className="mb-4 font-semibold text-white text-3xl">
            Trước tiên, bạn muốn đi đâu?
          </p>
          <p className="text-gray-200 font-extralight mb-8 text-sm">
            Bạn sẽ nhận được các gợi ý cá nhân hóa mà bạn có thể lưu lại và biến
            thành lịch trình du lịch của riêng bạn.
          </p>

          <div className="relative z-20 max-w-xl mx-auto transform translate-y-12">
            <div className="relative" ref={searchInputRef}>
              <Input
                placeholder="Tìm kiếm điểm đến"
                className="w-full shadow-lg rounded-full py-3"
                size="large"
                prefix={<SearchOutlined className="ml-2" />}
                value={searchTerm}
                onChange={handleSearchChange}
                onClick={() => setShowSearchResults(searchTerm.length > 0)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Search results dropdown positioned absolutely in the document */}
      {showSearchResults && searchInputRef.current && (
        <div 
          ref={searchResultsRef}
          className="fixed bg-white rounded-lg shadow-2xl z-[9999] max-h-96 overflow-y-auto w-full max-w-xl"
          style={{
            top: searchInputRef.current.getBoundingClientRect().bottom + window.scrollY + 8,
            left: '50%',
            transform: 'translateX(-50%)'
          }}
        >
          {filteredDestinations.length > 0 ? (
            <List
              dataSource={filteredDestinations}
              renderItem={(dest) => (
                <List.Item 
                  className="cursor-pointer hover:bg-gray-50 transition-colors px-4"
                  onClick={() => handleSelectSearchResult(dest.id)}
                >
                  <List.Item.Meta
                    avatar={<Avatar src={dest.imageUrl} size="large" />}
                    title={<span className="font-medium">{dest.name}</span>}
                    description={dest.description}
                  />
                  <div className="flex items-center">
                    <Rate value={dest.rating} disabled allowHalf className="text-xs" />
                    <span className="ml-2 text-gray-500 text-sm">{dest.rating}</span>
                  </div>
                </List.Item>
              )}
            />
          ) : (
            <Empty
              description="Không tìm thấy điểm đến"
              className="py-4"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          )}
        </div>
      )}

      <div className="flex justify-center flex-col mb-16">
        <p className="text-center font-semibold text-xl mb-4">
          Khám phá địa điểm phổ biến
        </p>
        <div className="grid lg:grid-cols-2 gap-6">
          {DESTINATIONS.map((dest) => (
            <Card
              key={dest.id}
              hoverable
              className={`cursor-pointer ${
                selectedDestination === dest.id
                  ? "border-2 border-blue-500"
                  : ""
              }`}
              onClick={() => handleCardClick(dest.id)}
            >
              <div className="flex items-center">
                <img
                  src={dest.imageUrl}
                  alt={dest.name}
                  className="w-16 h-16 mr-4"
                />
                <div className="flex-1">
                  <div className="flex justify-between items-center">
                    <Title level={4} className="mb-0">
                      {dest.name}
                    </Title>
                    <div className="flex items-center">
                      <Rate defaultValue={dest.rating} disabled allowHalf />
                      <span className="ml-2 text-gray-500">{dest.rating}</span>
                    </div>
                  </div>
                  <Text className="text-gray-600">{dest.description}</Text>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
      <div className="flex justify-center flex-col">
        <p className="text-center font-semibold text-xl mb-4">
          Quay lại với những địa điểm đã chọn
        </p>
        <div className="flex flex-row justify-center gap-4">
          {DESTINATIONS.map((dest) => (
            <Card
              key={dest.id}
              hoverable
              className={`cursor-pointer ${
                selectedDestination === dest.id
                  ? "border-2 border-blue-500"
                  : ""
              }`}
              onClick={() => handleCardClick(dest.id)}
            >
              <div className="flex flex-col">
                <img
                  src={dest.imageUrl}
                  alt={dest.name}
                  className="w-fit h-fit"
                />
                <div className="flex-1 mt-2">
                  <p className="mb-0">{dest.name}</p>
                  <Rate defaultValue={dest.rating} disabled allowHalf />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
