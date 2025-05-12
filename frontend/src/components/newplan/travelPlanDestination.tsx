import React, { useState, useRef, useEffect } from "react";
import { Card, Typography, Input, Rate, List, Avatar, Empty, Carousel } from "antd";
import { SearchOutlined, LeftOutlined, RightOutlined } from "@ant-design/icons";
import { DESTINATIONS } from "../../constants/travelPlanConstants";

const { Title, Text } = Typography;

interface DestinationStepProps {
  selectedDestination: string | null;
  onSelectDestination: (destId: string) => void;
  onStartPlan: () => void;
}

// Slideshow data with images and descriptions
const slideshowData = [
  {
    image: "/slideshow/plan.jpg",
    title: "Lên kế hoạch du lịch dễ dàng",
    description: "Thêm các tùy chọn cá nhân và sở thích để tạo lịch trình phù hợp với bạn"
  },
  {
    image: "/slideshow/personalOptions.jpg",
    title: "Tùy chỉnh lịch trình thông minh",
    description: "Lịch trình được tạo bởi AI thông minh, phù hợp với nhu cầu và ngân sách của bạn"
  },
  {
    image: "/slideshow/share.png",
    title: "Chia sẻ với bạn bè",
    description: "Dễ dàng chia sẻ lịch trình với bạn bè và gia đình để cùng lên kế hoạch"
  },
  {
    image: "/slideshow/splitBill.png",
    title: "Chia sẻ chi phí thông minh",
    description: "Tính toán và chia hóa đơn công bằng sau mỗi chuyến đi"
  }
];

export const DestinationStep: React.FC<DestinationStepProps> = ({
  selectedDestination,
  onSelectDestination,
  onStartPlan,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showSearchResults, setShowSearchResults] = useState(false);
  const searchInputRef = useRef<HTMLDivElement>(null);
  const searchResultsRef = useRef<HTMLDivElement>(null);
  const carouselRef = useRef<any>(null);
  const [currentSlide, setCurrentSlide] = useState(0);

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

  // Auto-advance slideshow
  useEffect(() => {
    const interval = setInterval(() => {
      if (carouselRef.current) {
        const nextSlide = (currentSlide + 1) % slideshowData.length;
        carouselRef.current.goTo(nextSlide);
        setCurrentSlide(nextSlide);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [currentSlide]);

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

  const nextSlide = () => {
    if (carouselRef.current) {
      const nextSlideIndex = (currentSlide + 1) % slideshowData.length;
      carouselRef.current.goTo(nextSlideIndex);
      setCurrentSlide(nextSlideIndex);
    }
  };

  const prevSlide = () => {
    if (carouselRef.current) {
      const prevSlideIndex = (currentSlide - 1 + slideshowData.length) % slideshowData.length;
      carouselRef.current.goTo(prevSlideIndex);
      setCurrentSlide(prevSlideIndex);
    }
  };

  return (
    <div className="p-8 font-inter">
      <div className="mb-20 relative rounded-2xl overflow-hidden shadow-xl h-[500px]">
        <Carousel
          ref={carouselRef}
          autoplay={false}
          effect="fade"
          dots={false}
          beforeChange={(_, to) => setCurrentSlide(to)}
          className="h-full"
        >
          {slideshowData.map((slide, index) => (
            <div key={index} className="h-[500px]">
              <div 
                className="w-full h-full bg-cover bg-center relative before:content-[''] before:absolute before:inset-0 before:bg-gradient-to-b before:from-black/60 before:via-black/40 before:to-black/30"
                style={{ backgroundImage: `url(${slide.image})` }}
              >
                <div className="absolute inset-0 flex flex-col justify-center items-center text-center p-8 z-10">
                  <h2 className="text-white text-4xl font-bold mb-4">{slide.title}</h2>
                  <p className="text-gray-100 text-xl max-w-2xl mb-12">{slide.description}</p>
                </div>
              </div>
            </div>
          ))}
        </Carousel>

        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 z-20">
          <button 
            onClick={prevSlide} 
            className="bg-white/30 cursor-pointer hover:bg-white/50 transition-colors p-3 rounded-full text-white"
          >
            <LeftOutlined className="text-xl" />
          </button>
        </div>

        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 z-20">
          <button 
            onClick={nextSlide} 
            className="bg-white/30 cursor-pointer hover:bg-white/50 transition-colors p-3 rounded-full text-white"
          >
            <RightOutlined className="text-xl" />
          </button>
        </div>

        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20 flex gap-2">
          {slideshowData.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                carouselRef.current?.goTo(index);
                setCurrentSlide(index);
              }}
              className={`w-3 h-3 rounded-full ${
                currentSlide === index ? "bg-white" : "bg-white/50"
              }`}
            />
          ))}
        </div>

        <div className="absolute bottom-16 left-0 right-0 z-30">
          <div className="relative z-20 max-w-xl mx-auto">
            <div className="relative" ref={searchInputRef}>
              <Input
                placeholder="Tìm kiếm điểm đến"
                className="w-full shadow-lg rounded-full py-4 px-6 text-lg"
                size="large"
                prefix={<SearchOutlined className="ml-2 text-xl" />}
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
