import React from "react";
import { Typography, Button, Card, InputNumber } from "antd";
import { NumOfPeople } from "../../../types/travelPlan";

const { Title } = Typography;

interface PeopleSelectionProps {
  people: NumOfPeople;
  onPeopleChange: (people: NumOfPeople) => void;
}

export const PeopleSelection: React.FC<PeopleSelectionProps> = ({
  people,
  onPeopleChange,
}) => {
  const handlePeopleChange = (type: keyof NumOfPeople, value: number) => {
    onPeopleChange({ ...people, [type]: value });
  };

  return (
    <Card className="mb-6 shadow-sm">
      <Title level={4}>Số lượng người tham gia chuyến di</Title>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <div className="font-semibold">Người lớn</div>
            <div className="text-gray-500 text-sm">Từ 13 tuổi trở lên</div>
          </div>
          <div className="flex items-center">
            <Button
              icon="-"
              onClick={() =>
                handlePeopleChange("adults", Math.max(1, people.adults - 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
              disabled={people.adults <= 1}
            />
            <InputNumber
              min={1}
              max={10}
              value={people.adults}
              onChange={(value) => handlePeopleChange("adults", value || 1)}
              controls={false}
              className="w-12 text-center mx-2"
            />
            <Button
              icon="+"
              onClick={() =>
                handlePeopleChange("adults", Math.min(10, people.adults + 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
            />
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <div className="font-semibold">Trẻ em</div>
            <div className="text-gray-500 text-sm">Từ 2-12 tuổi</div>
          </div>
          <div className="flex items-center">
            <Button
              icon="-"
              onClick={() =>
                handlePeopleChange("children", Math.max(0, people.children - 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
              disabled={people.children <= 0}
            />
            <InputNumber
              min={0}
              max={10}
              value={people.children}
              onChange={(value) => handlePeopleChange("children", value || 0)}
              controls={false}
              className="w-12 text-center mx-2"
            />
            <Button
              icon="+"
              onClick={() =>
                handlePeopleChange(
                  "children",
                  Math.min(10, people.children + 1)
                )
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
            />
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <div className="font-semibold">Em bé</div>
            <div className="text-gray-500 text-sm">Dưới 2 tuổi</div>
          </div>
          <div className="flex items-center">
            <Button
              icon="-"
              onClick={() =>
                handlePeopleChange("infants", Math.max(0, people.infants - 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
              disabled={people.infants <= 0}
            />
            <InputNumber
              min={0}
              max={5}
              value={people.infants}
              onChange={(value) => handlePeopleChange("infants", value || 0)}
              controls={false}
              className="w-12 text-center mx-2"
            />
            <Button
              icon="+"
              onClick={() =>
                handlePeopleChange("infants", Math.min(5, people.infants + 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
            />
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <div className="font-semibold">Thú cưng</div>
            <div className="text-gray-500 text-sm">
              Số lượng thú cưng đi cùng
            </div>
          </div>
          <div className="flex items-center">
            <Button
              icon="-"
              onClick={() =>
                handlePeopleChange("pets", Math.max(0, people.pets - 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
              disabled={people.pets <= 0}
            />
            <InputNumber
              min={0}
              max={3}
              value={people.pets}
              onChange={(value) => handlePeopleChange("pets", value || 0)}
              controls={false}
              className="w-12 text-center mx-2"
            />
            <Button
              icon="+"
              onClick={() =>
                handlePeopleChange("pets", Math.min(3, people.pets + 1))
              }
              className="flex items-center justify-center h-8 w-8 rounded-full"
            />
          </div>
        </div>
      </div>
    </Card>
  );
};
