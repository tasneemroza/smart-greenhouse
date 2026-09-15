import { useEffect, useState } from "react";

import {
  createSensor,
  getSensors,
  type Sensor,
} from "../../services/api";


export default function SensorList() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState("");

  async function loadSensors() {
    try {
      setLoading(true);
      setError("");

      const data = await getSensors();
      setSensors(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load sensors",
      );
    } finally {
      setLoading(false);
    }
  }

  async function addSensor(type: "moisture" | "light") {
    try {
      setCreating(type);
      setError("");

      const sensor = await createSensor({
        type,
        display_name:
          type === "moisture"
            ? "Greenhouse Moisture Sensor"
            : "Greenhouse Light Sensor",
      });

      setSensors((currentSensors) => [
        sensor,
        ...currentSensors,
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create sensor",
      );
    } finally {
      setCreating("");
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg bg-white p-6 shadow">
        <p className="text-gray-500">Loading sensors...</p>
      </div>
    );
  }

  return (
    <section className="rounded-lg bg-white p-6 shadow">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-700">
            Sensors
          </h2>

          <p className="mt-1 text-gray-500">
            Manage the sensors connected to the greenhouse.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => addSensor("moisture")}
            disabled={creating !== ""}
            className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
          >
            {creating === "moisture"
              ? "Adding..."
              : "Add Moisture Sensor"}
          </button>

          <button
            type="button"
            onClick={() => addSensor("light")}
            disabled={creating !== ""}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {creating === "light"
              ? "Adding..."
              : "Add Light Sensor"}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {sensors.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="text-gray-500">
            No sensors have been added yet.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {sensors.map((sensor) => (
            <div
              key={sensor.id}
              className="rounded-lg border p-5"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-700">
                  {sensor.display_name}
                </h3>

                <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
                  {sensor.device_type}
                </span>
              </div>

              <div className="mt-4 text-gray-600">
                <p>
                  Threshold:{" "}
                  <strong>
                    {sensor.default_config.threshold}
                  </strong>
                </p>

                <p>
                  Unit:{" "}
                  <strong>
                    {sensor.default_config.unit}
                  </strong>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}