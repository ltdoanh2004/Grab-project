import React from "react";
import { DestinationStep } from "./travelPlanDestination";
import { TimeStep } from "./travelPlanTime";
import { PersonalStep } from "./travelPlanPersonal";
import { PeopleBudgetStep } from "./travelPlanBasic";
import { LoadingStep } from "./travelLoading";
import { StepNavigation } from "./navbar";
import { useTravelPlan } from "../../hooks/useTravelPlans";
import { DESTINATIONS } from "../../constants/travelPlanConstants";

export const TravelNewPlan: React.FC = () => {
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
    selectedOptions,
    travelTime,
    handleMonthChange,
    handleLengthChange,
    people,
    handlePeopleChange,
    isDestinationSelection,
  } = useTravelPlan();

  // Get destination name for display in loading screen
  const selectedDestination =
    DESTINATIONS.find((dest) => dest.id === selectedDestinationId)?.name ||
    "điểm đến của bạn";

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
            selectedOptions={selectedOptions}
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
            handleNextStep();
          }}
        />
      ) : (
        <>
          <StepNavigation currentStep={currentStep} />
          {renderStepContent()}
        </>
      )}
    </div>
  );
};
