import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-700">
        Smart Greenhouse
      </h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <section id="sensors" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Sensors</h2>
          <p className="mt-2 text-gray-500">
            Monitor greenhouse sensor data.
          </p>
        </section>

        <section id="config" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Config</h2>
          <p className="mt-2 text-gray-500">
            Configure greenhouse settings.
          </p>
        </section>

        <section id="automation" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Automation</h2>
          <p className="mt-2 text-gray-500">
            Manage automatic greenhouse actions.
          </p>
        </section>

        <section id="overview" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Overview</h2>
          <p className="mt-2 text-gray-500">
            View the greenhouse overview.
          </p>
        </section>

        <section id="controls" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Controls</h2>
          <p className="mt-2 text-gray-500">
            Control greenhouse devices.
          </p>
        </section>

        <section id="events" className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-xl font-semibold text-gray-700">Events</h2>
          <p className="mt-2 text-gray-500">
            View recent greenhouse events.
          </p>
        </section>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)