import { useState } from "react";

export const useTravelPlan = () => {
  const [currentStep, setCurrentStep] = useState<number>(-1);
  const [selectedDestinationId, setSelectedDestinationId] = useState<
    string | null
  >(null);

  const [isExactDates, setIsExactDates] = useState<boolean>(true);

  const handleNextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const handlePrevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleDestinationSelect = (destId: string) => {
    setSelectedDestinationId(destId);
  };

  const handleStartPlan = () => {
    setCurrentStep(0);
  };

  const handleBacktoMain = () => {
    setCurrentStep(-1);
  };

  const toggleDateMode = () => {
    setIsExactDates(!isExactDates);
  };

  return {
    currentStep,
    selectedDestinationId,

    isExactDates,
    handleNextStep,
    handlePrevStep,
    handleDestinationSelect,
    handleStartPlan,
    handleBacktoMain,

    toggleDateMode,
    isDestinationSelection: currentStep === -1,
  };
};
