const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type Sensor = {
  id: string;
  device_type: string;
  display_name: string;
  default_config: {
    threshold: number;
    unit: string;
  };
};

export type CreateSensorRequest = {
  type: string;
  display_name?: string;
};

export async function getSensors(): Promise<Sensor[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to load sensors");
  }

  return response.json();
}

export async function createSensor(
  sensor: CreateSensorRequest,
): Promise<Sensor> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sensor),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create sensor");
  }

  return response.json();
}