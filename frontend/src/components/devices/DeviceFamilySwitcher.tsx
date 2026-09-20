import type { DeviceFamily } from "../../services/api";

type DeviceFamilySwitcherProps = {
  selectedFamily: DeviceFamily;
  onChange: (family: DeviceFamily) => void;
};

export default function DeviceFamilySwitcher({
  selectedFamily,
  onChange,
}: DeviceFamilySwitcherProps) {
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        className={`rounded px-4 py-2 ${
          selectedFamily === "simulation"
            ? "bg-blue-600 text-white"
            : "bg-gray-200 text-gray-700 hover:bg-gray-300"
        }`}
      >
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        className={`rounded px-4 py-2 ${
          selectedFamily === "edge"
            ? "bg-blue-600 text-white"
            : "bg-gray-200 text-gray-700 hover:bg-gray-300"
        }`}
      >
        Edge Hardware
      </button>
    </div>
  );
}