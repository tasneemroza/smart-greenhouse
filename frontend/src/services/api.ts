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
};

export type DeviceFamily = "simulation" | "edge";

export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: DeviceFamily;
  display_name: string;
  default_config: Record<string, unknown>;
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