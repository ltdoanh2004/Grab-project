import React, { useState } from "react";

type TabType = "plan-new" | "plan-list";

interface TravelHeaderProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const TravelHeader: React.FC<TravelHeaderProps> = ({
  activeTab,
  onTabChange,
}) => {
  return (
    <header className="sticky top-0 z-50 shadow-sm">
      <div className="flex justify-between font-inter items-center p-2 bg-gray-50 w-full">
        <div className="flex flex-row items-center">
          <img
            src="https://cdn-icons-png.flaticon.com/512/684/684908.png"
            alt="Travel Icon"
            className="w-8 h-8 mr-4"
          />
          <h1 className="text-xl font-bold text-black">Travel Planner</h1>
        </div>

        <div className="flex flex-row">
          <button
            className={`px-4 py-2 mx-1 cursor-pointer ${
              activeTab === "plan-new"
                ? "font-bold border-b-2 border-black text-CF0F47"
                : "hover:text-black"
            }`}
            onClick={() => onTabChange("plan-new")}
          >
            Chuyến đi
          </button>
          <button
            className={`px-4 py-2 mx-1 cursor-pointer ${
              activeTab === "plan-list"
                ? "font-bold border-b-2 border-black text-CF0F47"
                : "hover:text-black"
            }`}
            onClick={() => onTabChange("plan-list")}
          >
            Lịch trình
          </button>
        </div>

        <div className="flex flex-row">
          <button className="ml-4">Đăng nhập</button>
          <button className="ml-4">Đăng ký</button>
        </div>
      </div>
    </header>
  );
};
