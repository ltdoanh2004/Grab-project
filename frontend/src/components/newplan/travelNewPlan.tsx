import React from "react";
import { DestinationStep } from "./travelPlanDestination";
import { TimeStep } from "./travelPlanTime";
import { PersonalStep } from "./travelPlanPersonal";
import { StepNavigation } from "./navbar";
import { useTravelPlan } from "../../hooks/useTravelPlans";
import { Typography, Button } from "antd";
import { DESTINATIONS } from "../../constants/travelPlanConstants";

const { Title } = Typography;

export const TravelNewPlan: React.FC = () => {
  const {
    currentStep,
    selectedDestinationId,
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
    isDestinationSelection,
  } = useTravelPlan();

  const selectedDestination = DESTINATIONS.find(
    (dest) => dest.id === selectedDestinationId
  );

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <TimeStep
            travelTime={travelTime}
            onSwitchTimeType={handleTimeType}
            onDateChange={handleDateChange}
            onMonthChange={handleMonthChange}
            onLengthChange={handleLengthChange}
            onNext={handleNextStep}
            onPrev={handleBacktoMain}
          />
        );
      case 1:
        return (
          <PersonalStep
            selectedOptions={selectedOptions}
            onAddOption={handleAddOption}
            onNext={handleNextStep}
            onPrev={handlePrevStep}
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
          {/* <div className="p-4 border-b bg-blue-50">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <img
                  src={selectedDestination?.imageUrl}
                  alt={selectedDestination?.name}
                  className="w-10 h-10 mr-3"
                />
                <Title level={4} className="m-0">
                  {selectedDestination?.name}, {selectedDestination?.country}
                </Title>
              </div>
              <Button type="link" onClick={handleBacktoMain}>
                Thay đổi
              </Button>
            </div>
          </div> */}

          <StepNavigation currentStep={currentStep} />
          {renderStepContent()}
        </>
      )}
    </div>
  );
};
