import { Destination } from "../types/travelPlan";
import { PersonalOptions } from "../types/travelPlan";

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
export const BUDGET_RANGES = {
  $: { min: 0, max: 5000000, description: "Tiết kiệm" },
  $$: { min: 5000000, max: 10000000, description: "Vừa phải" },
  $$$: { min: 10000000, max: 20000000, description: "Thoải mái" },
  $$$$: { min: 20000000, max: 50000000, description: "Sang trọng" },
  $$$$$: { min: 50000000, max: Infinity, description: "Đẳng cấp" },
};
