import React from "react";
import { DestinationStep } from "./travelPlanDestination";
import { TimeStep } from "./travelPlanTime";
import { PersonalStep } from "./travelPlanPersonal";
import { PeopleBudgetStep } from "./travelPlanBasic";
import { LoadingStep } from "./travelLoading";
import { StepNavigation } from "./navbar";
import { useTravelPlan } from "../../hooks/useTravelPlans";
import { useAuth } from "../../hooks/useAuth";
import { DESTINATIONS } from "../../constants/travelPlanConstants";
import { Modal } from "antd";
import { SignIn } from "../authScreen/signIn";
import { SignUp } from "../authScreen/signUp";

export const TravelNewPlan: React.FC = () => {
  const [fade, setFade] = React.useState(false);

  const {
    currentStep,
    selectedDestinationId,
    budget,
    handleBudgetChange,
    handleNextStep,
    handlePrevStep,
    handleDestinationSelect,
    handleBacktoMain,
    handleDateChange,
    handleTimeType,
    handleAddOption,
    personalOptions,
    travelTime,
    handleMonthChange,
    handleLengthChange,
    people,
    handlePeopleChange,
    isDestinationSelection,
  } = useTravelPlan();

  const { isLoggedIn, authModalState, closeAuthModal, requireAuth } = useAuth();

  // Get destination name for display in loading screen
  const selectedDestination =
    DESTINATIONS.find((dest) => dest.id === selectedDestinationId)?.name ||
    "điểm đến của bạn";

  // Handle destination selection with auth check
  const handleDestinationWithAuth = (destId: string) => {
    handleDestinationSelect(destId);
    requireAuth(() => handleNextStep());
  };

  const switchTab = (tab: "signIn" | "signUp") => {
    setFade(true);
    setTimeout(() => {
      setFade(false);
    }, 200);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <PeopleBudgetStep
            budget={budget}
            onBudgetChange={handleBudgetChange}
            people={people}
            onPeopleChange={handlePeopleChange}
            onNext={handleNextStep}
            onPrev={handleBacktoMain}
          />
        );
      case 1:
        return (
          <TimeStep
            travelTime={travelTime}
            onSwitchTimeType={handleTimeType}
            onDateChange={handleDateChange}
            onMonthChange={handleMonthChange}
            onLengthChange={handleLengthChange}
            onNext={handleNextStep}
            onPrev={handlePrevStep}
          />
        );
      case 2:
        return (
          <PersonalStep
            personalOptions={personalOptions}
            onAddOption={handleAddOption}
            onNext={handleNextStep}
            onPrev={handlePrevStep}
            destination={selectedDestination}
            budget={budget}
            people={people}
            travelTime={travelTime}
          />
        );
      case 3:
        return (
          <LoadingStep
            destination={selectedDestination}
            onFinish={handleNextStep}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md max-w-6xl mx-auto my-8">
      {isDestinationSelection ? (
        <DestinationStep
          selectedDestination={selectedDestinationId}
          onSelectDestination={handleDestinationSelect}
          onStartPlan={() => {
            requireAuth(handleNextStep);
          }}
        />
      ) : (
        <>
          <StepNavigation currentStep={currentStep} />
          {renderStepContent()}
        </>
      )}

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
          {authModalState.initialTab === "signIn" ? (
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
    </div>
  );
};
