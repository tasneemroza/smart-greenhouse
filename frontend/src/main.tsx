import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";
import "./index.css";

import SensorList from "./features/sensors/SensorList";
import DeviceList from "./components/devices/DeviceList";

function Dashboard() {
  return (
    <div className="min-h-screen bg-green-50 px-4 py-8 text-gray-800 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight text-green-900">
            Smart Greenhouse
          </h1>

          <p className="mt-2 text-sm text-gray-600">
            Monitor and manage your greenhouse devices
          </p>
        </header>

        <div className="space-y-6">
          <section
            id="sensors"
            className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-5 text-xl font-semibold text-gray-800">
              Sensors
            </h2>

            <SensorList />
          </section>

          <section
            id="devices"
            className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-5 text-xl font-semibold text-gray-800">
              Devices
            </h2>

            <DeviceList />
          </section>

          <div className="grid gap-6 md:grid-cols-3">
            <section
              id="config"
              className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-800">
                Config
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Greenhouse configuration will be available here.
              </p>
            </section>

            <section
              id="automation"
              className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-800">
                Automation
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Automation controls will be available here.
              </p>
            </section>

            <section
              id="overview"
              className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-800">
                Overview
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Greenhouse overview will be available here.
              </p>
            </section>

            <section
              id="controls"
              className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-800">
                Controls
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Greenhouse controls will be available here.
              </p>
            </section>

            <section
              id="events"
              className="rounded-2xl border border-green-100 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-800">
                Events
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Greenhouse events will be available here.
              </p>
            </section>
          </div>
        </div>
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