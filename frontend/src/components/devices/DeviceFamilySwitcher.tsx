import { Monitor, Cpu } from "lucide-react";
import type { DeviceFamily } from "../../services/api";

type DeviceFamilySwitcherProps = {
  selectedFamily: DeviceFamily;
  onChange: (family: DeviceFamily) => void;
};

export default function DeviceFamilySwitcher({
  selectedFamily,
  onChange,
}: DeviceFamilySwitcherProps) {
  const baseStyle =
    "rounded-xl border px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#344A4F] focus:ring-offset-2";

  const selectedStyle =
    "border-[#344A4F] bg-[#344A4F] text-white shadow-md";

  const unselectedStyle =
    "border-[#D8C5B8] bg-[#F3E6DC] text-[#344A4F] hover:border-[#B98C72] hover:bg-[#EAD5C6]";

  return (
    <div className="mb-6 inline-flex flex-wrap gap-2 rounded-2xl border border-[#D8C5B8] bg-[#F6F8F7] p-2 shadow-sm">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        aria-pressed={selectedFamily === "simulation"}
        className={`${baseStyle} ${
          selectedFamily === "simulation"
            ? selectedStyle
            : unselectedStyle
        }`}
      >
        <Monitor size={18} aria-hidden="true" className="mr-2 inline-block align-middle" />
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        aria-pressed={selectedFamily === "edge"}
        className={`${baseStyle} ${
          selectedFamily === "edge"
            ? selectedStyle
            : unselectedStyle
        }`}
      >
        <Cpu size={18} aria-hidden="true" className="mr-2 inline-block align-middle" />
        Edge Hardware
      </button>
    </div>
  );
}