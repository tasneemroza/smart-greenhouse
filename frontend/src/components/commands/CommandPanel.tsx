import { useEffect, useState } from "react";
import {
  executeCommand,
  fetchCommandHistory,
  fetchDevices,
  type CommandResultDto,
  type DeviceDto,
} from "../../services/api";

export default function CommandPanel() {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [history, setHistory] = useState<CommandResultDto[]>([]);
  const [level, setLevel] = useState(1);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    const [deviceData, commandData] = await Promise.all([
      fetchDevices({ role: "actuator" }),
      fetchCommandHistory(20),
    ]);

    setDevices(deviceData);
    setHistory(commandData);
    setSelectedId((previous) =>
      deviceData.some((device) => device.id === previous)
        ? previous
        : (deviceData[0]?.id ?? ""),
    );
  }

  useEffect(() => {
    refresh().catch((err) => setError(String(err)));
  }, []);

  const selected = devices.find((device) => device.id === selectedId);

  const commandLabels: Record<string, string> = {
    start_pump: "Start Pump",
    stop_pump: "Stop Pump",
    start_grow_light: "Start Grow Light",
    stop_grow_light: "Stop Grow Light",
    set_light_level: "Set Light Level",
  };

  const allowedCommands = selected?.allowed_commands ?? [];

  const isGrowLight = allowedCommands.some(
    (command) => command.includes("grow_light") ||
      command === "set_light_level"
  );

  const deviceCommands = isGrowLight
    ? ["start_grow_light", "stop_grow_light", "set_light_level"]
    : ["start_pump", "stop_pump"];

  async function runCommand(commandType: string) {
    if (
      !selected ||
      busy ||
      !allowedCommands.includes(commandType)
    ) {
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");

    try {
      const result = await executeCommand({
        device_id: selected.id,
        command_type: commandType,
        payload:
          commandType === "set_light_level"
            ? { level }
            : {},
      });

      setMessage(
        `${commandType}: ${result.status}` +
          (result.error_message
            ? ` - ${result.error_message}`
            : ""),
      );

      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      await refresh().catch(() => {});
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-[#D7E5E3] p-5">
        <h3 className="mb-4 text-lg font-semibold">
          Actuator Controls
        </h3>

        <label
          htmlFor="actuator-select"
          className="mb-2 block text-sm font-medium"
        >
          Select actuator
        </label>

        <select
          id="actuator-select"
          value={selectedId}
          onChange={(event) => setSelectedId(event.target.value)}
          className="w-full rounded-lg border border-[#D7E5E3] p-3"
        >
          {devices.map((device) => (
            <option key={device.id} value={device.id}>
              {device.display_name} ({device.state ?? "unknown"})
            </option>
          ))}
        </select>

        {selected && (
          <div className="mt-4 space-y-4">
            <p className="text-sm">
              <strong>State:</strong> {selected.state}
            </p>

            <p className="text-sm">
              <strong>Family:</strong> {selected.device_family}
            </p>

            {isGrowLight && (
              <div>
                <label
                  htmlFor="light-level"
                  className="mb-2 block text-sm"
                >
                  Light level: {level}%
                </label>

                <input
                  id="light-level"
                  type="range"
                  min={0}
                  max={100}
                  value={level}
                  onChange={(event) =>
                    setLevel(Number(event.target.value))
                  }
                  className="w-full"
                />
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              {deviceCommands.map((command) => (
                <button
                  key={command}
                  type="button"
                  disabled={
                    busy || !allowedCommands.includes(command)
                  }
                  onClick={() => runCommand(command)}
                  className="rounded-lg bg-[#344A4F] px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {busy ? "Executing..." : commandLabels[command]}
                </button>
              ))}
            </div>
          </div>
        )}

        {message && (
          <p role="status" className="mt-4 text-sm text-[#344A4F]">
            {message}
          </p>
        )}

        {error && (
          <p role="alert" className="mt-4 text-sm text-red-700">
            {error}
          </p>
        )}
      </div>

      <div className="rounded-xl border border-[#D7E5E3] p-5">
        <h3 className="mb-4 text-lg font-semibold">
          Recent Command History
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="p-2">Command</th>
                <th className="p-2">Status</th>
                <th className="p-2">Time</th>
                <th className="p-2">Message</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry) => (
                <tr key={entry.id} className="border-b">
                  <td className="p-2">{entry.command_type}</td>
                  <td className="p-2">{entry.status}</td>
                  <td className="p-2">
                    {new Date(entry.created_at).toLocaleString()}
                  </td>
                  <td className="p-2">
                    {entry.error_message ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {history.length === 0 && (
            <p className="py-4 text-sm text-[#68797B]">
              No commands recorded yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}