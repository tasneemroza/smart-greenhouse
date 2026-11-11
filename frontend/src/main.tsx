import {
  LayoutDashboard,
  Activity,
  Cpu,
  Settings,
  History,
  Workflow,
  SlidersHorizontal,
  Bell,
} from "lucide-react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  NavLink,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import "./index.css";

import SensorList from "./features/sensors/SensorList";
import DeviceList from "./components/devices/DeviceList";
import LocationConfigWizard from "./components/config/LocationConfigWizard";
import AutomationPanel from "./features/automation/AutomationPanel";
import OverviewPanel from "./features/overview/OverviewPanel";
import ExecutionLog from "./features/actuators/ExecutionLog";

const navigation = [
  { label: "Overview", path: "/overview", icon: LayoutDashboard },
  { label: "Sensors", path: "/sensors", icon: Activity },
  { label: "Devices", path: "/devices", icon: Cpu },
  { label: "Configuration", path: "/configuration", icon: Settings },
  { label: "Actuator Logs", path: "/actuator-logs", icon: History },
  { label: "Automation", path: "/automation", icon: Workflow },
  { label: "Controls", path: "/controls", icon: SlidersHorizontal },
  { label: "Events", path: "/events", icon: Bell },
];

function Page({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-[#D7E5E3] bg-white shadow-[0_4px_24px_rgba(38,59,64,0.045)]">
      <div className="border-b border-[#E4ECE9] bg-[#FBFCFB] px-5 py-5 sm:px-7">
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#B98C72]">
          Greenhouse Management
        </p>
        <h2 className="text-2xl font-semibold tracking-tight text-[#263B40]">
          {title}
        </h2>
        {description && (
          <p className="mt-2 text-sm leading-6 text-[#68797B]">
            {description}
          </p>
        )}
      </div>
      <div className="min-w-0 p-5 sm:p-7">
        {children}
      </div>
    </section>
  );
}

function DashboardLayout() {
  return (
    <div className="min-h-screen bg-[#ECF1F0] text-[#293C40]">
      <header className="border-b border-[#263B40] bg-[#263B40]">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-5 py-5 lg:px-8">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-[#66817E] bg-[#344A4F] text-white">
            <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 21V10" />
              <path d="M12 15C8 15 4 12 4 6c5 0 8 3 8 9Z" />
              <path d="M12 11c0-5 3-8 8-8 0 5-3 8-8 8Z" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#D5AD92]">
              Smart Monitoring Platform
            </p>
            <h1 className="mt-1 text-xl font-semibold text-white sm:text-2xl">
              Smart Greenhouse
            </h1>
          </div>
          <div className="ml-auto hidden rounded-full border border-[#66817E] bg-[#344A4F] px-4 py-2 text-xs text-[#D7E5E3] sm:block">
            IoT Control Center
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-7 sm:px-6 lg:grid-cols-[245px_minmax(0,1fr)] lg:px-8">
        <aside className="self-start rounded-2xl border border-[#D7E5E3] bg-white p-3 shadow-sm lg:sticky lg:top-6">
          <div className="mb-3 border-b border-[#E4ECE9] px-3 pb-4 pt-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#B98C72]">
              Workspace
            </p>
            <p className="mt-1 text-sm font-medium text-[#344A4F]">
              Main Navigation
            </p>
          </div>

          <nav aria-label="Main navigation" className="flex flex-wrap gap-2 lg:flex-col">
            {navigation.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 rounded-xl border border-[#344A4F] bg-[#344A4F] px-4 py-3 text-sm font-medium text-white shadow-sm"
                    : "flex items-center gap-3 rounded-xl border border-transparent bg-[#F6F8F7] px-4 py-3 text-sm font-medium text-[#52666A] transition-colors hover:bg-[#E7EEEC]"
                }
              >
                <item.icon size={18} strokeWidth={1.8} aria-hidden="true" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-5 hidden border-t border-[#E4ECE9] px-3 pt-4 lg:block">
            <p className="text-xs leading-5 text-[#68797B]">
              Monitor sensors, manage devices, and configure greenhouse automation.
            </p>
          </div>
        </aside>

        <main className="min-w-0">
          <Routes>
            <Route path="/overview" element={
              <Page title="Overview" description="Your greenhouse monitoring and management overview.">
                <OverviewPanel />
              </Page>
            } />

            <Route path="/sensors" element={
              <Page title="Sensors" description="Monitor readings, sampling intervals, and sensor tracking.">
                <SensorList />
              </Page>
            } />

            <Route path="/devices" element={
              <Page title="Devices" description="Manage simulation devices and edge hardware.">
                <DeviceList />
              </Page>
            } />

            <Route path="/configuration" element={
              <Page title="Configuration" description="Manage greenhouse locations, zones, and watering schedules.">
                <LocationConfigWizard />
              </Page>
            } />

            <Route path="/actuator-logs" element={
              <Page title="Actuator Logs">
                <ExecutionLog />
              </Page>
            } />

            <Route path="/automation" element={
              <Page title="Automation">
                <AutomationPanel />
              </Page>
            } />

            <Route path="/controls" element={
              <Page title="Controls">
                <p className="text-sm text-[#68797B]">
                  Greenhouse controls will be available here.
                </p>
              </Page>
            } />

            <Route path="/events" element={
              <Page title="Events">
                <p className="text-sm text-[#68797B]">
                  Greenhouse events will be available here.
                </p>
              </Page>
            } />

            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/dashboard" element={<Navigate to="/overview" replace />} />
            <Route path="*" element={<Navigate to="/overview" replace />} />
          </Routes>
        </main>
      </div>

      <footer className="mx-auto max-w-7xl border-t border-[#D7E5E3] px-6 py-5 text-center text-xs text-[#68797B]">
        Smart Greenhouse - Monitoring System
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <DashboardLayout />
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);