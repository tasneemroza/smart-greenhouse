import { useEffect, useState } from "react";

import {
  fetchDevices,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

export default function DeviceList() {
  const [selectedFamily, setSelectedFamily] =
    useState<DeviceFamily>("simulation");
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
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

  useEffect(() => {
    loadDevices(selectedFamily);
  }, [selectedFamily]);

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
          {provisioning ? "Provisioning..." : "Provision selected family"}
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

              <h3 className="font-semibold">{device.display_name}</h3>

              <p className="text-sm text-gray-600">
                Type: {device.device_type}
              </p>

              <p className="text-sm text-gray-600">
                Protocol:{" "}
                {String(device.default_config.protocol ?? "not specified")}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}