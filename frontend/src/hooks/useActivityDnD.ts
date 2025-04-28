import { useRef } from "react";
import { useDrag, useDrop } from "react-dnd";

import { ItemTypes, DragItem } from "../types/travelPlan";

export function useActivityDnD(
  isEditMode: boolean,
  dragIndex: number,
  dayId: number,
  move: (from: number, to: number, dayId: number) => void
) {
  const ref = useRef<HTMLDivElement>(null);

  const [{ isDragging }, drag] = useDrag(
    () => ({
      type: ItemTypes.ACTIVITY,
      canDrag: () => isEditMode,
      item: {
        id: `${dayId}-${dragIndex}`,
        dayId,
        index: dragIndex,
        type: ItemTypes.ACTIVITY,
      },
      collect: (m) => ({ isDragging: m.isDragging() }),
    }),
    [isEditMode, dragIndex, dayId]
  );

  const [{ isOver }, drop] = useDrop<DragItem, void, { isOver: boolean }>(
    () => ({
      accept: ItemTypes.ACTIVITY,
      canDrop: () => isEditMode,
      collect: (m) => ({ isOver: m.isOver() }),
      hover: (item) => {
        if (!ref.current) return;
        if (item.dayId !== dayId || item.index === dragIndex) return;
        move(item.index, dragIndex, dayId);
        item.index = dragIndex;
      },
    }),
    [isEditMode, dragIndex, dayId, move]
  );

  drag(drop(ref));
  return { ref, isDragging, isOver } as const;
}
