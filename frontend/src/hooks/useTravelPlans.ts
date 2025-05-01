import { useState, useCallback } from "react";
import {
  TravelTime,
  PersonalOption,
  Budget,
  NumOfPeople,
} from "../types/travelPlan";
import { BUDGET_RANGES } from "../constants/travelPlanConstants";

export const useTravelPlan = () => {
  //step magnage
  const [currentStep, setCurrentStep] = useState<number>(-1);

  //destination
  const [selectedDestinationId, setSelectedDestinationId] = useState<
    string | null
  >(null);

  const handleDestinationSelect = useCallback((destId: string) => {
    setSelectedDestinationId(destId);
  }, []);

  //bdget & People
  const [budget, setBudget] = useState<Budget>({
    type: "$$",
    exactBudget: 5000000,
  });

  const [people, setPeople] = useState<NumOfPeople>({
    adults: 2,
    children: 0,
    infants: 0,
    pets: 0,
  });

  const handleBudgetChange = useCallback((newBudget: Budget) => {
    setBudget(newBudget);
  }, []);

  const handlePeopleChange = useCallback((newPeople: NumOfPeople) => {
    setPeople(newPeople);
  }, []);

  //time
  const [travelTime, setTravelTime] = useState<TravelTime>({
    type: "exact",
    startDate: new Date(),
    endDate: new Date(),
  });

  const handleTimeType = useCallback(
    (type: "exact" | "flexible") => {
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
    },
    [travelTime.type]
  );

  const handleDateChange = useCallback(
    (dates: any) => {
      if (dates && travelTime.type === "exact") {
        setTravelTime({
          ...travelTime,
          startDate: dates[0] ? dates[0].toDate() : new Date(),
          endDate: dates[1] ? dates[1].toDate() : null,
        });
      }
    },
    [travelTime]
  );

  const handleMonthChange = useCallback(
    (month: number) => {
      if (travelTime.type === "flexible") {
        setTravelTime({
          ...travelTime,
          month,
        });
      }
    },
    [travelTime]
  );

  const handleLengthChange = useCallback(
    (days: number) => {
      if (travelTime.type === "flexible") {
        setTravelTime({
          ...travelTime,
          length: days,
        });
      }
    },
    [travelTime]
  );

  // Options
  const [personalOptions, setpersonalOptions] = useState<PersonalOption[]>([]);

  const handleAddOption = useCallback(
    (option: PersonalOption) => {
      const optionExists = personalOptions.some(
        (item) => item.type === option.type && item.name === option.name
      );

      if (optionExists) {
        setpersonalOptions(
          personalOptions.filter(
            (item) => !(item.type === option.type && item.name === option.name)
          )
        );
      } else {
        setpersonalOptions([...personalOptions, option]);
      }
    },
    [personalOptions]
  );

  // fỏnav
  const handleNextStep = useCallback(() => {
    setCurrentStep(currentStep + 1);
  }, [currentStep]);

  const handlePrevStep = useCallback(() => {
    setCurrentStep(currentStep - 1);
  }, [currentStep]);

  const handleStartPlan = useCallback(() => {
    setCurrentStep(0);
  }, []);

  const handleBacktoMain = useCallback(() => {
    setCurrentStep(-1);
  }, []);

  return {
    currentStep,
    handleNextStep,
    handlePrevStep,
    handleStartPlan,
    handleBacktoMain,
    isDestinationSelection: currentStep === -1,
    selectedDestinationId,
    handleDestinationSelect,
    budget,
    handleBudgetChange,
    people,
    handlePeopleChange,
    travelTime,
    handleTimeType,
    handleDateChange,
    handleMonthChange,
    handleLengthChange,
    personalOptions,
    handleAddOption,
  };
};
