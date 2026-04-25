export function SchedulePanel() {
  const tasks = [
    { resource: "Tube Furnace A", tasks: [
      { name: "Synthesis (Batch 1)", start: 0, duration: 8, status: "complete" },
      { name: "Synthesis (Batch 2)", start: 10, duration: 8, status: "active" },
      { name: "Synthesis (Batch 3)", start: 20, duration: 8, status: "pending" },
    ]},
    { resource: "Glove Box #3", tasks: [
      { name: "Sample prep", start: 0, duration: 2, status: "complete" },
      { name: "Pellet pressing", start: 8, duration: 3, status: "complete" },
      { name: "Storage", start: 18, duration: 1, status: "pending" },
    ]},
    { resource: "XRD Instrument", tasks: [
      { name: "Phase analysis", start: 9, duration: 4, status: "active" },
      { name: "Structure refinement", start: 14, duration: 3, status: "pending" },
    ]},
    { resource: "Impedance Analyzer", tasks: [
      { name: "RT measurements", start: 10, duration: 3, status: "pending" },
      { name: "Temp sweep", start: 15, duration: 10, status: "pending" },
    ]},
  ];

  const hours = Array.from({ length: 30 }, (_, i) => i);

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm text-stone-600">Resource Timeline</h3>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-600 rounded" />
            <span className="text-stone-600">Complete</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-600 rounded" />
            <span className="text-stone-600">Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-amber-700 rounded" />
            <span className="text-stone-600">Pending</span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[800px]">
          <div className="flex mb-2">
            <div className="w-48 flex-shrink-0" />
            <div className="flex-1 flex border-b border-amber-200">
              {hours.map((hour) => (
                <div
                  key={hour}
                  className="flex-1 text-center text-xs text-stone-600 pb-2"
                >
                  {hour % 5 === 0 ? `${hour}h` : ""}
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {tasks.map((row, idx) => (
              <div key={idx} className="flex items-center">
                <div className="w-48 flex-shrink-0 pr-4">
                  <div className="text-sm text-stone-900">{row.resource}</div>
                </div>

                <div className="flex-1 relative h-10 bg-amber-50/50 rounded">
                  <div className="absolute inset-0 flex">
                    {hours.map((hour) => (
                      <div
                        key={hour}
                        className="flex-1 border-r border-amber-200/50"
                      />
                    ))}
                  </div>

                  {row.tasks.map((task, taskIdx) => {
                    const colors = {
                      complete: "bg-green-600",
                      active: "bg-blue-600",
                      pending: "bg-amber-700",
                    };

                    const left = (task.start / 30) * 100;
                    const width = (task.duration / 30) * 100;

                    return (
                      <div
                        key={taskIdx}
                        className={`absolute top-1 bottom-1 ${colors[task.status]} rounded px-2 flex items-center text-xs text-white`}
                        style={{
                          left: `${left}%`,
                          width: `${width}%`,
                        }}
                      >
                        <span className="truncate">{task.name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-4 bg-amber-50/50 rounded">
          <div className="text-xs text-stone-600 mb-1 font-mono">TOTAL DURATION</div>
          <div className="text-2xl text-stone-900">28 hours</div>
        </div>
        <div className="p-4 bg-amber-50/50 rounded">
          <div className="text-xs text-stone-600 mb-1 font-mono">RESOURCE UTILIZATION</div>
          <div className="text-2xl text-stone-900">67%</div>
        </div>
        <div className="p-4 bg-amber-50/50 rounded">
          <div className="text-xs text-stone-600 mb-1 font-mono">IDLE TIME</div>
          <div className="text-2xl text-stone-900">9.2 hours</div>
        </div>
      </div>
    </div>
  );
}
