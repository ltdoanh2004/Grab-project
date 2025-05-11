export const BACKUP_HOTEL_IMAGES = [
  "https://www.vietnambooking.com/wp-content/uploads/2020/12/Khach-san-Vinpearl-Tay-Ninh.jpg",
  "https://media-cdn-v2.laodong.vn/Storage/NewsPortal/2023/5/29/1198274/Swimming-Pool-1.jpg",
  "https://acihome.vn/uploads/17/top-khach-san-dep-nhat-sang-chanh-nhat-tai-viet-nam3.jpg",
  "https://i.ex-cdn.com/golfviet.vn/files/content/2020/11/10/top-10-khach-san-lon-nhat-viet-nam-1026.jpg",
  "https://www.thereveriesaigon.com/wp-content/uploads/2024/04/Room-3310_PDK-2000x1500.jpg"
];

/**
 * Returns a random backup hotel image URL
 */
export function getRandomHotelImage(): string {
  const randomIndex = Math.floor(Math.random() * BACKUP_HOTEL_IMAGES.length);
  return BACKUP_HOTEL_IMAGES[randomIndex];
}

/**
 * Returns a specific hotel image by index (with fallback to random if index is out of bounds)
 */
export function getHotelImageByIndex(index: number): string {
  if (index >= 0 && index < BACKUP_HOTEL_IMAGES.length) {
    return BACKUP_HOTEL_IMAGES[index];
  }
  return getRandomHotelImage();
} 