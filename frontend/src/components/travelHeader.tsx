import React, { useState, useEffect } from "react";
import { Modal, Avatar, Dropdown } from "antd";
import { UserOutlined, LogoutOutlined } from "@ant-design/icons";
import { SignIn } from "./authScreen/signIn";
import { SignUp } from "./authScreen/signUp";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

type TabType = "plan-new" | "plan-list";

interface TravelHeaderProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const TravelHeader: React.FC<TravelHeaderProps> = ({
  activeTab,
  onTabChange,
}) => {
  const navigate = useNavigate();
  const { isLoggedIn, signOut, authModalState, closeAuthModal, requireAuth } =
    useAuth();
  const [fade, setFade] = useState(false);
  const [authTab, setAuthTab] = useState<"signIn" | "signUp">("signIn");

  // Keep local authTab in sync with authModalState
  useEffect(() => {
    if (authModalState.initialTab) {
      setAuthTab(authModalState.initialTab);
    }
  }, [authModalState]);

  const switchTab = (tab: "signIn" | "signUp") => {
    setFade(true);
    setTimeout(() => {
      setAuthTab(tab);
      setFade(false);
    }, 200);
  };

  const userMenuItems = [
    {
      key: "1",
      label: "Đăng xuất",
      icon: <LogoutOutlined />,
      onClick: signOut,
    },
  ];

  const handleLogoClick = () => {
    navigate('/');
    onTabChange('plan-new');
  };

  return (
    <header className="sticky top-0 z-50 shadow-sm bg-white">
      <div className="max-w-7xl mx-auto flex justify-between font-inter items-center py-3 px-4 md:px-6">
        <div 
          className="flex items-center cursor-pointer" 
          onClick={handleLogoClick}
        >
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
            onClick={() => requireAuth(() => onTabChange("plan-list"))}
          >
            Lịch trình
            {activeTab === "plan-list" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-black"></span>
            )}
          </button>
        </div>

        {isLoggedIn ? (
          <div className="flex justify-end w-[154px]">
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={["click"]}
            >
              <div className="cursor-pointer border-2 border-gray-300 rounded-full hover:border-gray-500 transition-all">
                <Avatar
                  size={40}
                  src="https://i.pinimg.com/736x/39/59/fe/3959fe4712c01cd61b5d524e04eec6db.jpg"
                  className="hover:opacity-80 transition-opacity"
                />
              </div>
            </Dropdown>
          </div>
        ) : (
          <div className="flex space-x-3">
            <button
              className="px-4 py-1.5 text-sm font-medium text-black hover:text-gray-700 border border-gray-300 hover:border-gray-400 rounded-full transition-all duration-200 cursor-pointer"
              onClick={() => requireAuth(undefined, "signIn")}
            >
              Đăng nhập
            </button>
            <button
              className="px-4 py-1.5 text-sm font-medium text-white bg-black hover:bg-gray-800 rounded-full shadow-sm hover:shadow transition-all duration-200 cursor-pointer"
              onClick={() => requireAuth(undefined, "signUp")}
            >
              Đăng ký
            </button>
          </div>
        )}
      </div>

      <Modal
        open={authModalState.isOpen}
        onCancel={closeAuthModal}
        footer={null}
        destroyOnClose
        centered
        width={420}
      >
        <div
          style={{
            transition: "opacity 0.1s",
            opacity: fade ? 0 : 1,
            minHeight: 420,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {authTab === "signIn" ? (
            <SignIn
              onSwitchToSignUp={() => switchTab("signUp")}
              onLoginSuccess={closeAuthModal}
            />
          ) : (
            <SignUp
              onSwitchToSignIn={() => switchTab("signIn")}
              onSignUpSuccess={closeAuthModal}
            />
          )}
        </div>
      </Modal>
    </header>
  );
};
