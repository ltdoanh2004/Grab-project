import { useState, useCallback, useMemo } from "react";
import dayjs from "dayjs";

export function useTimeEdit(initial: string, save: (v: string) => void) {
  const [editing, setEditing] = useState(false);
  const [start, end] = useMemo(() => initial.split(" - "), [initial]);
  const [startTime, setStartTime] = useState(() => dayjs(start, "HH:mm"));
  const [endTime, setEndTime] = useState(() => dayjs(end, "HH:mm"));

  const commit = useCallback(() => {
    setEditing(false);
    save(`${startTime.format("HH:mm")} - ${endTime.format("HH:mm")}`);
  }, [save, startTime, endTime]);

  return {
    editing,
    startTime,
    endTime,
    setStartTime,
    setEndTime,
    begin: () => setEditing(true),
    commit,
  } as const;
}
