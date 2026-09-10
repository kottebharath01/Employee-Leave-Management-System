import { useState } from "react";
import EmployeesTab from "./EmployeesTab";
import LeaveTypesTab from "./LeaveTypesTab";
import LeaveBalancesTab from "./LeaveBalancesTab";
import HolidaysTab from "./HolidaysTab";

const TABS = [
  { key: "employees", label: "Employees", component: EmployeesTab },
  { key: "leave-types", label: "Leave Types", component: LeaveTypesTab },
  { key: "balances", label: "Leave Balances", component: LeaveBalancesTab },
  { key: "holidays", label: "Holidays", component: HolidaysTab },
];

export default function HrPage() {
  const [activeTab, setActiveTab] = useState("employees");
  const ActiveComponent = TABS.find((t) => t.key === activeTab).component;

  return (
    <div>
      <h1>HR Panel</h1>
      <div className="tab-bar">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`tab-button ${activeTab === t.key ? "active" : ""}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <ActiveComponent />
    </div>
  );
}
