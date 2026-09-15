import { useEffect, useState } from "react";

import {
  createSensor,
  fetchSensors,
  type SensorDto,
} from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadSensors() {
    try {
      setLoading(true);
      setError("");

      const data = await fetchSensors();
      setSensors(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load sensors",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  async function handleCreateSensor(type: string) {
    try {
      setError("");

      const displayName =
        type === "moisture"
          ? "Soil moisture sensor"
          : "Greenhouse light sensor";

      const newSensor = await createSensor(type, displayName);

      setSensors((current) => [newSensor, ...current]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create sensor",
      );
    }
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => handleCreateSensor("moisture")}
          className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          Add moisture sensor
        </button>

        <button
          type="button"
          onClick={() => handleCreateSensor("light")}
          className="rounded bg-yellow-500 px-4 py-2 text-white hover:bg-yellow-600"
        >
          Add light sensor
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-100 p-3 text-red-700">
          {error}
        </div>
      )}

      {loading && <p>Loading sensors...</p>}

      {!loading && !error && sensors.length === 0 && (
        <p className="text-gray-500">No sensors found.</p>
      )}

      {!loading && sensors.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {sensors.map((sensor) => (
            <div
              key={sensor.id}
              className="rounded border p-4 shadow-sm"
            >
              <h3 className="font-semibold">{sensor.display_name}</h3>

              <p className="text-sm text-gray-600">
                Type: {sensor.device_type}
              </p>

              <p className="text-sm text-gray-600">
                Unit: {sensor.default_config.unit}
              </p>

              <p className="text-sm text-gray-600">
                Threshold: {sensor.default_config.threshold}
              </p>

              <p className="text-sm text-gray-600">
                Sampling interval:{" "}
                {sensor.default_config.sampling_interval_seconds} seconds
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}