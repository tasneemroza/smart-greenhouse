import { useState } from "react";

type Zone = {
  name: string;
  moisture_threshold_low: string;
  moisture_threshold_high: string;
  schedule: string;
};

type SavedZone = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};

type SavedConfig = {
  location: {
    id: string;
    name: string;
  };
  zones: SavedZone[];
};

const createZone = (): Zone => ({
  name: "",
  moisture_threshold_low: "0.2",
  moisture_threshold_high: "0.45",
  schedule: "08:00",
});

function LocationConfigWizard() {
  const [locationName, setLocationName] = useState("");
  const [zones, setZones] = useState<Zone[]>([createZone()]);
  const [savedConfig, setSavedConfig] = useState<SavedConfig | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const updateZone = (
    index: number,
    field: keyof Zone,
    value: string,
  ) => {
    setZones((current) =>
      current.map((zone, zoneIndex) =>
        zoneIndex === index
          ? { ...zone, [field]: value }
          : zone,
      ),
    );
  };

  const addZone = () => {
    setZones((current) => [...current, createZone()]);
  };

  const removeZone = (index: number) => {
    if (zones.length === 1) {
      return;
    }

    setZones((current) =>
      current.filter((_, zoneIndex) => zoneIndex !== index),
    );
  };

  const validate = () => {
    if (!locationName.trim()) {
      return "Location name is required.";
    }

    if (zones.length === 0) {
      return "At least one zone is required.";
    }

    for (const zone of zones) {
      if (!zone.name.trim()) {
        return "Every zone needs a name.";
      }

      const low = Number(zone.moisture_threshold_low);
      const high = Number(zone.moisture_threshold_high);

      if (Number.isNaN(low) || Number.isNaN(high)) {
        return "Moisture thresholds must be numbers.";
      }

      if (low < 0 || low > 1 || high < 0 || high > 1) {
        return "Moisture thresholds must be between 0 and 1.";
      }

      if (low >= high) {
        return "Low moisture threshold must be lower than high threshold.";
      }

      if (!zone.schedule.trim()) {
        return "Schedule is required.";
      }
    }

    return "";
  };

  const handleSubmit = async () => {
    setError("");
    setSuccess("");

    const validationError = validate();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/locations/config",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            location_name: locationName.trim(),
            zones: zones.map((zone) => ({
              name: zone.name.trim(),
              moisture_threshold_low: Number(
                zone.moisture_threshold_low,
              ),
              moisture_threshold_high: Number(
                zone.moisture_threshold_high,
              ),
              schedule: {
                watering: zone.schedule.trim(),
              },
            })),
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to save configuration.");
      }

      setSavedConfig(data);
      setSuccess("Location configuration saved successfully.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to save configuration.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-800">
          Location Configuration
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Create a location and configure one or more greenhouse zones.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {success}
        </div>
      )}

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Location name
        </label>

        <input
          type="text"
          value={locationName}
          onChange={(event) => setLocationName(event.target.value)}
          placeholder="Lab Site A"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500"
        />
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-gray-800">
            Zones
          </h4>

          <button
            type="button"
            onClick={addZone}
            className="rounded-lg bg-green-700 px-3 py-2 text-sm font-medium text-white hover:bg-green-800"
          >
            Add zone
          </button>
        </div>

        {zones.map((zone, index) => (
          <div
            key={index}
            className="rounded-xl border border-gray-200 bg-gray-50 p-4"
          >
            <div className="mb-4 flex items-center justify-between">
              <h5 className="font-medium text-gray-800">
                Zone {index + 1}
              </h5>

              {zones.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeZone(index)}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Zone name
                </label>

                <input
                  type="text"
                  value={zone.name}
                  onChange={(event) =>
                    updateZone(index, "name", event.target.value)
                  }
                  placeholder="Bench 1"
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Watering schedule
                </label>

                <input
                  type="time"
                  value={zone.schedule}
                  onChange={(event) =>
                    updateZone(index, "schedule", event.target.value)
                  }
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Low moisture threshold
                </label>

                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={zone.moisture_threshold_low}
                  onChange={(event) =>
                    updateZone(
                      index,
                      "moisture_threshold_low",
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  High moisture threshold
                </label>

                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={zone.moisture_threshold_high}
                  onChange={(event) =>
                    updateZone(
                      index,
                      "moisture_threshold_high",
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={loading}
        className="rounded-lg bg-green-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Saving..." : "Save configuration"}
      </button>

      {savedConfig && (
        <div className="rounded-xl border border-green-200 bg-green-50 p-4">
          <h4 className="font-semibold text-green-900">
            Saved Configuration
          </h4>

          <p className="mt-2 text-sm text-gray-700">
            <strong>Location:</strong>{" "}
            {savedConfig.location.name}
          </p>

          <p className="mt-1 break-all text-sm text-gray-700">
            <strong>Location ID:</strong>{" "}
            {savedConfig.location.id}
          </p>

          <div className="mt-4 space-y-3">
            {savedConfig.zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded-lg border border-green-100 bg-white p-3"
              >
                <p className="font-medium text-gray-800">
                  {zone.name}
                </p>

                <p className="mt-1 text-sm text-gray-600">
                  Threshold: {zone.moisture_threshold_low} –{" "}
                  {zone.moisture_threshold_high}
                </p>

                <p className="mt-1 text-sm text-gray-600">
                  Watering:{" "}
                  {String(zone.schedule.watering ?? "Not set")}
                </p>

                <p className="mt-1 break-all text-xs text-gray-500">
                  location_id: {zone.location_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default LocationConfigWizard;