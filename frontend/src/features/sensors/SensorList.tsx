
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

            return {
              id: sensor.id,
              state: {
                latest: readings[0] ?? null,
                readings,
                interval: sensor.sampling_interval_seconds,
                tracking: sensor.tracking_enabled,
              },
            };
          } catch {
            return {
              id: sensor.id,
              state: {
                latest: null,
                readings: [],
                interval: sensor.sampling_interval_seconds,
                tracking: sensor.tracking_enabled,
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
    const timer = window.setInterval(async () => {
      for (const sensor of sensors) {
        const state = sensorStates[sensor.id];

        if (!state?.tracking) {
          continue;
        }

        try {
          const readings = await fetchReadings(sensor.id, 20);

          setSensorStates((current) => ({
            ...current,
            [sensor.id]: {
              ...current[sensor.id],
              latest: readings[0] ?? null,
              readings,
            },
          }));
        } catch {
          continue;
        }
      }
    }, 5000);

    return () => window.clearInterval(timer);
  }, [sensors, sensorStates]);

  async function handleCreateSensor(type: string) {
    try {
      setError("");

      const displayName =
        type === "moisture"
          ? "Soil moisture sensor"
          : "Greenhouse light sensor";

      const newSensor = await createSensor(type, displayName);
      const readings = await fetchReadings(newSensor.id, 20);

      setSensors((current) => [newSensor, ...current]);

      setSensorStates((current) => ({
        ...current,
        [newSensor.id]: {
          latest: readings[0] ?? null,
          readings,
          interval: newSensor.sampling_interval_seconds,
          tracking: newSensor.tracking_enabled,
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

  function handleIntervalChange(sensorId: string, value: string) {
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

    if (current.interval < 5) {
      setError("Sampling interval must be at least 5 seconds");
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
    <div className="text-[#293B32]">
      <div className="mb-5 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => handleCreateSensor("moisture")}
          className="rounded-xl bg-[#315747] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#264637] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#315747]"
        >
          Add moisture sensor
        </button>

        <button
          type="button"
          onClick={() => handleCreateSensor("light")}
          className="rounded-xl border border-[#DDE5DC] bg-[#E7EFE6] px-4 py-2.5 text-sm font-medium text-[#315747] transition hover:bg-[#DCE8DA] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#315747]"
        >
          Add light sensor
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="mb-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {loading && (
        <p className="py-4 text-sm text-[#6F7C73]">Loading sensors...</p>
      )}

      {!loading && !error && sensors.length === 0 && (
        <p className="rounded-xl border border-dashed border-[#DDE5DC] bg-[#F6F7F2] p-6 text-sm text-[#6F7C73]">
          No sensors found.
        </p>
      )}

      {!loading && sensors.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {sensors.map((sensor) => {
            const state = sensorStates[sensor.id];

            return (
              <div
                key={sensor.id}
                className="min-w-0 rounded-2xl border border-[#DDE5DC] bg-white p-4 shadow-[0_3px_16px_rgba(41,59,50,0.05)] transition-shadow hover:shadow-md sm:p-5"
              >
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="break-words font-semibold text-[#293B32]">
                      {sensor.display_name}
                    </h3>

                    <p className="mt-1 text-sm text-[#6F7C73]">
                      Type: {sensor.device_type}
                    </p>

                    <p className="text-sm text-[#6F7C73]">
                      Unit: {sensor.default_config.unit}
                    </p>
                  </div>

                  {state?.latest && (
                    <span className="shrink-0 rounded-full bg-[#E7EFE6] px-3 py-1 text-xs font-medium text-[#315747]">
                      {state.latest.source}
                    </span>
                  )}
                </div>

                <div className="mb-4 rounded-xl border border-[#E7EFE6] bg-[#F6F7F2] p-4">
                  <p className="text-sm font-medium text-[#6F7C73]">
                    Latest value
                  </p>

                  {state?.latest ? (
                    <>
                      <p className="mt-1 break-words text-3xl font-bold tracking-tight text-[#315747]">
                        {state.latest.value.toFixed(2)}{" "}
                        <span className="text-lg font-medium">
                          {state.latest.unit}
                        </span>
                      </p>

                      <p className="mt-2 text-xs text-[#6F7C73]">
                        {formatRecordedAt(state.latest.recorded_at)}
                      </p>
                    </>
                  ) : (
                    <p className="mt-2 text-sm text-[#6F7C73]">
                      No reading available
                    </p>
                  )}
                </div>

                <div className="mb-5">
                  <button
                    type="button"
                    onClick={() => handleRead(sensor.id)}
                    disabled={readingId === sensor.id}
                    className="rounded-xl bg-[#315747] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#264637] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#315747] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {readingId === sensor.id ? "Reading..." : "Read now"}
                  </button>
                </div>

                <div className="mb-5">
                  <label
                    htmlFor={`interval-${sensor.id}`}
                    className="mb-2 block text-sm font-semibold text-[#293B32]"
                  >
                    Sampling interval
                  </label>

                  <div className="flex gap-2">
                    <input
                      id={`interval-${sensor.id}`}
                      type="number"
                      min="5"
                      value={
                        state?.interval ??
                        sensor.sampling_interval_seconds
                      }
                      onChange={(event) =>
                        handleIntervalChange(sensor.id, event.target.value)
                      }
                      className="w-full min-w-0 rounded-xl border border-[#DDE5DC] bg-white px-3 py-2 text-sm text-[#293B32] focus:border-[#315747] focus:outline-none focus:ring-2 focus:ring-[#E7EFE6]"
                    />

                    <button
                      type="button"
                      onClick={() => handleSaveInterval(sensor.id)}
                      disabled={savingId === sensor.id}
                      className="rounded-xl bg-[#315747] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#264637] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {savingId === sensor.id ? "Saving..." : "Save"}
                    </button>
                  </div>

                  <p className="mt-2 text-xs text-[#6F7C73]">
                    Minimum: 5 seconds
                  </p>
                </div>

                <div className="mb-5 flex items-center justify-between rounded-xl bg-[#F6F7F2] px-3 py-3">
                  <label
                    htmlFor={`tracking-${sensor.id}`}
                    className="text-sm font-medium text-[#293B32]"
                  >
                    Tracking
                  </label>

                  <input
                    id={`tracking-${sensor.id}`}
                    type="checkbox"
                    checked={
                      state?.tracking ?? sensor.tracking_enabled
                    }
                    disabled={savingId === sensor.id}
                    onChange={(event) =>
                      handleTrackingChange(
                        sensor.id,
                        event.target.checked,
                      )
                    }
                    className="h-5 w-5 accent-[#315747] disabled:cursor-not-allowed"
                  />
                </div>

                <div className="border-t border-[#E7EFE6] pt-4">
                  <p className="mb-3 text-sm font-semibold text-[#293B32]">
                    Recent readings
                  </p>

                  {state?.readings.length ? (
                    <div className="space-y-2">
                      {state.readings.slice(0, 5).map((reading) => (
                        <div
                          key={`${reading.recorded_at}-${reading.value}`}
                          className="flex flex-wrap justify-between gap-x-3 gap-y-1 text-xs text-[#6F7C73]"
                        >
                          <span className="font-medium text-[#315747]">
                            {reading.value.toFixed(2)} {reading.unit}
                          </span>

                          <span>{formatRecordedAt(reading.recorded_at)}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[#6F7C73]">
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
