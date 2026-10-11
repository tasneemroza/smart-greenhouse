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
    <div className="mb-6 inline-flex flex-wrap gap-2 rounded-2xl border border-gray-200 bg-gray-50 p-2 shadow-sm">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        aria-pressed={selectedFamily === "simulation"}
        className={`rounded-xl px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 ${
          selectedFamily === "simulation"
            ? "bg-blue-600 text-white shadow-md"
            : "bg-transparent text-gray-600 hover:bg-white hover:text-gray-900"
        }`}
      >
        <span className="mr-2" aria-hidden="true">
          ◉
        </span>
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        aria-pressed={selectedFamily === "edge"}
        className={`rounded-xl px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 ${
          selectedFamily === "edge"
            ? "bg-blue-600 text-white shadow-md"
            : "bg-transparent text-gray-600 hover:bg-white hover:text-gray-900"
        }`}
      >
        <span className="mr-2" aria-hidden="true">
          ◈
        </span>
        Edge Hardware
      </button>
    </div>
  );
}
