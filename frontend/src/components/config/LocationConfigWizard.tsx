import { useEffect, useState } from "react";

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

type SavedLocation = {
  id: string;
  name: string;
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
  const [locations, setLocations] = useState<SavedLocation[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [editingZoneId, setEditingZoneId] = useState<string | null>(null);
  const [editingZone, setEditingZone] = useState<Zone | null>(null);
  const [newZone, setNewZone] = useState<Zone>(createZone());
  const [showAddZone, setShowAddZone] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const loadLocations = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/locations",
      );

      if (!response.ok) {
        throw new Error("Failed to load saved locations.");
      }

      const data: SavedLocation[] = await response.json();
      setLocations(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to load saved locations.",
      );
    }
  };

  useEffect(() => {
    loadLocations();
  }, []);

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

  const validateZone = (zone: Zone) => {
    if (!zone.name.trim()) {
      return "Zone name is required.";
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

    return "";
  };

  const validate = () => {
    if (!locationName.trim()) {
      return "Location name is required.";
    }

    if (zones.length === 0) {
      return "At least one zone is required.";
    }

    for (const zone of zones) {
      const zoneError = validateZone(zone);

      if (zoneError) {
        return zoneError;
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
      setSelectedLocationId(data.location.id);
      setSuccess("Location configuration saved successfully.");
      await loadLocations();
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

  const openLocation = async (locationId: string) => {
    setError("");
    setSuccess("");
    setSelectedLocationId(locationId);
    setEditingZoneId(null);
    setEditingZone(null);
    setShowAddZone(false);
    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/locations/${locationId}/config`,
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load location.");
      }

      setSavedConfig(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to load location.",
      );
    } finally {
      setLoading(false);
    }
  };

  const deleteLocation = async (locationId: string) => {
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/locations/${locationId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to delete location.");
      }

      if (selectedLocationId === locationId) {
        setSelectedLocationId("");
        setSavedConfig(null);
        setEditingZoneId(null);
        setEditingZone(null);
        setShowAddZone(false);
      }

      setSuccess("Location deleted successfully.");
      await loadLocations();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to delete location.",
      );
    } finally {
      setLoading(false);
    }
  };

  const startEditingZone = (zone: SavedZone) => {
    setError("");
    setSuccess("");
    setEditingZoneId(zone.id);
    setEditingZone({
      name: zone.name,
      moisture_threshold_low: String(
        zone.moisture_threshold_low,
      ),
      moisture_threshold_high: String(
        zone.moisture_threshold_high,
      ),
      schedule: String(zone.schedule.watering ?? ""),
    });
    setShowAddZone(false);
  };

  const cancelEditingZone = () => {
    setEditingZoneId(null);
    setEditingZone(null);
  };

  const updateEditingZone = (
    field: keyof Zone,
    value: string,
  ) => {
    setEditingZone((current) =>
      current
        ? {
            ...current,
            [field]: value,
          }
        : current,
    );
  };

  const saveEditedZone = async () => {
    if (!editingZoneId || !editingZone || !selectedLocationId) {
      return;
    }

    setError("");
    setSuccess("");

    const validationError = validateZone(editingZone);

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/locations/${selectedLocationId}/zones/${editingZoneId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: editingZone.name.trim(),
            moisture_threshold_low: Number(
              editingZone.moisture_threshold_low,
            ),
            moisture_threshold_high: Number(
              editingZone.moisture_threshold_high,
            ),
            schedule: {
              watering: editingZone.schedule.trim(),
            },
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to update zone.");
      }

      setSavedConfig((current) =>
        current
          ? {
              ...current,
              zones: current.zones.map((zone) =>
                zone.id === editingZoneId ? data : zone,
              ),
            }
          : current,
      );

      setEditingZoneId(null);
      setEditingZone(null);
      setSuccess("Zone updated successfully.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to update zone.",
      );
    } finally {
      setLoading(false);
    }
  };

  const deleteZone = async (zoneId: string) => {
    if (!selectedLocationId || !savedConfig) {
      return;
    }

    if (savedConfig.zones.length <= 1) {
      setError("Cannot delete the last zone.");
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/locations/${selectedLocationId}/zones/${zoneId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to delete zone.");
      }

      setSavedConfig((current) =>
        current
          ? {
              ...current,
              zones: current.zones.filter(
                (zone) => zone.id !== zoneId,
              ),
            }
          : current,
      );

      if (editingZoneId === zoneId) {
        setEditingZoneId(null);
        setEditingZone(null);
      }

      setSuccess("Zone deleted successfully.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to delete zone.",
      );
    } finally {
      setLoading(false);
    }
  };

  const updateNewZone = (
    field: keyof Zone,
    value: string,
  ) => {
    setNewZone((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const addZoneToSavedLocation = async () => {
    if (!selectedLocationId) {
      return;
    }

    setError("");
    setSuccess("");

    const validationError = validateZone(newZone);

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/locations/${selectedLocationId}/zones`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: newZone.name.trim(),
            moisture_threshold_low: Number(
              newZone.moisture_threshold_low,
            ),
            moisture_threshold_high: Number(
              newZone.moisture_threshold_high,
            ),
            schedule: {
              watering: newZone.schedule.trim(),
            },
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to add zone.");
      }

      setSavedConfig((current) =>
        current
          ? {
              ...current,
              zones: [...current.zones, data],
            }
          : current,
      );

      setNewZone(createZone());
      setShowAddZone(false);
      setSuccess("Zone added successfully.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to add zone.",
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
          Create and manage greenhouse locations and zones.
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

      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h4 className="font-semibold text-gray-800">
          Saved locations
        </h4>

        <div className="mt-4 space-y-2">
          {locations.length === 0 ? (
            <p className="text-sm text-gray-500">
              No saved locations yet.
            </p>
          ) : (
            locations.map((location) => (
              <div
                key={location.id}
                className={`flex items-center justify-between rounded-lg border p-3 ${
                  selectedLocationId === location.id
                    ? "border-green-300 bg-green-50"
                    : "border-gray-200 bg-gray-50"
                }`}
              >
                <button
                  type="button"
                  onClick={() => openLocation(location.id)}
                  className="text-left font-medium text-gray-800 hover:text-green-700"
                >
                  {location.name}
                </button>

                <button
                  type="button"
                  onClick={() => deleteLocation(location.id)}
                  disabled={loading}
                  className="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
        <h4 className="font-semibold text-gray-800">
          Create new location
        </h4>

        <div className="mt-4">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Location name
          </label>

          <input
            type="text"
            value={locationName}
            onChange={(event) => setLocationName(event.target.value)}
            placeholder="Lab Site A"
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
          />
        </div>

        <div className="mt-6 space-y-4">
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
              className="rounded-xl border border-gray-200 bg-white p-4"
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
          className="mt-6 rounded-lg bg-green-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Saving..." : "Save configuration"}
        </button>
      </div>

      {savedConfig && (
        <div className="rounded-xl border border-green-200 bg-green-50 p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h4 className="font-semibold text-green-900">
                {savedConfig.location.name}
              </h4>

              <p className="mt-1 break-all text-xs text-gray-500">
                Location ID: {savedConfig.location.id}
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setShowAddZone((current) => !current);
                setEditingZoneId(null);
                setEditingZone(null);
                setError("");
                setSuccess("");
              }}
              disabled={loading}
              className="shrink-0 rounded-lg bg-green-700 px-3 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
            >
              {showAddZone ? "Cancel" : "Add zone"}
            </button>
          </div>

          {showAddZone && (
            <div className="mt-4 rounded-xl border border-green-100 bg-white p-4">
              <h5 className="font-medium text-gray-800">
                Add zone
              </h5>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Zone name
                  </label>

                  <input
                    type="text"
                    value={newZone.name}
                    onChange={(event) =>
                      updateNewZone("name", event.target.value)
                    }
                    placeholder="Zone 2"
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Watering schedule
                  </label>

                  <input
                    type="time"
                    value={newZone.schedule}
                    onChange={(event) =>
                      updateNewZone("schedule", event.target.value)
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
                    value={newZone.moisture_threshold_low}
                    onChange={(event) =>
                      updateNewZone(
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
                    value={newZone.moisture_threshold_high}
                    onChange={(event) =>
                      updateNewZone(
                        "moisture_threshold_high",
                        event.target.value,
                      )
                    }
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={addZoneToSavedLocation}
                disabled={loading}
                className="mt-4 rounded-lg bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
              >
                {loading ? "Adding..." : "Save zone"}
              </button>
            </div>
          )}

          <div className="mt-4 space-y-3">
            {savedConfig.zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded-lg border border-green-100 bg-white p-4"
              >
                {editingZoneId === zone.id && editingZone ? (
                  <>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label className="mb-2 block text-sm font-medium text-gray-700">
                          Zone name
                        </label>

                        <input
                          type="text"
                          value={editingZone.name}
                          onChange={(event) =>
                            updateEditingZone(
                              "name",
                              event.target.value,
                            )
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500"
                        />
                      </div>

                      <div>
                        <label className="mb-2 block text-sm font-medium text-gray-700">
                          Watering schedule
                        </label>

                        <input
                          type="time"
                          value={editingZone.schedule}
                          onChange={(event) =>
                            updateEditingZone(
                              "schedule",
                              event.target.value,
                            )
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500"
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
                          value={editingZone.moisture_threshold_low}
                          onChange={(event) =>
                            updateEditingZone(
                              "moisture_threshold_low",
                              event.target.value,
                            )
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500"
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
                          value={editingZone.moisture_threshold_high}
                          onChange={(event) =>
                            updateEditingZone(
                              "moisture_threshold_high",
                              event.target.value,
                            )
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500"
                        />
                      </div>
                    </div>

                    <div className="mt-4 flex gap-2">
                      <button
                        type="button"
                        onClick={saveEditedZone}
                        disabled={loading}
                        className="rounded-lg bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
                      >
                        {loading ? "Saving..." : "Save changes"}
                      </button>

                      <button
                        type="button"
                        onClick={cancelEditingZone}
                        disabled={loading}
                        className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-medium text-gray-800">
                          {zone.name}
                        </p>

                        <p className="mt-1 text-sm text-gray-600">
                          Threshold:{" "}
                          {zone.moisture_threshold_low} –{" "}
                          {zone.moisture_threshold_high}
                        </p>

                        <p className="mt-1 text-sm text-gray-600">
                          Watering:{" "}
                          {String(
                            zone.schedule.watering ?? "Not set",
                          )}
                        </p>
                      </div>

                      <div className="flex shrink-0 gap-3">
                        <button
                          type="button"
                          onClick={() => startEditingZone(zone)}
                          disabled={loading}
                          className="text-sm font-medium text-green-700 hover:text-green-900 disabled:opacity-50"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() => deleteZone(zone.id)}
                          disabled={
                            loading ||
                            savedConfig.zones.length <= 1
                          }
                          className="text-sm font-medium text-red-600 hover:text-red-800 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default LocationConfigWizard;