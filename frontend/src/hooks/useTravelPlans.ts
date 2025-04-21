import { useState } from "react";
import { TravelTime, PersonalOption } from "../types/travelPlan";

export const useTravelPlan = () => {
  const [currentStep, setCurrentStep] = useState<number>(-1);
  const [selectedDestinationId, setSelectedDestinationId] = useState<
    string | null
  >(null);

  const [travelTime, setTravelTime] = useState<TravelTime>({
    type: "exact",
    startDate: new Date(),
    endDate: new Date(),
  });
  const [selectedOptions, setSelectedOptions] = useState<PersonalOption[]>([]);

  const handleTimeType = (type: "exact" | "flexible") => {
    if (type === "exact" && travelTime.type !== "exact") {
      setTravelTime({
        type: "exact",
        startDate: new Date(),
        endDate: new Date(),
      });
    } else if (type === "flexible" && travelTime.type !== "flexible") {
      setTravelTime({
        type: "flexible",
        month: 0,
        length: 0,
      });
    }
  };

  const handleDateChange = (dates: any) => {
    if (dates && travelTime.type === "exact") {
      setTravelTime({
        ...travelTime,
        startDate: dates[0] ? dates[0].toDate() : new Date(),
        endDate: dates[1] ? dates[1].toDate() : null,
      });
    }
  };

  const handleMonthChange = (month: number) => {
    if (travelTime.type === "flexible") {
      setTravelTime({
        ...travelTime,
        month,
      });
    }
  };

  const handleLengthChange = (days: number) => {
    if (travelTime.type === "flexible") {
      setTravelTime({
        ...travelTime,
        length: days,
      });
    }
  };

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

  const handleAddOption = (option: PersonalOption) => {
    const optionExists = selectedOptions.some(
      (item) => item.type === option.type && item.name === option.name
    );

    if (optionExists) {
      setSelectedOptions(
        selectedOptions.filter(
          (item) => !(item.type === option.type && item.name === option.name)
        )
      );
    } else {
      setSelectedOptions([...selectedOptions, option]);
    }
  };

  return {
    currentStep,
    selectedDestinationId,
    travelTime,
    handleNextStep,
    handlePrevStep,
    handleDestinationSelect,
    handleTimeType,
    handleStartPlan,
    handleBacktoMain,
    handleDateChange,
    handleMonthChange,
    handleAddOption,
    selectedOptions,
    handleLengthChange,
    isDestinationSelection: currentStep === -1,
  };
};
