import { useEffect, useState } from "react";
import {
  MOCK_TRAVEL_DETAIL,
  MOCK_TRAVEL_DETAIL_2,
  MOCK_TRAVEL_PLANS,
} from "../constants/travelPlanConstants";
import {
  TravelActivity,
  TravelDetailData,
  TravelDay,
  TravelSegment,
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
    if (travelId === "temp123") {
      const local = localStorage.getItem("tripPlan_temp123");
      if (local) {
        setTravelDetail(JSON.parse(local));
        setLoading(false);
        return;
      }
    }
    const mockDetail =
      travelId === MOCK_TRAVEL_DETAIL.id
        ? MOCK_TRAVEL_DETAIL
        : travelId === MOCK_TRAVEL_DETAIL_2.id
        ? MOCK_TRAVEL_DETAIL_2
        : (MOCK_TRAVEL_PLANS.find((p) => p.id === travelId) as any);

    if (mockDetail && mockDetail.plan_by_day) {
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

  // Helper: flatten all activities for a day (from segments)
  const getAllActivitiesOfDay = (day: TravelDay): TravelActivity[] => {
    return day.segments.flatMap((segment: TravelSegment) => segment.activities);
  };

  // Helper: update activities in a day (by segments)
  const updateActivitiesOfDay = (
    day: TravelDay,
    newActivities: TravelActivity[]
  ) => {
    // Distribute newActivities back into segments by original segment lengths
    let idx = 0;
    const newSegments = day.segments.map((segment) => {
      const segActs = segment.activities.length;
      const acts = newActivities.slice(idx, idx + segActs);
      idx += segActs;
      return { ...segment, activities: acts };
    });
    return { ...day, segments: newSegments };
  };

  const toggleEditMode = () => {
    if (isEditMode && travelDetail) {
      // Sort activities in each segment by start_time
      const sortedTravelDetail = {
        ...travelDetail,
        plan_by_day: travelDetail.plan_by_day.map((day) => ({
          ...day,
          segments: day.segments.map((segment) => ({
            ...segment,
            activities: [...segment.activities].sort((a, b) => {
              const getStart = (time: string) => {
                const [h, m] = a.start_time.split(":").map(Number);
                return h * 60 + m;
              };
              return getStart(a.start_time) - getStart(b.start_time);
            }),
          })),
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
      updatedTravelDetail.plan_by_day = updatedTravelDetail.plan_by_day.map(
        (day) => {
          if (day.date !== currentDay.date) return day;
          return {
            ...day,
            segments: day.segments.map((segment) => ({
              ...segment,
              activities: segment.activities.map((a) =>
                a.id === activityToReplace.id
                  ? { ...newActivity, id: activityToReplace.id }
                  : a
              ),
            })),
          };
        }
      );
      setTravelDetail(updatedTravelDetail);
      setShowAISuggestions(false);
    }
  };

  const handleDeleteActivity = (day: TravelDay, activity: TravelActivity) => {
    if (!travelDetail) return;
    const updatedTravelDetail = { ...travelDetail };
    updatedTravelDetail.plan_by_day = updatedTravelDetail.plan_by_day.map(
      (d) => {
        if (d.date !== day.date) return d;
        return {
          ...d,
          segments: d.segments.map((segment) => ({
            ...segment,
            activities: segment.activities.filter((a) => a.id !== activity.id),
          })),
        };
      }
    );
    setTravelDetail(updatedTravelDetail);
  };

  const handleUpdateActivityTime = (
    day: TravelDay,
    activity: TravelActivity,
    newTime: string
  ) => {
    if (!travelDetail) return;
    const [start_time, end_time] = newTime.split(" - ");
    const updatedTravelDetail = { ...travelDetail };
    updatedTravelDetail.plan_by_day = updatedTravelDetail.plan_by_day.map(
      (d) => {
        if (d.date !== day.date) return d;
        return {
          ...d,
          segments: d.segments.map((segment) => ({
            ...segment,
            activities: segment.activities.map((a) =>
              a.id === activity.id
                ? {
                    ...a,
                    start_time: start_time || a.start_time,
                    end_time: end_time || a.end_time,
                  }
                : a
            ),
          })),
        };
      }
    );
    setTravelDetail(updatedTravelDetail);
  };

  // Move activity between segments/days
  const handleMoveActivity = (
    fromIndex: number,
    toIndex: number,
    fromDayDate: string,
    toDayDate: string
  ) => {
    if (!travelDetail) return;
    const updatedTravelDetail = { ...travelDetail };
    const fromDayIdx = updatedTravelDetail.plan_by_day.findIndex(
      (d) => d.date === fromDayDate
    );
    const toDayIdx = updatedTravelDetail.plan_by_day.findIndex(
      (d) => d.date === toDayDate
    );
    if (fromDayIdx === -1 || toDayIdx === -1) return;

    // Flatten activities for both days
    const fromDay = updatedTravelDetail.plan_by_day[fromDayIdx];
    const toDay = updatedTravelDetail.plan_by_day[toDayIdx];
    let fromActs = getAllActivitiesOfDay(fromDay);
    let toActs = getAllActivitiesOfDay(toDay);

    // Move activity
    const [moved] = fromActs.splice(fromIndex, 1);
    toActs.splice(toIndex, 0, moved);

    // Update days
    updatedTravelDetail.plan_by_day[fromDayIdx] = updateActivitiesOfDay(
      fromDay,
      fromActs
    );
    updatedTravelDetail.plan_by_day[toDayIdx] = updateActivitiesOfDay(
      toDay,
      toActs
    );

    setTravelDetail(updatedTravelDetail);
  };

  const openAddActivityModal = (day: TravelDay) => {
    setDayForNewActivity(day);
    setActivitySearchModalVisible(true);
  };

  const handleAddCustomActivity = (searchValue: string) => {
    if (travelDetail && dayForNewActivity && searchValue.trim()) {
      // Add to first segment by default
      const newActivity: TravelActivity = {
        id: `custom-${Date.now()}`,
        type: "attraction",
        name: searchValue,
        start_time: "12:00",
        end_time: "14:00",
        description: "Hoạt động do người dùng tự thêm",
        rating: 5,
      };
      const updatedTravelDetail = { ...travelDetail };
      updatedTravelDetail.plan_by_day = updatedTravelDetail.plan_by_day.map(
        (d) => {
          if (d.date !== dayForNewActivity.date) return d;
          return {
            ...d,
            segments: d.segments.map((segment, idx) =>
              idx === 0
                ? {
                    ...segment,
                    activities: [...segment.activities, newActivity],
                  }
                : segment
            ),
          };
        }
      );
      setTravelDetail(updatedTravelDetail);
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
    setTravelDetail,
  };
}
