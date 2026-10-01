import { useEffect, useState } from "react";

import {
  createSensor,
  fetchReadings,
  fetchSensors,
  readSensor,
  updateSampling,
  type ReadingDto,
  type SensorDto,
} from "../../services/api";

type SensorState = {
  latest: ReadingDto | null;
  readings: ReadingDto[];
  interval: number;
  tracking: boolean;
};

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [sensorStates, setSensorStates] = useState<
    Record<string, SensorState>
  >({});
  const [loading, setLoading] = useState(true);
  const [readingId, setReadingId] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function loadSensors() {
    try {
      setLoading(true);
      setError("");

      const data = await fetchSensors();
      setSensors(data);

      const states = await Promise.all(
        data.map(async (sensor) => {
          try {
            const readings = await fetchReadings(sensor.id, 20);
            const latest = readings[0] ?? null;

            return {
              id: sensor.id,
              state: {
                latest,
                readings,
                interval:
                  sensor.default_config.sampling_interval_seconds || 300,
                tracking: true,
              },
            };
          } catch {
            return {
              id: sensor.id,
              state: {
                latest: null,
                readings: [],
                interval:
                  sensor.default_config.sampling_interval_seconds || 300,
                tracking: true,
              },
            };
          }
        }),
      );

      setSensorStates(
        Object.fromEntries(
          states.map(({ id, state }) => [id, state]),
        ),
      );
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

  useEffect(() => {
    const interval = window.setInterval(async () => {
      for (const sensor of sensors) {
        const state = sensorStates[sensor.id];

        if (!state?.tracking) {
          continue;
        }

        try {
          const readings = await fetchReadings(sensor.id, 20);
          const latest = readings[0] ?? null;

          setSensorStates((current) => ({
            ...current,
            [sensor.id]: {
              ...current[sensor.id],
              latest,
              readings,
            },
          }));
        } catch {
          continue;
        }
      }
    }, 5000);

    return () => window.clearInterval(interval);
  }, [sensors, sensorStates]);

  async function handleCreateSensor(type: string) {
    try {
      setError("");

      const displayName =
        type === "moisture"
          ? "Soil moisture sensor"
          : "Greenhouse light sensor";

      const newSensor = await createSensor(type, displayName);

      setSensors((current) => [newSensor, ...current]);

      const readings = await fetchReadings(newSensor.id, 20);

      setSensorStates((current) => ({
        ...current,
        [newSensor.id]: {
          latest: readings[0] ?? null,
          readings,
          interval:
            newSensor.default_config.sampling_interval_seconds || 300,
          tracking: true,
        },
      }));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create sensor",
      );
    }
  }

  async function handleRead(sensorId: string) {
    try {
      setReadingId(sensorId);
      setError("");

      const reading = await readSensor(sensorId);

      setSensorStates((current) => {
        const existing = current[sensorId];

        return {
          ...current,
          [sensorId]: {
            latest: reading,
            readings: [reading, ...(existing?.readings ?? [])],
            interval: existing?.interval ?? 300,
            tracking: existing?.tracking ?? true,
          },
        };
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to read sensor",
      );
    } finally {
      setReadingId(null);
    }
  }

  async function handleIntervalChange(
    sensorId: string,
    value: string,
  ) {
    const interval = Number(value);

    if (!Number.isInteger(interval) || interval < 5) {
      return;
    }

    setSensorStates((current) => ({
      ...current,
      [sensorId]: {
        ...current[sensorId],
        interval,
      },
    }));
  }

  async function handleTrackingChange(
    sensorId: string,
    tracking: boolean,
  ) {
    const current = sensorStates[sensorId];

    if (!current) {
      return;
    }

    try {
      setSavingId(sensorId);
      setError("");

      await updateSampling(sensorId, {
        sampling_interval_seconds: current.interval,
        tracking_enabled: tracking,
      });

      setSensorStates((states) => ({
        ...states,
        [sensorId]: {
          ...states[sensorId],
          tracking,
        },
      }));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update tracking",
      );
    } finally {
      setSavingId(null);
    }
  }

  async function handleSaveInterval(sensorId: string) {
    const current = sensorStates[sensorId];

    if (!current) {
      return;
    }

    try {
      setSavingId(sensorId);
      setError("");

      await updateSampling(sensorId, {
        sampling_interval_seconds: current.interval,
        tracking_enabled: current.tracking,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update sampling interval",
      );
    } finally {
      setSavingId(null);
    }
  }

  function formatRecordedAt(value: string) {
    return new Date(value).toLocaleString();
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
          {sensors.map((sensor) => {
            const state = sensorStates[sensor.id];

            return (
              <div
                key={sensor.id}
                className="rounded border p-4 shadow-sm"
              >
                <div className="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold">
                      {sensor.display_name}
                    </h3>

                    <p className="text-sm text-gray-600">
                      Type: {sensor.device_type}
                    </p>

                    <p className="text-sm text-gray-600">
                      Unit: {sensor.default_config.unit}
                    </p>
                  </div>

                  {state?.latest && (
                    <span
                      className={`rounded px-2 py-1 text-xs font-medium ${
                        state.latest.source === "simulation"
                          ? "bg-blue-100 text-blue-700"
                          : state.latest.source === "mqtt"
                            ? "bg-purple-100 text-purple-700"
                            : "bg-gray-200 text-gray-700"
                      }`}
                    >
                      {state.latest.source}
                    </span>
                  )}
                </div>

                <div className="mb-4 rounded bg-gray-50 p-3">
                  <p className="text-sm text-gray-500">
                    Latest value
                  </p>

                  {state?.latest ? (
                    <>
                      <p className="text-2xl font-semibold">
                        {state.latest.value.toFixed(2)}{" "}
                        {state.latest.unit}
                      </p>

                      <p className="text-xs text-gray-500">
                        {formatRecordedAt(
                          state.latest.recorded_at,
                        )}
                      </p>
                    </>
                  ) : (
                    <p className="text-gray-500">
                      No reading available
                    </p>
                  )}
                </div>

                <div className="mb-4">
                  <button
                    type="button"
                    onClick={() => handleRead(sensor.id)}
                    disabled={readingId === sensor.id}
                    className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {readingId === sensor.id
                      ? "Reading..."
                      : "Read now"}
                  </button>
                </div>

                <div className="mb-4">
                  <label className="mb-1 block text-sm font-medium">
                    Sampling interval
                  </label>

                  <div className="flex gap-2">
                    <input
                      type="number"
                      min="5"
                      value={state?.interval ?? 300}
                      onChange={(event) =>
                        handleIntervalChange(
                          sensor.id,
                          event.target.value,
                        )
                      }
                      className="w-full rounded border px-3 py-2"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        handleSaveInterval(sensor.id)
                      }
                      disabled={savingId === sensor.id}
                      className="rounded bg-gray-700 px-3 py-2 text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Save
                    </button>
                  </div>

                  <p className="mt-1 text-xs text-gray-500">
                    Minimum: 5 seconds
                  </p>
                </div>

                <div className="mb-4 flex items-center justify-between">
                  <label
                    htmlFor={`tracking-${sensor.id}`}
                    className="text-sm font-medium"
                  >
                    Tracking
                  </label>

                  <input
                    id={`tracking-${sensor.id}`}
                    type="checkbox"
                    checked={state?.tracking ?? true}
                    disabled={savingId === sensor.id}
                    onChange={(event) =>
                      handleTrackingChange(
                        sensor.id,
                        event.target.checked,
                      )
                    }
                    className="h-5 w-5"
                  />
                </div>

                <div>
                  <p className="mb-2 text-sm font-medium">
                    Recent readings
                  </p>

                  {state?.readings.length ? (
                    <div className="space-y-1">
                      {state.readings.slice(0, 5).map((reading) => (
                        <div
                          key={`${reading.recorded_at}-${reading.value}`}
                          className="flex justify-between text-xs text-gray-600"
                        >
                          <span>
                            {reading.value.toFixed(2)}{" "}
                            {reading.unit}
                          </span>

                          <span>
                            {formatRecordedAt(
                              reading.recorded_at,
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500">
                      No readings yet.
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}