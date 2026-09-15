import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import SensorList from "./features/sensors/SensorList";


function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-700">
        Smart Greenhouse Dashboard
      </h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <section
        id="sensors"
        className="rounded-lg bg-white p-6 shadow md:col-span-2 lg:col-span-3"
>          <SensorList />
        </section>

        <section
          id="config"
          className="rounded-lg bg-white p-6 shadow"
        >
          <h2 className="text-xl font-semibold text-gray-700">
            Config
          </h2>

          <p className="mt-2 text-gray-500">
            Greenhouse configuration will be available here.
          </p>
        </section>

        <section
          id="automation"
          className="rounded-lg bg-white p-6 shadow"
        >
          <h2 className="text-xl font-semibold text-gray-700">
            Automation
          </h2>

          <p className="mt-2 text-gray-500">
            Automation controls will be available here.
          </p>
        </section>

        <section
          id="overview"
          className="rounded-lg bg-white p-6 shadow"
        >
          <h2 className="text-xl font-semibold text-gray-700">
            Overview
          </h2>

          <p className="mt-2 text-gray-500">
            Greenhouse overview will be available here.
          </p>
        </section>

        <section
          id="controls"
          className="rounded-lg bg-white p-6 shadow"
        >
          <h2 className="text-xl font-semibold text-gray-700">
            Controls
          </h2>

          <p className="mt-2 text-gray-500">
            Greenhouse controls will be available here.
          </p>
        </section>

        <section
          id="events"
          className="rounded-lg bg-white p-6 shadow"
        >
          <h2 className="text-xl font-semibold text-gray-700">
            Events
          </h2>

          <p className="mt-2 text-gray-500">
            Greenhouse events will be available here.
          </p>
        </section>
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