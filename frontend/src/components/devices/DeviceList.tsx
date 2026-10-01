import { useEffect, useMemo, useState } from "react";

import {
  assignDeviceToZone,
  fetchDevices,
  fetchLocations,
  fetchZones,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
  type LocationDto,
  type ZoneDto,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

type ZoneOption = {
  id: string;
  label: string;
};

export default function DeviceList() {
  const [selectedFamily, setSelectedFamily] =
    useState<DeviceFamily>("simulation");

  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [zones, setZones] = useState<ZoneDto[]>([]);

  const [loading, setLoading] = useState(true);
  const [loadingZones, setLoadingZones] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
  const [assigningDeviceId, setAssigningDeviceId] = useState<string | null>(
    null,
  );
  const [error, setError] = useState("");

  async function loadDevices(family: DeviceFamily) {
    try {
      setLoading(true);
      setError("");

      const data = await fetchDevices({ family });
      setDevices(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load devices",
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadLocationsAndZones() {
    try {
      setLoadingZones(true);
      setError("");

      const locationData = await fetchLocations();

      const zoneGroups = await Promise.all(
        locationData.map((location) => fetchZones(location.id)),
      );

      setLocations(locationData);
      setZones(zoneGroups.flat());
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load locations and zones",
      );
    } finally {
      setLoadingZones(false);
    }
  }

  useEffect(() => {
    loadDevices(selectedFamily);
  }, [selectedFamily]);

  useEffect(() => {
    loadLocationsAndZones();
  }, []);

  async function handleProvision() {
    try {
      setProvisioning(true);
      setError("");

      await provisionDeviceFamily(selectedFamily);
      await loadDevices(selectedFamily);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to provision device family",
      );
    } finally {
      setProvisioning(false);
    }
  }

  async function handleZoneChange(
    deviceId: string,
    zoneId: string | null,
  ) {
    try {
      setAssigningDeviceId(deviceId);
      setError("");

      const updatedDevice = await assignDeviceToZone(
        deviceId,
        zoneId,
      );

      setDevices((currentDevices) =>
        currentDevices.map((device) =>
          device.id === updatedDevice.id
            ? updatedDevice
            : device,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to assign device to zone",
      );
    } finally {
      setAssigningDeviceId(null);
    }
  }

  const locationById = useMemo(() => {
    return new Map(
      locations.map((location) => [location.id, location]),
    );
  }, [locations]);

  const zoneOptions = useMemo<ZoneOption[]>(() => {
    return zones
      .map((zone) => {
        const location = locationById.get(zone.location_id);

        return {
          id: zone.id,
          label: location
            ? `${location.name} — ${zone.name}`
            : zone.name,
        };
      })
      .sort((a, b) => a.label.localeCompare(b.label));
  }, [zones, locationById]);

  function getCurrentZoneLabel(device: DeviceDto) {
    if (!device.zone_id) {
      return "Unassigned";
    }

    const zone = zones.find(
      (item) => item.id === device.zone_id,
    );

    if (!zone) {
      return "Unknown zone";
    }

    const location = locationById.get(zone.location_id);

    return location
      ? `${location.name} — ${zone.name}`
      : zone.name;
  }

  return (
    <div>
      <DeviceFamilySwitcher
        selectedFamily={selectedFamily}
        onChange={setSelectedFamily}
      />

      <div className="mb-6">
        <button
          type="button"
          onClick={handleProvision}
          disabled={provisioning}
          className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {provisioning
            ? "Provisioning..."
            : "Provision selected family"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-100 p-3 text-red-700">
          {error}
        </div>
      )}

      {loading && <p>Loading devices...</p>}

      {!loading && !error && devices.length === 0 && (
        <p className="text-gray-500">No devices found.</p>
      )}

      {!loading && devices.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device) => (
            <div
              key={device.id}
              className="rounded border p-4 shadow-sm"
            >
              <div className="mb-2 flex flex-wrap gap-2">
                <span className="rounded bg-gray-200 px-2 py-1 text-xs font-medium text-gray-700">
                  {device.role}
                </span>

                <span className="rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                  {device.device_family}
                </span>
              </div>

              <h3 className="font-semibold">
                {device.display_name}
              </h3>

              <p className="text-sm text-gray-600">
                Type: {device.device_type}
              </p>

              <p className="text-sm text-gray-600">
                Protocol:{" "}
                {String(
                  device.default_config.protocol ??
                    "not specified",
                )}
              </p>

              <div className="mt-4">
                <label
                  htmlFor={`zone-${device.id}`}
                  className="mb-1 block text-sm font-medium text-gray-700"
                >
                  Zone
                </label>

                <select
                  id={`zone-${device.id}`}
                  value={device.zone_id ?? ""}
                  onChange={(event) =>
                    handleZoneChange(
                      device.id,
                      event.target.value || null,
                    )
                  }
                  disabled={
                    loadingZones ||
                    assigningDeviceId === device.id
                  }
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500 disabled:cursor-not-allowed disabled:bg-gray-100"
                >
                  <option value="">Unassigned</option>

                  {zoneOptions.map((zone) => (
                    <option
                      key={zone.id}
                      value={zone.id}
                    >
                      {zone.label}
                    </option>
                  ))}
                </select>

                <p className="mt-1 text-xs text-gray-500">
                  Current: {getCurrentZoneLabel(device)}
                </p>

                {assigningDeviceId === device.id && (
                  <p className="mt-1 text-xs text-green-600">
                    Saving zone assignment...
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}