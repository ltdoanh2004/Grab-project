import React, { useState, useEffect } from "react";
import dayjs, { Dayjs } from "dayjs";
import { Card, Typography, Calendar, Row, Col, Button } from "antd";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import { ExactTime } from "../../../types/travelPlan";

const { Text } = Typography;

interface ExactTimeComponentProps {
  timeData: ExactTime;
  onDateChange: (dates: any) => void;
}

export const ExactTimeComponent: React.FC<ExactTimeComponentProps> = ({
  timeData,
  onDateChange,
}) => {
  const startDate = timeData.startDate ? dayjs(timeData.startDate) : null;
  const endDate = timeData.endDate ? dayjs(timeData.endDate) : null;
  const [startMonth, setStartMonth] = useState<Dayjs>(startDate ?? dayjs());
  const [endMonth, setEndMonth] = useState<Dayjs>(
    endDate ?? dayjs().add(1, "month")
  );

  const handleSelect = (date: Dayjs, isEndCalendar = false) => {
    if (!startDate || (startDate && endDate)) {
      onDateChange([date, null]);
    } else {
      onDateChange(
        date.isBefore(startDate) ? [date, startDate] : [startDate, date]
      );
    }
  };

  const handleMonthChange = (isStart: boolean, increment: boolean) => {
    if (isStart) {
      const newStartMonth = increment
        ? startMonth.add(1, "month")
        : startMonth.subtract(1, "month");
      setStartMonth(newStartMonth);
      setEndMonth(newStartMonth.add(1, "month"));
    } else {
      const newEndMonth = increment
        ? endMonth.add(1, "month")
        : endMonth.subtract(1, "month");
      if (
        !increment &&
        newEndMonth.isBefore(startMonth) &&
        !newEndMonth.isSame(startMonth)
      )
        return;
      setEndMonth(newEndMonth);
    }
  };

  const MonthHeader = ({
    value,
    isStart,
  }: {
    value: Dayjs;
    isStart: boolean;
  }) => (
    <div className="flex justify-between items-center mb-2 font-semibold text-md">
      <Button
        icon={<LeftOutlined />}
        type="text"
        onClick={() => handleMonthChange(isStart, false)}
        disabled={
          isStart
            ? value.isSame(dayjs(), "month")
            : value.isSame(startMonth, "month")
        }
      />
      <div className="text-lg">{value.format("MMMM YYYY")}</div>
      <Button
        icon={<RightOutlined />}
        type="text"
        onClick={() => handleMonthChange(isStart, true)}
      />
    </div>
  );

  const renderCalendarCell = (current: Dayjs, isEndCalendar = false) => {
    const isToday = current.isSame(dayjs(), "day");
    const isStartDate = startDate && current.isSame(startDate, "day");
    const isEndDate = endDate && current.isSame(endDate, "day");
    const isInRange =
      startDate &&
      endDate &&
      current.isAfter(startDate, "day") &&
      current.isBefore(endDate, "day");

    const isDisabled =
      isEndCalendar && startDate
        ? current.isBefore(startDate, "day") || current.isBefore(dayjs(), "day")
        : current.isBefore(dayjs(), "day");

    let cellClasses =
      "flex justify-center items-center w-12 mx-auto rounded-full transition-all";

    if (isStartDate || isEndDate) {
      cellClasses += " bg-blue-500 text-white";
    } else if (isInRange) {
      cellClasses += " bg-blue-50";
    } else if (isToday) {
      cellClasses += " border border-blue-500";
    }

    if (isDisabled) {
      cellClasses += " text-gray-300 cursor-not-allowed";
    } else {
      cellClasses += " cursor-pointer hover:bg-gray-50";
    }

    return (
      <div className="relative h-full p-1 font-inter">
        <div className={cellClasses}>{current.date()}</div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-5xl border-0 mx-auto">
      <div className="text-center mb-5">
        <Text type="secondary" className="text-base">
          {startDate && endDate ? (
            <>
              Từ{" "}
              <span className="font-semibold">
                {startDate.format("DD/MM/YYYY")}
              </span>{" "}
              đến{" "}
              <span className="font-semibold">
                {endDate.format("DD/MM/YYYY")}
              </span>
            </>
          ) : startDate ? (
            <>
              Đã chọn{" "}
              <span className="font-semibold">
                {startDate.format("DD/MM/YYYY")}
              </span>
              . Vui lòng chọn ngày về
            </>
          ) : (
            "Vui lòng chọn ngày đi"
          )}
        </Text>
      </div>

      <div className="flex flex-row space-x-8">
        <div className="flex-1 font-['Segoe_UI'] border border-gray-100 rounded-lg p-3 shadow-sm">
          <Calendar
            fullscreen={false}
            onSelect={(date) => handleSelect(date, false)}
            value={startMonth}
            validRange={[dayjs(), dayjs().add(2, "year")]}
            headerRender={(props) => <MonthHeader {...props} isStart={true} />}
            mode="month"
            fullCellRender={(date) => renderCalendarCell(date, false)}
            className="text-sm"
          />
        </div>
        <div className="flex-1 font-['Segoe_UI'] border border-gray-100 rounded-lg p-3 shadow-sm">
          <Calendar
            fullscreen={false}
            onSelect={(date) => handleSelect(date, true)}
            value={endMonth}
            validRange={[dayjs(), dayjs().add(2, "year")]}
            headerRender={(props) => <MonthHeader {...props} isStart={false} />}
            mode="month"
            fullCellRender={(date) => renderCalendarCell(date, true)}
            className="text-sm"
          />
        </div>
      </div>
    </div>
  );
};
