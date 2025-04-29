import React from "react";

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
    <header className="sticky top-0 z-50 shadow-sm bg-white">
      <div className="max-w-7xl mx-auto flex justify-between font-inter items-center py-3 px-4 md:px-6">
        <div className="flex items-center">
          <div className="flex items-center justify-center w-10 h-10 rounded-full bg-black mr-3">
            <img
              src="https://cdn-icons-png.flaticon.com/512/684/684908.png"
              alt="Travel Icon"
              className="w-5 h-5 invert"
            />
          </div>
          <h1 className="text-xl font-bold text-black">Travel Planner</h1>
        </div>

        <div className="flex space-x-1">
          <button
            className={`px-4 py-2 relative cursor-pointer rounded-md transition-all duration-200 ${
              activeTab === "plan-new"
                ? "text-black font-semibold"
                : "text-gray-600 hover:text-black hover:bg-gray-50"
            }`}
            onClick={() => onTabChange("plan-new")}
          >
            Chuyến đi
            {activeTab === "plan-new" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-black"></span>
            )}
          </button>
          <button
            className={`px-4 py-2 relative cursor-pointer rounded-md transition-all duration-200 ${
              activeTab === "plan-list"
                ? "text-black font-semibold"
                : "text-gray-600 hover:text-black hover:bg-gray-50"
            }`}
            onClick={() => onTabChange("plan-list")}
          >
            Lịch trình
            {activeTab === "plan-list" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-black"></span>
            )}
          </button>
        </div>

        <div className="flex space-x-3">
          <button className="px-4 py-1.5 text-sm font-medium text-black hover:text-gray-700 border border-gray-300 hover:border-gray-400 rounded-full transition-all duration-200">
            Đăng nhập
          </button>
          <button className="px-4 py-1.5 text-sm font-medium text-white bg-black hover:bg-gray-800 rounded-full shadow-sm hover:shadow transition-all duration-200">
            Đăng ký
          </button>
        </div>
      </div>
    </header>
  );
};
