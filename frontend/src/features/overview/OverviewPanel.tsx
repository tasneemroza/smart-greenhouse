import { useEffect, useState } from "react";
import { fetchLocations, fetchOverview } from "../../services/api";
import type { LocationDto, LocationOverviewDto } from "../../services/api";

export default function OverviewPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [overview, setOverview] = useState<LocationOverviewDto | null>(null);
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [loadingOverview, setLoadingOverview] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    fetchLocations()
      .then((items) => {
        if (!active) return;
        setLocations(items);
        if (items.length > 0) setLocationId(items[0].id);
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load locations.");
        }
      })
      .finally(() => {
        if (active) setLoadingLocations(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!locationId) {
      setOverview(null);
      return;
    }

    let active = true;
    setLoadingOverview(true);
    setError("");
    setOverview(null);

    fetchOverview(locationId)
      .then((data) => {
        if (active) setOverview(data);
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load overview.");
        }
      })
      .finally(() => {
        if (active) setLoadingOverview(false);
      });

    return () => {
      active = false;
    };
  }, [locationId]);

  if (loadingLocations) {
    return <p className="text-sm text-[#6F7C73]">Loading locations...</p>;
  }

  return (
    <div className="space-y-5">
      {locations.length > 0 && (
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-[#52675A]">
            Location
          </span>
          <select
            value={locationId}
            onChange={(event) => setLocationId(event.target.value)}
            className="w-full rounded-xl border border-[#DDE5DC] bg-white px-3 py-2 text-sm text-[#293B32] outline-none focus:border-[#315747]"
          >
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {error && (
        <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {!error && locations.length === 0 && (
        <p className="text-sm text-[#6F7C73]">
          No locations found. Create a location in Configuration first.
        </p>
      )}

      {loadingOverview && (
        <p className="text-sm text-[#6F7C73]">Loading greenhouse overview...</p>
      )}

      {overview && !loadingOverview && (
        <div className="space-y-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#6F7C73]">
              Selected greenhouse
            </p>
            <h3 className="mt-1 text-lg font-bold text-[#315747]">
              {overview.location.name}
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-[#E7EFE6] p-3">
              <p className="text-sm text-[#52675A]">Sensors</p>
              <p className="mt-1 text-2xl font-bold text-[#315747]">
                {overview.device_counts.sensor}
              </p>
            </div>
            <div className="rounded-xl bg-[#E7EFE6] p-3">
              <p className="text-sm text-[#52675A]">Actuators</p>
              <p className="mt-1 text-2xl font-bold text-[#315747]">
                {overview.device_counts.actuator}
              </p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-[#293B32]">Zones and devices</h4>

            {overview.zones.length === 0 ? (
              <p className="mt-2 text-sm text-[#6F7C73]">
                No zones configured for this location.
              </p>
            ) : (
              <div className="mt-3 space-y-3">
                {overview.zones.map((zone) => (
                  <section
                    key={zone.id}
                    className="rounded-xl border border-[#DDE5DC] p-3"
                  >
                    <h5 className="font-semibold text-[#315747]">{zone.name}</h5>
                    <p className="mt-1 text-xs text-[#6F7C73]">
                      Moisture thresholds: {zone.moisture_threshold_low}–{zone.moisture_threshold_high}
                    </p>

                    {zone.devices.length === 0 ? (
                      <p className="mt-2 text-sm text-[#6F7C73]">No assigned devices.</p>
                    ) : (
                      <ul className="mt-3 space-y-3">
                        {zone.devices.map((device) => {
                          const reading = zone.latest_readings.find(
                            (item) => item.device_id === device.id,
                          );

                          return (
                            <li key={device.id} className="border-t border-[#EDF0EA] pt-2">
                              <p className="text-sm font-medium text-[#293B32]">
                                {device.display_name}
                              </p>
                              <p className="text-xs text-[#6F7C73]">
                                {device.device_type} · {device.role}
                              </p>
                              {device.role === "sensor" && (
                                <div className="mt-1 text-sm text-[#52675A]">
                                  {reading ? (
                                    <>
                                      <p>
                                        Latest reading: <strong>{reading.value} {reading.unit}</strong>
                                      </p>
                                      <p className="text-xs">
                                        Recorded: {new Date(reading.recorded_at).toLocaleString()}
                                      </p>
                                      <p className="text-xs">
                                        Tracking: {reading.tracking_enabled ? "On" : "Off"} ·
                                        Sampling: {reading.sampling_interval_seconds}s
                                      </p>
                                    </>
                                  ) : (
                                    <p>No reading recorded yet.</p>
                                  )}
                                </div>
                              )}
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </section>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-xl border border-[#DDE5DC] p-3">
            <h4 className="font-semibold text-[#315747]">Automation strategy</h4>
            <p className="mt-1 text-sm text-[#52675A]">
              {overview.strategy_key ?? "No strategy configured"}
            </p>

            <h5 className="mt-3 text-sm font-semibold text-[#293B32]">
              Latest evaluation
            </h5>
            {overview.last_recommendation ? (
              <>
                <p className="mt-1 text-sm text-[#293B32]">
                  {overview.last_recommendation.action}
                </p>
                <p className="mt-1 text-sm text-[#6F7C73]">
                  {overview.last_recommendation.reason}
                </p>
              </>
            ) : (
              <p className="mt-1 text-sm text-[#6F7C73]">
                No recommendation available.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
