import { useCallback, useEffect, useState } from "react";
import {
  fetchActuatorExecutions,
  type ActuatorExecutionDto,
} from "../../services/api";

export default function ExecutionLog() {
  const [executions, setExecutions] = useState<ActuatorExecutionDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadExecutions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const records = await fetchActuatorExecutions(20);
      setExecutions(records);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load executions",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadExecutions();
  }, [loadExecutions]);

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#293B32]">
            Actuator Execution Log
          </h2>
          <p className="mt-1 text-sm text-[#6F7C73]">
            Recent actuator commands and applied execution policies.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadExecutions()}
          disabled={loading}
          className="rounded-full bg-[#315747] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#264637] disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div role="alert" className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && executions.length === 0 ? (
        <p className="py-8 text-center text-sm text-[#6F7C73]">
          Loading execution history...
        </p>
      ) : !loading && !error && executions.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[#DDE5DC] bg-[#F6F7F2] px-4 py-10 text-center">
          <p className="font-medium text-[#315747]">
            No actuator executions yet
          </p>
          <p className="mt-2 text-sm text-[#6F7C73]">
            Execution records will appear here after an actuator command is attempted.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[#DDE5DC]">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[#E7EFE6] text-[#315747]">
              <tr>
                <th scope="col" className="px-4 py-3 font-semibold">Time</th>
                <th scope="col" className="px-4 py-3 font-semibold">Device ID</th>
                <th scope="col" className="px-4 py-3 font-semibold">Status</th>
                <th scope="col" className="px-4 py-3 font-semibold">Policies</th>
                <th scope="col" className="px-4 py-3 font-semibold">Message</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-[#DDE5DC]">
              {executions.map((execution) => (
                <tr key={execution.id} className="hover:bg-[#F6F7F2]">
                  <td className="whitespace-nowrap px-4 py-3 text-[#52675A]">
                    {new Date(execution.created_at).toLocaleString()}
                  </td>

                  <td className="px-4 py-3 font-mono text-xs text-[#52675A]">
                    {execution.device_id}
                  </td>

                  <td className="px-4 py-3">
                    <span
                      className={
                        execution.success
                          ? "rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800"
                          : "rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800"
                      }
                    >
                      {execution.success ? "Success" : "Blocked / Failed"}
                    </span>
                  </td>

                  <td className="px-4 py-3 text-[#52675A]">
                    {execution.policy_applied.join(", ") || "None"}
                  </td>

                  <td className="px-4 py-3 text-[#52675A]">
                    {execution.message || "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="mt-3 text-xs text-[#6F7C73]">
        Showing up to 20 most recent execution attempts. Use Refresh to load new records.
      </p>
    </div>
  );
}
