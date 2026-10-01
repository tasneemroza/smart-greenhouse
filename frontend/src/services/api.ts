const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type SensorDto = {
  id: string;
  device_type: string;
  display_name: string;
  default_config: {
    sampling_interval_seconds: number;
    unit: string;
    threshold: number;
  };
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};

export type ReadingDto = {
  device_id: string;
  value: number;
  unit: string;
  source: "simulation" | "mqtt" | "vendor";
  recorded_at: string;
};

export type SamplingConfigDto = {
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};

export type SamplingResponse = {
  device_id: string;
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};

export type DeviceFamily = "simulation" | "edge";

export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: DeviceFamily;
  display_name: string;
  default_config: Record<string, unknown>;
  location_id: string | null;
  zone_id: string | null;
};

export type LocationDto = {
  id: string;
  name: string;
};

export type ZoneDto = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};

export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to load sensors");
  }

  return response.json();
}

export async function createSensor(
  type: string,
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create sensor");
  }

  return response.json();
}

export async function readSensor(
  deviceId: string,
): Promise<ReadingDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/read`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to read sensor");
  }

  return response.json();
}

export async function fetchReadings(
  deviceId: string,
  limit = 20,
): Promise<ReadingDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/readings?limit=${limit}`,
  );

  if (!response.ok) {
    throw new Error("Failed to load sensor readings");
  }

  return response.json();
}

export async function updateSampling(
  deviceId: string,
  config: SamplingConfigDto,
): Promise<SamplingResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/sampling`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update sampling");
  }

  return response.json();
}

export async function fetchDevices(options?: {
  family?: DeviceFamily;
  role?: "sensor" | "actuator";
}): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (options?.family) {
    params.set("family", options.family);
  }

  if (options?.role) {
    params.set("role", options.role);
  }

  const query = params.toString();
  const url = `${API_BASE_URL}/api/devices${query ? `?${query}` : ""}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to load devices");
  }

  return response.json();
}

export async function provisionDeviceFamily(
  family: DeviceFamily,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${family}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to provision device family");
  }

  return response.json();
}

export async function fetchLocations(): Promise<LocationDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/locations`);

  if (!response.ok) {
    throw new Error("Failed to load locations");
  }

  return response.json();
}

export async function fetchZones(
  locationId: string,
): Promise<ZoneDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones`,
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to load zones");
  }

  return response.json();
}

export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<DeviceDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      error.detail || "Failed to assign device to zone",
    );
  }

  return response.json();
}