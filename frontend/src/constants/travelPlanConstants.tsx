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
  HomeOutlined,
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
export const formatDate = (date: Date | string | undefined | null): string => {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  if (!d || isNaN(d.getTime())) return "";
  return d.toLocaleDateString("vi-VN", {
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
export const calculateDurationDays = (
  start: Date | string | undefined | null,
  end: Date | string | undefined | null
): number => {
  if (!start || !end) return 0;
  const startDate = typeof start === "string" ? new Date(start) : start;
  const endDate = typeof end === "string" ? new Date(end) : end;
  if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return 0;
  return Math.round(
    (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
  );
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
export const getActivityIcon = (type: string) => {
  switch (type) {
    case "attraction":
      return <StarOutlined className="text-yellow-500" />;
    case "restaurant":
      return <DollarOutlined className="text-red-500" />;
    case "hotel":
      return <TeamOutlined className="text-blue-500" />;
    case "accommodation":
      return <HomeOutlined className="text-purple-500" />;
    case "transport":
      return <ClockCircleOutlined className="text-green-500" />;
    default:
      return <EnvironmentOutlined />;
  }
};

// ================= ACTIVITY & TRAVEL CONSTANTS =================

export const ACTIVITY_TYPE_COLORS: Record<string, string> = {
  attraction: "blue",
  restaurant: "green",
  hotel: "red",
  transport: "default",
  accommodation: "purple",
};

export const ACTIVITY_TYPE_TEXT: Record<string, string> = {
  attraction: "Tham quan",
  restaurant: "Nhà hàng",
  hotel: "Khách sạn",
  transport: "Di chuyển",
  accommodation: "Chỗ ở",
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
    trip_id: "trip-1",
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
    trip_id: "trip-2",
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
    trip_id: "trip-3",
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
  user_id: "user123",
  trip_name: "Trip to Hanoi",
  start_date: "2025-05-07",
  end_date: "2025-05-09",
  destination: "hanoi",
  adults: 2,
  children: 0,
  budgetType: "$$$",
  totalBudget: 15000000,
  spentBudget: 5000000,
  status: "confirmed",
  notes: "Mang theo áo mưa và kiểm tra thời tiết trước khi đi.",
  imageUrl: "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
  plan_by_day: [
    {
      date: "2025-05-07",
      day_title: "Ngày 1: Khám phá phố cổ Hà Nội",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "hotel_006100",
              type: "accommodation",
              name: "Hanoi Capital Hostel & Travel",
              start_time: "08:00",
              end_time: "10:00",
              description:
                "Bắt đầu ngày mới với không gian thoải mái tại Hanoi Capital Hostel & Travel.",
              rating: 4.5,
            },
            {
              id: "restaurant_020781",
              type: "restaurant",
              name: "Beefsteak Nam Sơn - Nguyễn Thị Minh Khai",
              start_time: "10:30",
              end_time: "11:30",
              description:
                "Thưởng thức bữa sáng với món bò nổi tiếng tại Beefsteak Nam Sơn.",
              rating: 4.2,
              cuisines: "Đặc sản địa phương",
              price_range: "100,000-300,000 VND",
            },
          ],
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "place_000481",
              type: "place",
              name: "Hanoi Old Quarter",
              start_time: "13:00",
              end_time: "15:00",
              description:
                "Chúng ta sẽ bắt đầu hành trình khám phá phố cổ Hà Nội.",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4,
            },
            {
              id: "place_000300",
              type: "place",
              name: "Ha Noi Nail",
              start_time: "15:30",
              end_time: "16:30",
              description:
                "Hãy tạm gác lại công việc và thư giãn tại Ha Noi Nail.",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4,
            },
          ],
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_000880",
              type: "restaurant",
              name: "Phở Hà Nội - Hồng Hà",
              start_time: "18:00",
              end_time: "19:00",
              description:
                "Chúng ta sẽ kết thúc ngày bằng bữa tối với món Phở Hà Nội truyền thống.",
              rating: 4.2,
              cuisines: "Đặc sản địa phương",
              price_range: "100,000-300,000 VND",
            },
            {
              id: "place_000159",
              type: "place",
              name: "City Game Hanoi",
              start_time: "19:30",
              end_time: "21:30",
              description:
                "Hãy thư giãn và tận hưởng những trò chơi thú vị tại City Game Hanoi.",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4,
            },
          ],
        },
      ],
    },
    {
      date: "2025-05-08",
      day_title: "Ngày 2: Khám phá những điểm đến nổi tiếng tại Hà Nội",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "hotel_005820",
              type: "accommodation",
              name: "Hanoi Capital Hostel & Travel",
              start_time: "08:00",
              end_time: "10:00",
              description:
                "Bạn sẽ được tận hưởng bữa sáng ngon miệng, chuẩn bị cho một ngày dài khám phá Hà Nội.",
              rating: 4.5,
              price: 850000,
            },
            {
              id: "place_011097",
              type: "place",
              name: "Hanoi Old Quarter",
              start_time: "10:30",
              end_time: "12:00",
              description:
                "Chúng ta sẽ dạo quanh khu phố cổ, tận hưởng không khí sôi động của Hà Nội.",
              address: "Hà Nội",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4.5,
              price: 50000,
            },
          ],
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "restaurant_000880",
              type: "restaurant",
              name: "Phở Hà Nội - Hồng Hà",
              start_time: "12:30",
              end_time: "13:30",
              description:
                "Hãy thưởng thức một bữa trưa ngon miệng với món phở truyền thống.",
              address: "Hà Nội",
              rating: 4.5,
              cuisines: "Đặc sản địa phương",
              price_range: "100,000-300,000 VND",
            },
            {
              id: "place_000159",
              type: "place",
              name: "City Game Hanoi",
              start_time: "14:00",
              end_time: "16:00",
              description:
                "Bạn sẽ được tham gia vào những trò chơi vui nhộn, thú vị.",
              address: "Hà Nội",
              categories: "entertainment",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4,
              price: 150000,
            },
          ],
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_004226",
              type: "restaurant",
              name: "Pho Phuc",
              start_time: "18:00",
              end_time: "19:00",
              description: "Hãy thưởng thức bữa tối với món phở ngon tuyệt.",
              address: "Hà Nội",
              rating: 4.5,
              cuisines: "Đặc sản địa phương",
              price_range: "100,000-300,000 VND",
            },
            {
              id: "place_000028",
              type: "place",
              name: "Nha Hat Cai Luong Ha Noi",
              start_time: "19:30",
              end_time: "21:00",
              description: "Thưởng thức buổi biểu diễn cải lương tuyệt vời.",
              address: "Hà Nội",
              categories: "entertainment",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4.5,
              price: 200000,
            },
          ],
        },
      ],
    },
    {
      date: "2025-05-09",
      day_title: "Ngày 3: Hành trình văn hóa Hà Nội",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "hotel_007260",
              type: "accommodation",
              name: "Hanoi Memory Premier Hotel & Spa",
              start_time: "08:00",
              end_time: "10:00",
              description:
                "Bạn sẽ được thưởng thức bữa sáng phong cách Việt Nam tại khách sạn.",
              rating: 4.5,
              price: 850000,
            },
            {
              id: "place_011097",
              type: "place",
              name: "Hanoi Old Quarter",
              start_time: "10:30",
              end_time: "12:30",
              description:
                "Chúng ta sẽ bắt đầu ngày mới bằng việc khám phá khu phố cổ Hà Nội.",
              address: "Hà Nội",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4.5,
              price: 50000,
            },
          ],
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "restaurant_020781",
              type: "restaurant",
              name: "Beefsteak Nam Sơn - Nguyễn Thị Minh Khai",
              start_time: "13:00",
              end_time: "14:00",
              description:
                "Hãy thưởng thức bữa trưa với món bò nổi tiếng của Hà Nội.",
              address: "Hà Nội",
              rating: 4.5,
              cuisines: "Đặc sản địa phương",
              price_range: "100,000-300,000 VND",
            },
            {
              id: "place_000481",
              type: "place",
              name: "Ha Noi",
              start_time: "14:30",
              end_time: "16:30",
              description:
                "Tiếp tục hành trình khám phá văn hóa, lịch sử của thủ đô Hà Nội.",
              address: "Hà Nội",
              categories: "sightseeing",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4.5,
              price: 50000,
            },
          ],
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_016933",
              type: "restaurant",
              name: "Highlands Coffee - Trà, Cà Phê & Bánh - Vincom Quang Trung",
              start_time: "17:00",
              end_time: "18:00",
              description:
                "Thưởng thức ly cà phê đặc sắc của Highlands Coffee.",
              address: "Hà Nội",
              rating: 4.5,
              cuisines: "Cà phê",
              price_range: "100,000-300,000 VND",
            },
            {
              id: "place_000028",
              type: "place",
              name: "Nha Hat Cai Luong Ha Noi",
              start_time: "19:00",
              end_time: "21:00",
              description:
                "Kết thúc ngày với buổi biểu diễn cải lương đầy màu sắc tại Nhà hát Cải lương Hà Nội.",
              address: "Hà Nội",
              categories: "entertainment",
              duration: "2h",
              opening_hours: "08:00-17:00",
              rating: 4.5,
              price: 100000,
            },
          ],
        },
      ],
    },
  ],
};

export const MOCK_TRAVEL_DETAIL_2: TravelDetailData = {
  id: "trip-2",
  user_id: "user123",
  trip_name: "Trip to Hanoi",
  start_date: "2025-05-10",
  end_date: "2025-05-12",
  destination: "hanoi",
  adults: 2,
  children: 0,
  budgetType: "$$$",
  totalBudget: 15000000,
  spentBudget: 5000000,
  status: "confirmed",
  notes: "Khám phá ẩm thực và văn hoá Hà Nội.",
  imageUrl: "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
  plan_by_day: [
    {
      date: "2025-05-10",
      day_title: "Ngày 1: Khám phá nét cổ kính của Hà Nội",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "hotel_008170",
              type: "accommodation",
              name: "Luxury Hanoi Hotel",
              start_time: "08:00",
              end_time: "11:00",
              description: "Thư giãn tại khách sạn sang trọng trong trung tâm thành phố.",
              address: "Hà Nội",
              rating: 4.5,
              price: 850000,
              image_url: "",
              price_ai_estimate: 3000000.0
            }
          ]
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "place_000003",
              type: "place",
              name: "Chuong Tailor",
              start_time: "13:00",
              end_time: "16:00",
              description: "Trải nghiệm làm đồ thủ công truyền thống tại Chuong Tailor.",
              address: "Hà Nội",
              categories: "shopping",
              rating: 4.2,
              price: 150000,
              image_url: "",
              price_ai_estimate: 300000.0
            }
          ]
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_001958",
              type: "restaurant",
              name: "Vietnamese Family Meal",
              start_time: "18:00",
              end_time: "20:00",
              description: "Thưởng thức bữa tối ấm cúng với món ăn gia đình Việt Nam.",
              address: "Hà Nội",
              cuisines: "Vietnamese",
              rating: 4.6,
              image_url: "",
              price_ai_estimate: 350000.0
            }
          ]
        }
      ],
      daily_tips: [
        "Nên bắt đầu sớm từ 6-8h sáng để tránh nóng và đông đúc.",
        "Mang theo nước và đồ ăn nhẹ để giữ năng lượng.",
        "Sử dụng bản đồ offline để không phụ thuộc vào internet.",
        "Mặc quần áo thoải mái và mang giày đi bộ.",
        "Đổi tiền trước khi đi để tránh rắc rối.",
        "Hãy cẩn thận với tài sản cá nhân khi đi qua khu vực đông người.",
        "Tham quan Văn Miếu Quốc Tử Giám vào buổi sáng để tránh đông đúc.",
        "Thưởng thức phở tại một quán nổi tiếng gần Hồ Hoàn Kiếm.",
        "Chụp ảnh tại Nhà Thờ Lớn Hà Nội vào buổi chiều để có ánh sáng đẹp."
      ]
    },
    {
      date: "2025-05-11",
      day_title: "Ngày 2: Thưởng thức Hà Nội qua ẩm thực",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "restaurant_000098",
              type: "restaurant",
              name: "Family Restaurant",
              start_time: "08:00",
              end_time: "10:00",
              description: "Bạn sẽ được thưởng thức bữa sáng với các món ăn truyền thống của Hà Nội.",
              address: "Hà Nội",
              price_ai_estimate: 120000.0
            }
          ]
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "restaurant_000623",
              type: "restaurant",
              name: "Little Hanoi Restaurants",
              start_time: "12:00",
              end_time: "14:00",
              description: "Hãy tận hưởng bữa trưa với những món ăn đặc trưng của Hà Nội.",
              address: "Hà Nội",
              price_ai_estimate: 150000.0
            }
          ]
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_000494",
              type: "restaurant",
              name: "Maison Sen",
              start_time: "18:00",
              end_time: "20:00",
              description: "Kết thúc ngày với bữa tối tại một trong những nhà hàng nổi tiếng nhất Hà Nội.",
              address: "Hà Nội",
              price_ai_estimate: 500000.0
            }
          ]
        }
      ],
      daily_tips: [
        "Đặt chỗ trước và đến Maison Sen vào buổi tối để có trải nghiệm tốt nhất.",
        "Di chuyển giữa các nhà hàng bằng taxi hoặc xe ôm công nghệ để tiết kiệm thời gian.",
        "Dự kiến chi phí mỗi bữa ăn từ 200,000 - 500,000 VND tùy món.",
        "Tránh đến Maison Sen vào giờ cao điểm 18h-20h nếu không đặt chỗ trước.",
        "Tìm hiểu khuyến mãi hoặc combo tại Family Restaurant để tiết kiệm chi phí.",
        "Giữ thái độ lịch sự khi giao tiếp với nhân viên nhà hàng và hỏi về cách ăn đúng cách."
      ]
    },
    {
      date: "2025-05-12",
      day_title: "Ngày 3: Trải nghiệm văn hóa ẩm thực Hà Nội",
      segments: [
        {
          time_of_day: "morning",
          activities: [
            {
              id: "restaurant_000231",
              type: "restaurant",
              name: "Minh´s Family Cooking",
              start_time: "08:30",
              end_time: "10:30",
              description: "Học nấu ăn Việt Nam trong bầu không khí gia đình tại Minh's Family Cooking.",
              address: "Hà Nội",
              cuisines: "Việt Nam",
              rating: 4.3,
              price_ai_estimate: 500000.0
            }
          ]
        },
        {
          time_of_day: "afternoon",
          activities: [
            {
              id: "restaurant_001808",
              type: "restaurant",
              name: "Freedom Hostel Restaurant",
              start_time: "12:00",
              end_time: "14:00",
              description: "Thưởng thức bữa trưa tại Freedom Hostel Restaurant, nơi có món ăn đặc trưng của Hà Nội.",
              address: "Hà Nội",
              cuisines: "Việt Nam",
              rating: 4.1,
              price_ai_estimate: 150000.0
            },
            {
              id: "restaurant_000498",
              type: "restaurant",
              name: "Vi Hanoi Restaurant & Cafe",
              start_time: "14:30",
              end_time: "16:00",
              description: "Thưởng thức cà phê Việt Nam tại Vi Hanoi Restaurant & Cafe.",
              address: "Hà Nội",
              cuisines: "Cafe",
              rating: 4.2,
              price_ai_estimate: 200000.0
            }
          ]
        },
        {
          time_of_day: "evening",
          activities: [
            {
              id: "restaurant_000658",
              type: "restaurant",
              name: "Bamboo Bar",
              start_time: "18:00",
              end_time: "20:00",
              description: "Cuối ngày, thư giãn tại Bamboo Bar với cocktail tuyệt vời.",
              address: "Hà Nội",
              cuisines: "Bar",
              rating: 4.5,
              price_ai_estimate: 300000.0
            }
          ]
        }
      ],
      daily_tips: [
        "Bắt đầu ngày mới với lớp học nấu ăn tại Minh's Family Cooking từ 08:30 - 10:30.",
        "Sử dụng xe ôm công nghệ hoặc taxi để di chuyển giữa các địa điểm trong ngày.",
        "Dự kiến chi phí cả ngày khoảng 700,000 - 900,000 VND, chuẩn bị thêm tiền mặt để tiện thanh toán.",
        "Tránh ăn quá no tại một địa điểm để thưởng thức nhiều món khác nhau trong ngày.",
        "Hỏi trước về nguyên liệu nếu có dị ứng thực phẩm.",
        "Hỏi về món ăn đặc biệt trong ngày hoặc thực đơn combo để tiết kiệm chi phí.",
        "Tìm hiểu giờ khuyến mãi \"happy hour\" tại Bamboo Bar.",
        "Tôn trọng phong tục tập quán địa phương khi tham gia lớp học nấu ăn.",
        "Thử cà phê trứng tại Vi Hanoi Cafe và các món đặc trưng như phở, bún chả tại Freedom Hostel Restaurant.",
        "Tôn trọng không gian chung và giữ thái độ lịch sự tại Bamboo Bar."
      ]
    }
  ]
};

export const MOCK_AI_SUGGESTIONS: TravelActivity[] = [
  {
    id: "ai-suggestion-1",
    type: "attraction",
    name: "Bảo tàng văn hóa dân tộc Việt Nam",
    start_time: "09:00",
    end_time: "11:30",
    address: "Đường Nguyễn Văn Huyên, Cầu Giấy, Hà Nội",
    description:
      "Một trong những bảo tàng lớn nhất về văn hóa dân tộc tại Hà Nội. Khám phá lịch sử và văn hóa đa dạng của 54 dân tộc Việt Nam.",
    image_url:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.8,
    duration: "2.5h",
    price: 30000,
  },
  {
    id: "ai-suggestion-2",
    type: "restaurant",
    name: "Phở Lý Quốc Sư",
    start_time: "12:00",
    end_time: "13:00",
    address: "Số 42 Lý Quốc Sư, Hoàn Kiếm, Hà Nội",
    description:
      "Thưởng thức phở truyền thống Hà Nội với nước dùng trong và ngọt tự nhiên. Nhà hàng nổi tiếng với công thức gia truyền nhiều đời.",
    image_url:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.9,
    price: 95000,
    duration: "1h",
  },
  {
    id: "ai-suggestion-3",
    type: "attraction",
    name: "Chùa Trấn Quốc",
    start_time: "14:00",
    end_time: "17:00",
    address: "Thanh Niên, Quận Tây Hồ, Hà Nội",
    description:
      "Chùa Phật giáo cổ nhất Hà Nội, nằm trên một hòn đảo nhỏ phía đông Hồ Tây. Kiến trúc độc đáo và bầu không khí thanh bình.",
    image_url:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.7,
    duration: "3h",
    price: 0,
  },
  {
    id: "ai-suggestion-4",
    type: "restaurant",
    name: "Cha Ca Thang Long",
    start_time: "18:00",
    end_time: "19:30",
    address: "19-21-31 Đường Thành, Hoàn Kiếm, Hà Nội",
    description:
      "Nhà hàng chuyên về món chả cá truyền thống Hà Nội. Được chế biến ngay tại bàn với cá lóc tươi, thì là, hành và các loại gia vị.",
    image_url:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.6,
    price: 175000,
    duration: "1.5h",
  },
  {
    id: "ai-suggestion-5",
    type: "attraction",
    name: "Phố cổ Hà Nội về đêm",
    start_time: "19:30",
    end_time: "21:00",
    address: "Khu phố cổ, Hoàn Kiếm, Hà Nội",
    description:
      "Khám phá phố cổ Hà Nội về đêm với không khí sôi động, ẩm thực đường phố phong phú và các cửa hàng mua sắm.",
    image_url:
      "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
    rating: 4.9,
    duration: "1.5h",
    price: 0,
  },
];
