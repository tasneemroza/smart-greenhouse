import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./index.css";

import SensorList from "./features/sensors/SensorList";
import DeviceList from "./components/devices/DeviceList";
import LocationConfigWizard from "./components/config/LocationConfigWizard";
import AutomationPanel from "./features/automation/AutomationPanel";
import OverviewPanel from "./features/overview/OverviewPanel";

function Dashboard() {
  return (
    <div className="min-h-screen bg-[#F6F7F2] px-4 py-6 text-[#293B32] sm:px-6 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 overflow-hidden rounded-3xl border border-[#DDE5DC] bg-[#E7EFE6] p-5 sm:p-8">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#315747] text-xl text-white"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M12 21V10"/><path d="M12 15C8 15 4 12 4 6c5 0 8 3 8 9Z"/><path d="M12 11c0-5 3-8 8-8 0 5-3 8-8 8Z"/></svg></div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#6F7C73]">
                Monitoring system
              </p>
              <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#315747] sm:text-3xl">
                Smart Greenhouse
              </h1>
            </div>
          </div>

          <p className="mt-5 max-w-2xl text-sm leading-6 text-[#52675A] sm:text-base">
            Monitor and manage your greenhouse devices from one place.
          </p>

          <nav className="mt-6 flex flex-wrap gap-2" aria-label="Dashboard sections">
            <a href="#sensors" className="rounded-full bg-[#315747] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#264637]">
              Sensors
            </a>
            <a href="#devices" className="rounded-full border border-[#DDE5DC] bg-white px-4 py-2 text-sm font-medium text-[#315747] transition hover:bg-[#F6F7F2]">
              Devices
            </a>
            <a href="#config" className="rounded-full border border-[#DDE5DC] bg-white px-4 py-2 text-sm font-medium text-[#315747] transition hover:bg-[#F6F7F2]">
              Configuration
            </a>
          </nav>
        </header>

        <main className="space-y-6">
          <section id="sensors" className="scroll-mt-6 rounded-2xl border border-[#DDE5DC] bg-white p-4 shadow-[0_3px_16px_rgba(41,59,50,0.04)] sm:p-6">
            <div className="mb-5">
              <h2 className="text-xl font-bold tracking-tight text-[#293B32]">Sensors</h2>
              <p className="mt-1 text-sm text-[#6F7C73]">Current readings, sampling intervals, and tracking.</p>
            </div>
            <SensorList />
          </section>

          <section id="devices" className="scroll-mt-6 rounded-2xl border border-[#DDE5DC] bg-white p-4 shadow-[0_3px_16px_rgba(41,59,50,0.04)] sm:p-6">
            <div className="mb-5">
              <h2 className="text-xl font-bold tracking-tight text-[#293B32]"> Devices</h2>
            </div>
            <DeviceList />
          </section>

          <section id="config" className="scroll-mt-6 rounded-2xl border border-[#DDE5DC] bg-white p-4 shadow-[0_3px_16px_rgba(41,59,50,0.04)] sm:p-6">
            <div className="mb-5">
              <h2 className="text-xl font-bold tracking-tight text-[#293B32]">Configuration</h2>
              <p className="mt-1 text-sm text-[#6F7C73]">Manage your existing greenhouse locations and zones.</p>
            </div>
            <LocationConfigWizard />
          </section>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <section id="automation" className="rounded-2xl border border-[#DDE5DC] bg-white p-5 shadow-[0_3px_16px_rgba(41,59,50,0.04)]">
              <AutomationPanel />
            </section>
            <section id="overview" className="rounded-2xl border border-[#DDE5DC] bg-white p-5 shadow-[0_3px_16px_rgba(41,59,50,0.04)]">
              <h2 className="text-base font-semibold text-[#315747]">Overview</h2>
              <OverviewPanel />
            </section>
            <section id="controls" className="rounded-2xl border border-[#DDE5DC] bg-white p-5 shadow-[0_3px_16px_rgba(41,59,50,0.04)]">
              <h2 className="text-base font-semibold text-[#315747]">Controls</h2>
              <p className="mt-2 text-sm leading-6 text-[#6F7C73]">Greenhouse controls will be available here.</p>
            </section>
            <section id="events" className="rounded-2xl border border-[#DDE5DC] bg-white p-5 shadow-[0_3px_16px_rgba(41,59,50,0.04)]">
              <h2 className="text-base font-semibold text-[#315747]">Events</h2>
              <p className="mt-2 text-sm leading-6 text-[#6F7C73]">Greenhouse events will be available here.</p>
            </section>
          </div>
        </main>

        <footer className="mt-8 border-t border-[#DDE5DC] py-5 text-center text-xs text-[#6F7C73]">
           Smart Greenhouse · Monitoring system
        </footer>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
