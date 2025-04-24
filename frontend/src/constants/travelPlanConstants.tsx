// ================= IMPORTS =================
import { List, Empty, TabsProps, Tag } from "antd";
import {
  ClockCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  ShareAltOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  StarOutlined,
} from "@ant-design/icons";
import {
  Destination,
  PersonalOptions,
  TravelActivity,
  TravelDetailData,
} from "../types/travelPlan";

/**
 * TABLE OF CONTENTS
 *
 * UTILITY FUNCTIONS:
 * - formatDate: Formats a date to Vietnamese locale (dd/mm/yyyy)
 * - formatCurrency: Formats a number as VND currency
 * - calculateDurationDays: Calculates number of days between two dates
 * - getStatusTag: Returns a styled Tag component based on trip status
 * - getActivityIcon: Returns an icon component based on activity type
 *
 * ACTIVITY & TRAVEL CONSTANTS:
 * - ACTIVITY_TYPE_COLORS: Color mapping for activity types
 * - ACTIVITY_TYPE_TEXT: Text labels for activity types
 * - BUDGET_RANGES: Budget ranges and descriptions
 *
 * MOCK DATA (to be replaced with API calls):
 * - DESTINATIONS: Sample destination data
 * - PERSONAL_OPTIONS: Sample preference options
 * - MOCK_TRAVEL_PLANS: Sample travel plan list
 * - MOCK_TRAVEL_DETAIL: Detailed sample travel plan
 * - ACTION_MENU_ITEMS: Menu actions for travel plans
 * - TRAVEL_PLAN_TABS: Tab configuration for travel plans list
 */

// ================= UTILITY FUNCTIONS =================

/**
 * Format a date using Vietnamese locale
 */
export const formatDate = (date: Date): string => {
  return date.toLocaleDateString("vi-VN", {
    day: "numeric",
    month: "numeric",
    year: "numeric",
  });
};

/**
 * Format a number as Vietnamese currency
 */
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    minimumFractionDigits: 0,
  }).format(value);
};

/**
 * Calculate the number of days between two dates
 */
export const calculateDurationDays = (start: Date, end: Date): number => {
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
};

/**
 * Get a status tag component based on travel status
 */
export const getStatusTag = (status: TravelDetailData["status"]) => {
  let color = "";
  let text = "";

  switch (status) {
    case "planning":
    case "confirmed":
      color = "orange";
      text = "Đang diễn ra";
      break;
    case "completed":
      color = "green";
      text = "Đã hoàn thành";
      break;
    case "canceled":
      color = "red";
      text = "Đã hủy";
      break;
    default:
      color = "default";
      text = "Không xác định";
  }

  return (
    <Tag color={color} className="text-sm py-1 px-3">
      {text}
    </Tag>
  );
};

/**
 * Get an icon component based on activity type
 */
export const getActivityIcon = (type: TravelActivity["type"]) => {
  switch (type) {
    case "attraction":
      return <StarOutlined className="text-yellow-500" />;
    case "restaurant":
      return <DollarOutlined className="text-red-500" />;
    case "hotel":
      return <TeamOutlined className="text-blue-500" />;
    case "transport":
      return <ClockCircleOutlined className="text-green-500" />;
    default:
      return <EnvironmentOutlined />;
  }
};

// ================= ACTIVITY & TRAVEL CONSTANTS =================

export const ACTIVITY_TYPE_COLORS: Record<TravelActivity["type"], string> = {
  attraction: "blue",
  restaurant: "green",
  hotel: "red",
  transport: "default",
};

export const ACTIVITY_TYPE_TEXT: Record<TravelActivity["type"], string> = {
  attraction: "Tham quan",
  restaurant: "Nhà hàng",
  hotel: "Khách sạn",
  transport: "Di chuyển",
};

export const BUDGET_RANGES = {
  $: { min: 0, max: 5000000, description: "Tiết kiệm" },
  $$: { min: 5000000, max: 10000000, description: "Vừa phải" },
  $$$: { min: 10000000, max: 20000000, description: "Thoải mái" },
  $$$$: { min: 20000000, max: 50000000, description: "Sang trọng" },
  $$$$$: { min: 50000000, max: Infinity, description: "Đẳng cấp" },
};

export const ACTION_MENU_ITEMS = [
  {
    key: "1",
    icon: <EditOutlined />,
    label: "Chỉnh sửa",
  },
  {
    key: "2",
    icon: <ShareAltOutlined />,
    label: "Chia sẻ",
  },
  {
    key: "3",
    icon: <StarOutlined />,
    label: "Đánh dấu yêu thích",
  },
  {
    key: "4",
    icon: <DeleteOutlined />,
    label: "Xóa",
    danger: true,
  },
];

// ================= MOCK DATA (to be replaced with API) =================

export const DESTINATIONS: Destination[] = [
  {
    id: "hanoi",
    name: "Hà Nội",
    country: "Việt Nam",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    description:
      "Thủ đô ngàn năm văn hiến với nhiều di tích lịch sử và ẩm thực đặc sắc",
    rating: 4.8,
  },
  {
    id: "danang",
    name: "Đà Nẵng",
    country: "Việt Nam",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    description: "Thành phố biển với cầu Rồng và bãi biển Mỹ Khê tuyệt đẹp",
    rating: 4.9,
  },
  {
    id: "hcmc",
    name: "Hồ Chí Minh",
    country: "Việt Nam",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    description:
      "Thành phố sôi động với nhịp sống hiện đại và ẩm thực phong phú",
    rating: 4.7,
  },
  {
    id: "nhatrang",
    name: "Nha Trang",
    country: "Việt Nam",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    description:
      "Thiên đường biển với các khu nghỉ dưỡng cao cấp và hoạt động lặn biển",
    rating: 4.6,
  },
];

export const PERSONAL_OPTIONS: PersonalOptions = {
  places: [
    {
      type: "places",
      name: "Địa điểm ít người biết tới",
      description: "Khám phá những địa điểm độc đáo và ít người biết",
    },
    {
      type: "places",
      name: "Di tích lịch sử",
      description: "Tham quan các địa điểm lịch sử có ý nghĩa",
    },
    {
      type: "places",
      name: "Cảnh quan thiên nhiên",
      description: "Khám phá vẻ đẹp thiên nhiên hùng vĩ",
    },
  ],
  activities: [
    {
      type: "activities",
      name: "Hoạt động mạo hiểm",
      description: "Những trải nghiệm thú vị và đầy thách thức",
    },
    {
      type: "activities",
      name: "Tham quan văn hóa",
      description: "Khám phá nét văn hóa độc đáo của địa phương",
    },
    {
      type: "activities",
      name: "Trải nghiệm làng nghề",
      description: "Tìm hiểu về các nghề truyền thống địa phương",
    },
  ],
  food: [
    {
      type: "food",
      name: "Đặc sản địa phương",
      description: "Những món ăn nổi tiếng của địa phương",
    },
    {
      type: "food",
      name: "Món ăn truyền thống",
      description: "Khám phá ẩm thực truyền thống lâu đời",
    },
    {
      type: "food",
      name: "Quán ăn bình dân",
      description: "Trải nghiệm ẩm thực đường phố đặc sắc",
    },
  ],
  transportation: [
    {
      type: "transportation",
      name: "Phương tiện địa phương",
      description: "Di chuyển bằng các phương tiện đặc trưng của địa phương",
    },
    {
      type: "transportation",
      name: "Thuê xe riêng",
      description: "Tự do khám phá với phương tiện cá nhân",
    },
    {
      type: "transportation",
      name: "Đi bộ khám phá",
      description: "Tản bộ tham quan các địa điểm du lịch",
    },
  ],
  accommodation: [
    {
      type: "accommodation",
      name: "Homestay",
      description: "Trải nghiệm sống cùng người dân địa phương",
    },
    {
      type: "accommodation",
      name: "Khách sạn sang trọng",
      description: "Nghỉ dưỡng tại các cơ sở lưu trú cao cấp",
    },
    {
      type: "accommodation",
      name: "Cắm trại ngoài trời",
      description: "Trải nghiệm gần gũi với thiên nhiên",
    },
  ],
};

export const MOCK_TRAVEL_PLANS = [
  {
    id: "trip-1",
    destination: "Hà Nội",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    startDate: new Date(2023, 11, 20),
    endDate: new Date(2023, 11, 25),
    adults: 2,
    children: 1,
    budgetType: "$$$",
    activities: ["Di tích lịch sử", "Ẩm thực đường phố", "Tham quan văn hóa"],
    status: "confirmed",
  },
  {
    id: "trip-2",
    destination: "Đà Nẵng",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    startDate: new Date(2023, 10, 5),
    endDate: new Date(2023, 10, 10),
    adults: 2,
    children: 0,
    budgetType: "$$",
    activities: ["Biển", "Bà Nà Hills", "Hội An"],
    status: "aaa",
  },
  {
    id: "trip-3",
    destination: "Nha Trang",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    startDate: new Date(2023, 7, 15),
    endDate: new Date(2023, 7, 20),
    adults: 4,
    children: 2,
    budgetType: "$$$$",
    activities: ["Lặn biển", "Câu cá", "Vinpearl Land"],
    status: "completed",
  },
];

export const TRAVEL_PLAN_TABS = (
  renderTravelPlanItem: (item: any) => React.ReactNode,
  travelPlans: typeof MOCK_TRAVEL_PLANS
): TabsProps["items"] => [
  {
    key: "confirmed",
    label: "Sắp tới",
    children: (
      <List
        dataSource={travelPlans.filter((plan) => plan.status === "confirmed")}
        renderItem={renderTravelPlanItem}
        locale={{
          emptyText: (
            <Empty description="Không có kế hoạch du lịch nào sắp tới" />
          ),
        }}
      />
    ),
  },
  {
    key: "completed",
    label: "Đã hoàn thành",
    children: (
      <List
        dataSource={travelPlans.filter((plan) => plan.status === "completed")}
        renderItem={renderTravelPlanItem}
        locale={{
          emptyText: (
            <Empty description="Chưa có kế hoạch du lịch nào đã hoàn thành" />
          ),
        }}
      />
    ),
  },
  {
    key: "all",
    label: "Tất cả",
    children: (
      <List
        dataSource={travelPlans}
        renderItem={renderTravelPlanItem}
        locale={{
          emptyText: <Empty description="Chưa có kế hoạch du lịch nào" />,
        }}
      />
    ),
  },
];

export const MOCK_TRAVEL_DETAIL: TravelDetailData = {
  id: "trip-1",
  destination: "Hà Nội",
  imageUrl: "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
  startDate: new Date(2023, 11, 20),
  endDate: new Date(2023, 11, 25),
  adults: 2,
  children: 1,
  budgetType: "$$$",
  totalBudget: 15000000,
  spentBudget: 8500000,
  status: "confirmed",
  notes:
    "Chuẩn bị áo ấm và đồ dùng cá nhân đầy đủ. Kiểm tra thời tiết trước khi đi.",
  days: [
    {
      day: 1,
      date: new Date(2023, 11, 20),
      activities: [
        {
          id: "act-1-1",
          time: "08:00 - 10:00",
          type: "transport",
          name: "Khởi hành từ sân bay Tân Sơn Nhất",
          location: "Sân bay Tân Sơn Nhất, TP HCM",
          description:
            "Check-in tại quầy VietJet Air, cửa 5. Chuyến bay VJ123.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4,
          duration: 2,
        },
        {
          id: "act-1-2",
          time: "12:00 - 14:00",
          type: "restaurant",
          name: "Nhà hàng Quán Ăn Ngon",
          location: "18 Phan Bội Châu, Hoàn Kiếm, Hà Nội",
          description:
            "Ăn trưa với các món đặc sản Hà Nội như phở, bún chả, nem rán.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4.5,
          price: "150.000đ - 300.000đ/người",
          contactInfo: "024 3733 5656",
        },
        {
          id: "act-1-3",
          time: "15:00 - 18:00",
          type: "attraction",
          name: "Hoàn Kiếm Lake & Old Quarter",
          location: "Hoàn Kiếm, Hà Nội",
          description:
            "Đi dạo quanh Hồ Hoàn Kiếm, thăm đền Ngọc Sơn và khám phá 36 phố phường.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4.8,
          duration: 3,
          price: "30.000đ (vé vào đền Ngọc Sơn)",
        },
      ],
    },
    {
      day: 2,
      date: new Date(2023, 11, 21),
      activities: [
        {
          id: "act-2-1",
          time: "07:00 - 08:00",
          type: "restaurant",
          name: "Phở Thìn",
          location: "13 Lò Đúc, Hai Bà Trưng, Hà Nội",
          description: "Phở bò nổi tiếng Hà Nội với thịt bò xào thơm lừng.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4.7,
          price: "60.000đ - 80.000đ/tô",
          contactInfo: "024 3821 2709",
        },
        {
          id: "act-2-2",
          time: "09:00 - 12:00",
          type: "attraction",
          name: "Lăng Chủ tịch Hồ Chí Minh & Khu di tích Ba Đình",
          location: "Số 2 Hùng Vương, Ba Đình, Hà Nội",
          description:
            "Thăm Lăng Chủ tịch, nhà sàn, chùa Một Cột và bảo tàng Hồ Chí Minh.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4.6,
          duration: 3,
          price: "Miễn phí",
        },
      ],
    },
    {
      day: 3,
      date: new Date(2023, 11, 22),
      activities: [
        {
          id: "act-3-1",
          time: "08:00 - 17:00",
          type: "attraction",
          name: "Chuyến tham quan Vịnh Hạ Long 1 ngày",
          location: "Vịnh Hạ Long, Quảng Ninh",
          description:
            "Đi tàu thăm các đảo đá, hang động và làng chài trên Vịnh Hạ Long.",
          imageUrl:
            "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
          rating: 4.9,
          duration: 9,
          price: "1.200.000đ/người (bao gồm xe đưa đón, tàu, ăn trưa)",
        },
      ],
    },
  ],
};
export const MOCK_AI_SUGGESTIONS: TravelActivity[] = [
  {
    id: "ai-suggestion-1",
    time: "00:00 - 00:00",
    type: "attraction",
    name: "Bảo tàng văn hóa dân tộc Việt Nam",
    location: "Đường Nguyễn Văn Huyên, Cầu Giấy, Hà Nội",
    description:
      "Một trong những bảo tàng lớn nhất về văn hóa dân tộc tại Hà Nội. Khám phá lịch sử và văn hóa đa dạng của 54 dân tộc Việt Nam.",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.8,
    duration: 2.5,
    price: "30.000đ/người",
  },
  {
    id: "ai-suggestion-2",
    time: "00:00 - 00:00",
    type: "restaurant",
    name: "Phở Lý Quốc Sư",
    location: "Số 42 Lý Quốc Sư, Hoàn Kiếm, Hà Nội",
    description:
      "Thưởng thức phở truyền thống Hà Nội với nước dùng trong và ngọt tự nhiên. Nhà hàng nổi tiếng với công thức gia truyền nhiều đời.",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.9,
    price: "75.000đ - 95.000đ/tô",
  },
  {
    id: "ai-suggestion-3",
    time: "00:00 - 00:00",
    type: "attraction",
    name: "Chùa Trấn Quốc",
    location: "Thanh Niên, Quận Tây Hồ, Hà Nội",
    description:
      "Chùa Phật giáo cổ nhất Hà Nội, nằm trên một hòn đảo nhỏ phía đông Hồ Tây. Kiến trúc độc đáo và bầu không khí thanh bình.",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.7,
    duration: 3,
    price: "Miễn phí (đóng góp tùy tâm)",
  },
  {
    id: "ai-suggestion-4",
    time: "00:00 - 00:00",
    type: "restaurant",
    name: "Cha Ca Thang Long",
    location: "19-21-31 Đường Thành, Hoàn Kiếm, Hà Nội",
    description:
      "Nhà hàng chuyên về món chả cá truyền thống Hà Nội. Được chế biến ngay tại bàn với cá lóc tươi, thì là, hành và các loại gia vị.",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.6,
    price: "175.000đ/người",
  },
  {
    id: "ai-suggestion-5",
    time: "00:00 - 00:00",
    type: "attraction",
    name: "Phố cổ Hà Nội về đêm",
    location: "Khu phố cổ, Hoàn Kiếm, Hà Nội",
    description:
      "Khám phá phố cổ Hà Nội về đêm với không khí sôi động, ẩm thực đường phố phong phú và các cửa hàng mua sắm.",
    imageUrl:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.9,
    duration: 1.5,
    price: "Miễn phí",
  },
];
