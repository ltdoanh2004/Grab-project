import { useState, useEffect, useCallback } from "react";

export type AuthModalState = {
  isOpen: boolean;
  onSuccess?: () => void;
  initialTab?: "signIn" | "signUp";
};

export function useAuth() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authModalState, setAuthModalState] = useState<AuthModalState>({
    isOpen: false,
    initialTab: "signIn",
  });

  useEffect(() => {
    const checkLoginStatus = () => {
      const token = localStorage.getItem("access_token");
      setIsLoggedIn(!!token);
    };

    checkLoginStatus();
    window.addEventListener("storage", checkLoginStatus);

    return () => {
      window.removeEventListener("storage", checkLoginStatus);
    };
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setIsLoggedIn(false);
  }, []);

  const closeAuthModal = useCallback(() => {
    setAuthModalState((prev) => ({ ...prev, isOpen: false }));
    // Execute the onSuccess callback if it exists and user is now logged in
    if (authModalState.onSuccess && localStorage.getItem("access_token")) {
      authModalState.onSuccess();
    }
  }, [authModalState]);

  const requireAuth = useCallback(
    (onSuccess?: () => void, initialTab: "signIn" | "signUp" = "signIn") => {
      if (isLoggedIn) {
        // If already logged in, just run the callback
        onSuccess?.();
      } else {
        // If not logged in, show the auth modal and store the callback
        setAuthModalState({
          isOpen: true,
          onSuccess,
          initialTab,
        });
      }
    },
    [isLoggedIn]
  );

  return {
    isLoggedIn,
    signOut,
    authModalState,
    closeAuthModal,
    requireAuth,
  };
}
