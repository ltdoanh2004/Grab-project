import { useState, useCallback, useEffect } from "react";
import {
  TravelTime,
  PersonalOption,
  Budget,
  NumOfPeople,
} from "../types/travelPlan";
import { BUDGET_RANGES } from "../constants/travelPlanConstants";
import { getUserTrips } from "../services/travelPlanApi";
import { useAuth } from "./useAuth";

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

export function useTravelPlans() {
  const [travelPlans, setTravelPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    let ignore = false;
    
    const fetchTravelPlans = async () => {
      if (!isLoggedIn) {
        setTravelPlans([]);
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        setError(null);
        
        const response = await getUserTrips();
        
        if (!ignore) {
          if (response && response.data) {
            setTravelPlans(response.data);
          } else {
            setTravelPlans([]);
          }
          setLoading(false);
        }
      } catch (err) {
        console.error("Error fetching travel plans:", err);
        if (!ignore) {
          setError("Failed to load travel plans. Please try again later.");
          setLoading(false);
        }
      }
    };

    fetchTravelPlans();
    
    return () => {
      ignore = true;
    };
  }, [isLoggedIn]);

  return {
    travelPlans,
    loading,
    error,
    refetch: async () => {
      setLoading(true);
      try {
        const response = await getUserTrips();
        if (response && response.data) {
          setTravelPlans(response.data);
        }
        setLoading(false);
      } catch (err) {
        setError("Failed to refresh travel plans. Please try again later.");
        setLoading(false);
      }
    }
  };
}
