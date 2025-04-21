import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";
import { TravelPlanList } from "./components/travelPlanList";
import { TravelHeader } from "./components/travelHeader";
import { TravelNewPlan } from "./components/newplan/travelNewPlan";
type TabType = "plan-new" | "plan-list";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      gcTime: 1000 * 60 * 5,
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState<TabType>("plan-new");

  return (
    <QueryClientProvider client={queryClient}>
      <div>
        <TravelHeader activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === "plan-new" ? (
          <TravelNewPlan />
        ) : (
          <div className="p-8 text-center">
            <h2 className="text-2xl">Lịch trình cuar banj</h2>
            <p></p>
          </div>
        )}
      </div>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
