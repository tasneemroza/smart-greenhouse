import { useEffect, useState } from "react";
import {
  evaluateAutomation,
  fetchLocations,
  saveAutomationStrategy,
  type AutomationEvaluationDto,
  type AutomationStrategyKey,
  type LocationDto,
} from "../../services/api";

export default function AutomationPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [strategy, setStrategy] = useState<AutomationStrategyKey>("conservative");
  const [result, setResult] = useState<AutomationEvaluationDto | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    fetchLocations()
      .then((items) => {
        if (!active) return;
        setLocations(items);
        if (items.length) setLocationId(items[0].id);
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Could not load locations.");
      });
    return () => {
      active = false;
    };
  }, []);

  async function saveStrategy() {
    if (!locationId) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await saveAutomationStrategy(locationId, strategy);
      setMessage("Strategy saved successfully.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save strategy.");
    } finally {
      setBusy(false);
    }
  }

  async function evaluateStrategy() {
    if (!locationId) return;
    setBusy(true);
    setError("");
    setMessage("");
    setResult(null);
    try {
      const response = await evaluateAutomation(locationId);
      setResult(response);
      setStrategy(response.strategy_key);
      setMessage("Evaluation completed.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not evaluate automation.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 className="text-base font-semibold text-[#315747]">Automation</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[#6F7C73]">
        Choose a location, save its strategy, and evaluate zone recommendations.
      </p>

      <div className="mt-6 space-y-5">
        <div>
          <label htmlFor="automation-location" className="mb-2 block text-sm font-bold text-[#293B32]">Location</label>
          <select
            id="automation-location"
            value={locationId}
            onChange={(event) => {
              setLocationId(event.target.value);
              setResult(null);
              setMessage("");
              setError("");
            }}
            disabled={locations.length === 0 || busy}
            className="w-full rounded-xl border border-[#DDE5DC] bg-white px-4 py-3 text-sm text-[#293B32] shadow-sm outline-none transition focus:border-[#71977A] focus:ring-4 focus:ring-[#E7EFE6] disabled:cursor-not-allowed disabled:bg-gray-50"
          >
            {locations.length === 0 && <option value="">No locations available</option>}
            {locations.map((location) => (
              <option key={location.id} value={location.id}>{location.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="automation-strategy" className="mb-2 block text-sm font-bold text-[#293B32]">Strategy</label>
          <select
            id="automation-strategy"
            value={strategy}
            onChange={(event) => setStrategy(event.target.value as AutomationStrategyKey)}
            className="w-full rounded-xl border border-[#DDE5DC] bg-white px-4 py-3 text-sm text-[#293B32] shadow-sm outline-none transition focus:border-[#71977A] focus:ring-4 focus:ring-[#E7EFE6] disabled:cursor-not-allowed disabled:bg-gray-50"
          >
            <option value="conservative">Conservative</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={saveStrategy}
            disabled={!locationId || busy}
            className="rounded-xl bg-[#315747] px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#254536] focus:outline-none focus:ring-2 focus:ring-[#71977A] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? "Please wait..." : "Save strategy"}
          </button>
          <button
            type="button"
            onClick={evaluateStrategy}
            disabled={!locationId || busy}
            className="rounded-xl border border-[#C9D8CA] bg-[#F4F7F1] px-5 py-3 text-base font-bold text-[#315747] transition-colors hover:bg-[#E7EFE6] focus:outline-none focus:ring-2 focus:ring-[#71977A] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Evaluate
          </button>
        </div>

        {message && <p role="status" className="rounded-xl border border-[#C9D8CA] bg-[#F4F7F1] px-4 py-3 text-sm font-medium text-[#315747]">{message}</p>}
        {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</p>}

        {result && (
          <div className="space-y-4 border-t border-[#DDE5DC] pt-5">
            <p className="text-base font-bold text-[#315747]">Results · {result.strategy_key}</p>
            {result.recommendations.length === 0 && (
              <p className="text-sm text-[#6F7C73]">No zones found for this location.</p>
            )}
            {result.recommendations.map((item) => (
              <div key={item.zone_id} className="rounded-2xl border border-[#DDE5DC] bg-[#FAFBF8] p-4 transition-colors hover:border-[#C9D8CA]">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-bold text-[#293B32]">{item.zone_name}</p>
                  <span className="rounded-full bg-[#E7EFE6] px-3 py-1 text-xs font-bold capitalize text-[#315747]">
                    {item.action}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-5 text-[#6F7C73]">{item.reason}</p>
                {item.intensity !== null && (
                  <p className="mt-2 text-xs text-[#6F7C73]">Intensity: {item.intensity}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

