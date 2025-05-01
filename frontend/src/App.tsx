import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";
import { Routes, Route, useNavigate, useParams } from "react-router-dom";
import { TravelHeader } from "./components/travelHeader";
import { TravelNewPlan } from "./components/newplan/travelNewPlan";
import { TravelPlanListTab } from "./components/planlist/travelList";
import { TravelDetail } from "./components/planlist/travelDetail";

type TabType = "plan-new" | "plan-list";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      gcTime: 1000 * 60 * 5,
    },
  },
});

function TravelDetailRouteWrapper() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  return <TravelDetail travelId={id || ""} onBack={() => navigate("/")} />;
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>("plan-new");

  return (
    <QueryClientProvider client={queryClient}>
      <div>
        <TravelHeader activeTab={activeTab} onTabChange={setActiveTab} />
        <Routes>
          <Route
            path="/"
            element={
              activeTab === "plan-new" ? (
                <TravelNewPlan />
              ) : (
                <TravelPlanListTab />
              )
            }
          />
          <Route path="/trips/:id" element={<TravelDetailRouteWrapper />} />{" "}
        </Routes>
      </div>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
