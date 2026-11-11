import { useEffect, useMemo, useState } from "react";

import {
  assignDeviceToZone,
  fetchDevices,
  fetchLocations,
  fetchZones,
  provisionDeviceFamily,
  type ActuatorState,
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

const actuatorStateStyles: Record<ActuatorState, string> = {
  off: "bg-slate-100 text-slate-700",
  idle: "bg-slate-100 text-slate-700",
  running: "bg-[#D7E5E3] text-[#344A4F]",
  error: "bg-red-100 text-red-700",
  maintenance: "bg-amber-100 text-amber-700",
};

export default function DeviceList() {
  const [selectedFamily, setSelectedFamily] =
    useState<DeviceFamily>("simulation");

  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [showAllDevices, setShowAllDevices] = useState(false);
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

  const visibleDevices = useMemo(() => {
    if (showAllDevices) {
      return devices;
    }

    const seenUnassignedSensorTypes = new Set<string>();

    return devices.filter((device) => {
      if (device.location_id || device.zone_id) {
        return true;
      }

      if (device.device_family === "edge") {
        return true;
      }

      if (device.device_type === "test_pump") {
        return false;
      }

      if (device.role === "actuator") {
        return true;
      }

      if (seenUnassignedSensorTypes.has(device.device_type)) {
        return false;
      }

      seenUnassignedSensorTypes.add(device.device_type);
      return true;
    });
  }, [devices, showAllDevices]);

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
            ? `${location.name} - ${zone.name}`
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
      ? `${location.name} - ${zone.name}`
      : zone.name;
  }

  return (
    <div>
      <DeviceFamilySwitcher
        selectedFamily={selectedFamily}
        onChange={setSelectedFamily}
      />

      <div className="mb-6 rounded-2xl border border-[#D7E5E3] bg-white p-5 shadow-sm">
        <button
          type="button"
          onClick={handleProvision}
          disabled={provisioning}
          className="rounded-xl bg-[#344A4F] px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#293D41] focus:outline-none focus:ring-2 focus:ring-[#344A4F] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {provisioning
            ? "Provisioning..."
            : "Provision selected family"}
        </button>
      </div>

      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#D7E5E3] bg-white p-4">
        <div>
          <p className="font-semibold text-[#293C40]">
            Device Overview
          </p>
          <p className="text-sm text-[#68797B]">
            Showing {visibleDevices.length} of {devices.length} devices
          </p>
        </div>

        <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-[#293C40]">
          <input
            type="checkbox"
            checked={showAllDevices}
            onChange={(event) =>
              setShowAllDevices(event.target.checked)
            }
            className="h-4 w-4 accent-[#344A4F]"
          />
          Show all devices
        </label>
      </div>

      {error && (
        <div role="alert" className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading && <p>Loading devices...</p>}

      {!loading && !error && visibleDevices.length === 0 && (
        <p className="text-[#68797B]">No devices found.</p>
      )}

      {!loading && visibleDevices.length > 0 && (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {visibleDevices.map((device) => (
            <div
              key={device.id}
              className="group rounded-2xl border border-[#D7E5E3] bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-[#D7E5E3] hover:shadow-md"
            >
              <div className="mb-2 flex flex-wrap gap-2">
                <span className="rounded-full bg-[#F6F8F7] px-3 py-1 text-xs font-semibold capitalize text-[#293C40]">
                  {device.role}
                </span>

                <span className="rounded-full bg-[#D7E5E3] px-3 py-1 text-xs font-semibold capitalize text-[#344A4F]">
                  {device.device_family}
                </span>
                {device.role === "actuator" && device.state && (
                  <span
                    title={`Allowed commands: ${device.allowed_commands.join(", ") || "None"}`}
                    className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${actuatorStateStyles[device.state]}`}
                  >
                    {device.state}
                  </span>
                )}
              </div>

              <h3 className="text-lg font-bold text-[#293C40]">
                {device.display_name}
              </h3>

              <p className="text-sm text-[#68797B]">
                Type: {device.device_type}
              </p>

              <p className="text-sm text-[#68797B]">
                Protocol:{" "}
                {String(
                  device.default_config.protocol ??
                    "not specified",
                )}
              </p>

              <div className="mt-4">
                <label
                  htmlFor={`zone-${device.id}`}
                  className="mb-1 block text-sm font-medium text-[#293C40]"
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
                  className="w-full rounded-xl border border-[#D7E5E3] bg-white px-3 py-2.5 text-sm text-[#293C40] outline-none transition focus:border-[#344A4F] focus:ring-2 focus:ring-[#E7EFE6] disabled:cursor-not-allowed disabled:bg-[#F6F8F7]"
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

                <p className="mt-1 text-xs text-[#68797B]">
                  Current: {getCurrentZoneLabel(device)}
                </p>

                {assigningDeviceId === device.id && (
                  <p className="mt-1 text-xs text-[#344A4F]">
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



