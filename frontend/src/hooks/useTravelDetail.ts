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
import apiClient from "../services/apiService";
import { getActivityDetail } from "../services/travelPlanApi";

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
    
    console.log(`Looking for trip with ID: ${travelId}`);
    
    const userInputKey = `userInput_${travelId}`;
    const storedUserInput = localStorage.getItem(userInputKey);
    if (storedUserInput) {
      try {
        const parsedUserInput = JSON.parse(storedUserInput);
        console.log(`[UserInput] Found stored user input for trip ${travelId}:`, parsedUserInput);
      } catch (error) {
        console.error(`Error parsing user input from localStorage for trip ${travelId}:`, error);
      }
    } else {
      console.log(`[UserInput] No stored user input found for trip ${travelId}`);
    }
    
    const fetchTripDetails = async () => {
      try {
        const response = await apiClient.get(`/trip/${travelId}`);
        
        if (response.data && response.data.data) {
          const apiTripData = response.data.data;
          
          const localData = localStorage.getItem(`tripPlan_${travelId}`);
          let localDailyTips: Record<string, string[]> = {};
          
          if (localData) {
            try {
              const parsedLocalData = JSON.parse(localData);
              
              if (parsedLocalData && parsedLocalData.plan_by_day) {
                parsedLocalData.plan_by_day.forEach((day: any, index: number) => {
                  if (day.daily_tips && day.daily_tips.length > 0) {
                    localDailyTips[day.date] = day.daily_tips;
                  }
                });
              }
            } catch (error) {
              console.error("Error parsing trip data from localStorage:", error);
            }
          }
          
          const processedTripData = { ...apiTripData };
          
          const enrichedDays = await Promise.all(
            apiTripData.plan_by_day.map(async (day: any) => {
              const enrichedSegments = await Promise.all(
                day.segments.map(async (segment: any) => {
                  const enrichedActivities = await Promise.all(
                    segment.activities.map(async (activity: any) => {
                      try {
                        const detailData = await getActivityDetail(activity.type, activity.id);
                        
                        let processedImageUrls: string[] = [];
                        if (detailData.image_urls && detailData.image_urls.length > 0) {
                          if (typeof detailData.image_urls[0] === 'string' && detailData.image_urls[0].includes(',')) {
                            processedImageUrls = detailData.image_urls[0]
                              .split(',')
                              .map(url => url.trim());
                          } else {
                            processedImageUrls = detailData.image_urls;
                          }
                        }
                        
                        return {
                          ...activity,
                          name: detailData.name || activity.name,
                          description: activity.description || detailData.description,
                          address: detailData.address,
                          location: detailData.location,
                          opening_hours: detailData.opening_hours,
                          price: detailData.price,
                          rating: detailData.rating,
                          image_urls: processedImageUrls,
                          image_url: processedImageUrls.length > 0 ? processedImageUrls[0] : undefined,
                          additional_info: detailData.additional_info,
                          url: detailData.url
                        };
                      } catch (error) {
                        console.error(`Error fetching details for ${activity.type} with ID ${activity.id}:`, error);
                        return activity;
                      }
                    })
                  );
                  
                  return {
                    ...segment,
                    activities: enrichedActivities
                  };
                })
              );
              
              return {
                ...day,
                segments: enrichedSegments,
                daily_tips: localDailyTips[day.date] || []
              };
            })
          );
          
          processedTripData.plan_by_day = enrichedDays;
          
          setTravelDetail(processedTripData);
          setLoading(false);
        } else {
          setNotFound(true);
          setLoading(false);
        }
      } catch (error) {
        console.error(`Error fetching trip ${travelId} from API:`, error);
        
        const localData = localStorage.getItem(`tripPlan_${travelId}`);
        
        if (localData) {
          try {
            const parsedData = JSON.parse(localData);
            console.log("Parsed trip data from localStorage:", parsedData);
            
            if (parsedData && parsedData.plan_by_day) {
              setTravelDetail(parsedData);
              setLoading(false);
              return;
            }
          } catch (error) {
            console.error("Error parsing trip data from localStorage:", error);
          }
        }
        
        const mockDetail =
          travelId === MOCK_TRAVEL_DETAIL.id
            ? MOCK_TRAVEL_DETAIL
            : travelId === MOCK_TRAVEL_DETAIL_2.id
            ? MOCK_TRAVEL_DETAIL_2
            : (MOCK_TRAVEL_PLANS.find((p) => p.id === travelId) as any);

        if (mockDetail && mockDetail.plan_by_day) {
          console.log(`Falling back to mock data for trip ID: ${travelId}`);
          setTimeout(() => {
            if (!ignore) {
              setTravelDetail({ ...mockDetail });
              setLoading(false);
            }
          }, 400);
          return;
        }
        
        setNotFound(true);
        setLoading(false);
      }
    };
    
    fetchTripDetails();

    return () => {
      ignore = true;
    };
  }, [travelId]);

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

  const getAllActivitiesOfDay = (day: TravelDay): TravelActivity[] => {
    return day.segments.flatMap((segment: TravelSegment) => segment.activities);
  };

  const updateActivitiesOfDay = (
    day: TravelDay,
    newActivities: TravelActivity[]
  ) => {
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
      const sortedTravelDetail = {
        ...travelDetail,
        plan_by_day: travelDetail.plan_by_day.map((day) => ({
          ...day,
          segments: day.segments.map((segment) => ({
            ...segment,
            activities: [...segment.activities].sort((a, b) => {
              const getTimeInMinutes = (time: string) => {
                if (!time) return 0;
                const [h, m] = time.split(":").map(Number);
                return h * 60 + (m || 0);
              };
              return getTimeInMinutes(a.start_time) - getTimeInMinutes(b.start_time);
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
            segments: day.segments.map((segment) => {
              const updatedActivities = segment.activities.map((a) =>
                a.id === activityToReplace.id
                  ? { 
                      ...newActivity, 
                      id: activityToReplace.id,
                      start_time: activityToReplace.start_time || newActivity.start_time,
                      end_time: activityToReplace.end_time || newActivity.end_time 
                    }
                  : a
              );
              
              return {
                ...segment,
                activities: updatedActivities.sort((a, b) => {
                  const getTimeInMinutes = (time: string) => {
                    if (!time) return 0;
                    const [h, m] = time.split(":").map(Number);
                    return h * 60 + (m || 0);
                  };
                  return getTimeInMinutes(a.start_time) - getTimeInMinutes(b.start_time);
                }),
              };
            }),
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
          segments: d.segments.map((segment) => {
            const updatedActivities = segment.activities.map((a) =>
              a.id === activity.id
                ? {
                    ...a,
                    start_time: start_time || a.start_time,
                    end_time: end_time || a.end_time,
                  }
                : a
            );
            
            return {
              ...segment,
              activities: updatedActivities.sort((a, b) => {
                const getTimeInMinutes = (time: string) => {
                  if (!time) return 0;
                  const [h, m] = time.split(":").map(Number);
                  return h * 60 + (m || 0);
                };
                return getTimeInMinutes(a.start_time) - getTimeInMinutes(b.start_time);
              }),
            };
          }),
        };
      }
    );
    setTravelDetail(updatedTravelDetail);
  };

  const handleMoveActivity = (
    fromDayIndex: number,
    fromSegment: string,
    fromActivityIndex: number,
    toDayIndex: number,
    toSegment: string,
    toActivityIndex: number
  ) => {
    if (!travelDetail) return;
    const updatedTravelDetail = { ...travelDetail };
    const fromDay = updatedTravelDetail.plan_by_day[fromDayIndex];
    const toDay = updatedTravelDetail.plan_by_day[toDayIndex];
    
    if (!fromDay || !toDay) return;
    
    const fromSegmentObj = fromDay.segments.find(s => s.time_of_day === fromSegment);
    const toSegmentObj = toDay.segments.find(s => s.time_of_day === toSegment);
    
    if (!fromSegmentObj || !toSegmentObj) return;
    
    const [movedActivity] = fromSegmentObj.activities.splice(fromActivityIndex, 1);
    
    toSegmentObj.activities.splice(toActivityIndex, 0, movedActivity);
    
    toSegmentObj.activities.sort((a, b) => {
      const getTimeInMinutes = (time: string) => {
        if (!time) return 0;
        const [h, m] = time.split(":").map(Number);
        return h * 60 + (m || 0);
      };
      return getTimeInMinutes(a.start_time) - getTimeInMinutes(b.start_time);
    });
    
    setTravelDetail(updatedTravelDetail);
  };

  const openAddActivityModal = (day: TravelDay) => {
    setDayForNewActivity(day);
    setActivitySearchModalVisible(true);
  };

  const handleAddCustomActivity = (searchValue: string) => {
    if (travelDetail && dayForNewActivity && searchValue.trim()) {
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
            segments: d.segments.map((segment, idx) => {
              if (idx === 0) {
                const updatedActivities = [...segment.activities, newActivity];
                return {
                  ...segment,
                  activities: updatedActivities.sort((a, b) => {
                    const getTimeInMinutes = (time: string) => {
                      if (!time) return 0;
                      const [h, m] = time.split(":").map(Number);
                      return h * 60 + (m || 0);
                    };
                    return getTimeInMinutes(a.start_time) - getTimeInMinutes(b.start_time);
                  }),
                };
              }
              return segment;
            }),
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
