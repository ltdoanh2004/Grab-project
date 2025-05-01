import { useEffect, useState } from "react";
import {
  MOCK_TRAVEL_DETAIL,
  MOCK_TRAVEL_PLANS,
} from "../constants/travelPlanConstants";
import {
  TravelActivity,
  TravelDetailData,
  TravelDay,
} from "../types/travelPlan";

export function useTravelDetail(travelId: string) {
  const [travelDetail, setTravelDetail] = useState<TravelDetailData | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setNotFound(false);

    const mockDetail =
      travelId === MOCK_TRAVEL_DETAIL.id
        ? MOCK_TRAVEL_DETAIL
        : (MOCK_TRAVEL_PLANS.find((p) => p.id === travelId) as any);

    if (mockDetail && mockDetail.days) {
      setTimeout(() => {
        if (!ignore) {
          setTravelDetail({ ...mockDetail });
          setLoading(false);
        }
      }, 400);
      return () => {
        ignore = true;
      };
    }

    setTimeout(() => {
      if (!ignore) {
        setNotFound(true);
        setLoading(false);
      }
    }, 400);

    return () => {
      ignore = true;
    };
  }, [travelId]);

  // All handlers below
  const [activeTab, setActiveTab] = useState<string>("itinerary");
  const [activityModalVisible, setActivityModalVisible] = useState(false);
  const [selectedActivity, setSelectedActivity] =
    useState<TravelActivity | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [currentDay, setCurrentDay] = useState<TravelDay | null>(null);
  const [activityToReplace, setActivityToReplace] =
    useState<TravelActivity | null>(null);
  const [activitySearchModalVisible, setActivitySearchModalVisible] =
    useState(false);
  const [dayForNewActivity, setDayForNewActivity] = useState<TravelDay | null>(
    null
  );

  const showActivityDetail = (activity: TravelActivity) => {
    setSelectedActivity(activity);
    setActivityModalVisible(true);
  };

  const toggleEditMode = () => {
    if (isEditMode && travelDetail) {
      const sortedTravelDetail = {
        ...travelDetail,
        days: travelDetail.days.map((day) => ({
          ...day,
          activities: [...day.activities].sort((a, b) => {
            const getStart = (time: string) => {
              const [start] = time.split(" - ");
              const [h, m] = start.split(":").map(Number);
              return h * 60 + m;
            };
            return getStart(a.time) - getStart(b.time);
          }),
        })),
      };
      setTravelDetail(sortedTravelDetail);
    }
    setIsEditMode((v) => !v);
    setShowAISuggestions(false);
    setActivitySearchModalVisible(false);
  };

  const handleReplaceActivity = (day: TravelDay, activity: TravelActivity) => {
    setCurrentDay(day);
    setActivityToReplace(activity);
    setShowAISuggestions(true);
  };

  const handleSelectAISuggestion = (newActivity: TravelActivity) => {
    if (travelDetail && currentDay && activityToReplace) {
      const updatedTravelDetail = { ...travelDetail };
      const dayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === currentDay.day
      );
      if (dayIndex !== -1) {
        const activityIndex = updatedTravelDetail.days[
          dayIndex
        ].activities.findIndex((a) => a.id === activityToReplace.id);

        if (activityIndex !== -1) {
          updatedTravelDetail.days[dayIndex].activities[activityIndex] = {
            ...newActivity,
            id: activityToReplace.id,
            time: activityToReplace.time,
          };
          setTravelDetail(updatedTravelDetail);
        }
      }
      setShowAISuggestions(false);
    }
  };

  const handleDeleteActivity = (day: TravelDay, activity: TravelActivity) => {
    if (!travelDetail) return;
    const updatedTravelDetail = { ...travelDetail };
    const dayIndex = updatedTravelDetail.days.findIndex(
      (d) => d.day === day.day
    );
    if (dayIndex !== -1) {
      updatedTravelDetail.days[dayIndex].activities = updatedTravelDetail.days[
        dayIndex
      ].activities.filter((a) => a.id !== activity.id);
      setTravelDetail(updatedTravelDetail);
    }
  };

  const handleUpdateActivityTime = (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => {
    if (!travelDetail) return;
    const updatedTravelDetail = { ...travelDetail };
    const dayIndex = updatedTravelDetail.days.findIndex(
      (d) => d.day === day.day
    );
    if (dayIndex !== -1) {
      const activityIndex = updatedTravelDetail.days[
        dayIndex
      ].activities.findIndex((a) => a.id === activity.id);

      if (activityIndex !== -1) {
        updatedTravelDetail.days[dayIndex].activities[activityIndex].time =
          newTime;
        setTravelDetail(updatedTravelDetail);
      }
    }
  };

  const handleMoveActivity = (
    fromIndex: number,
    toIndex: number,
    fromDayId: number,
    toDayId: number
  ) => {
    if (!travelDetail) return;
    try {
      const updatedTravelDetail = {
        ...travelDetail,
        days: travelDetail.days.map((day) => ({
          ...day,
          activities: [...day.activities],
        })),
      };

      const fromDayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === fromDayId
      );
      const toDayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === toDayId
      );

      if (fromDayIndex === -1 || toDayIndex === -1) return;

      if (fromDayIndex === toDayIndex) {
        const activities = updatedTravelDetail.days[fromDayIndex].activities;
        [activities[fromIndex], activities[toIndex]] = [
          activities[toIndex],
          activities[fromIndex],
        ];
        const tempTime = activities[fromIndex].time;
        activities[fromIndex].time = activities[toIndex].time;
        activities[toIndex].time = tempTime;
      } else {
        const fromActivities =
          updatedTravelDetail.days[fromDayIndex].activities;
        const toActivities = updatedTravelDetail.days[toDayIndex].activities;

        const fromActivity = fromActivities[fromIndex];
        const toActivity = toActivities[toIndex];

        fromActivities[fromIndex] = toActivity;
        toActivities[toIndex] = fromActivity;

        const tempTime = fromActivities[fromIndex].time;
        fromActivities[fromIndex].time = toActivities[toIndex].time;
        toActivities[toIndex].time = tempTime;
      }

      setTravelDetail(updatedTravelDetail);
    } catch (error) {
      console.error("Error in handleMoveActivity:", error);
    }
  };

  const openAddActivityModal = (day: TravelDay) => {
    setDayForNewActivity(day);
    setActivitySearchModalVisible(true);
  };

  const handleAddCustomActivity = (searchValue: string) => {
    if (travelDetail && dayForNewActivity && searchValue.trim()) {
      const newActivity: TravelActivity = {
        id: `custom-${Date.now()}`,
        time: "12:00 - 14:00",
        type: "attraction",
        name: searchValue,
        location: "Địa điểm tùy chỉnh",
        description: "Hoạt động do người dùng tự thêm",
        imageUrl:
          "https://rosevalleydalat.com/wp-content/uploads/2019/04/doiche.jpg",
        rating: 5,
        price: "Chưa có thông tin",
      };
      const updatedTravelDetail = { ...travelDetail };
      const dayIndex = updatedTravelDetail.days.findIndex(
        (d) => d.day === dayForNewActivity.day
      );
      if (dayIndex !== -1) {
        updatedTravelDetail.days[dayIndex].activities.push(newActivity);
        setTravelDetail(updatedTravelDetail);
      }
      setActivitySearchModalVisible(false);
    }
  };

  return {
    travelDetail,
    loading,
    notFound,
    activeTab,
    setActiveTab,
    activityModalVisible,
    setActivityModalVisible,
    selectedActivity,
    setSelectedActivity,
    isEditMode,
    toggleEditMode,
    showAISuggestions,
    setShowAISuggestions,
    currentDay,
    setCurrentDay,
    activityToReplace,
    setActivityToReplace,
    activitySearchModalVisible,
    setActivitySearchModalVisible,
    dayForNewActivity,
    setDayForNewActivity,
    showActivityDetail,
    handleReplaceActivity,
    handleSelectAISuggestion,
    handleDeleteActivity,
    handleUpdateActivityTime,
    handleMoveActivity,
    openAddActivityModal,
    handleAddCustomActivity,
  };
}
