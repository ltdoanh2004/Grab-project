export const DESTINATION_MAPPINGS: Record<string, string> = {
  "Bình Thuận": "binhthuan",
  "Cần Thơ": "cantho",
  "Đà Lạt": "dalat",
  "Đà Nẵng": "danang",
  "Hải Phòng": "haiphong",
  "Hà Nội": "hanoi",
  "HCMC": "hcmc",
  "Hồ Chí Minh": "hochiminh",
  "Huế": "hue",
  "Khánh Hoà": "khanhhoa",
  "Lâm Đồng": "lamdong",
  "Nha Trang": "nhatrang",
  "Phan Thiết": "phanthiet",
  "Sapa": "sapa",
  "Vũng Tàu": "vungtau"
};

// Reverse mapping for looking up name by ID
export const DESTINATION_IDS_TO_NAMES: Record<string, string> = Object.entries(DESTINATION_MAPPINGS)
  .reduce((acc, [name, id]) => {
    acc[id] = name;
    return acc;
  }, {} as Record<string, string>); 