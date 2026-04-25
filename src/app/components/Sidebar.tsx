import { Target, Network, FileText, Calendar, Play, Database, BarChart3, RefreshCw, ScrollText } from "lucide-react";

interface SidebarProps {
  currentSection: string;
  onSectionChange: (section: string) => void;
}

const sections = [
  { id: "goal", label: "Research Goal", icon: Target },
  { id: "claim-graph", label: "Claim Graph", icon: Network },
  { id: "compiler", label: "Experiment Plan", icon: FileText },
  { id: "schedule", label: "Schedule", icon: Calendar },
  { id: "execution", label: "Execution", icon: Play },
  { id: "validation", label: "Data Validation", icon: Database },
  { id: "results", label: "Results", icon: BarChart3 },
  { id: "next", label: "Next Experiment", icon: RefreshCw },
  { id: "provenance", label: "Provenance Log", icon: ScrollText },
];

export function Sidebar({ currentSection, onSectionChange }: SidebarProps) {
  return (
    <aside className="w-64 border-r border-amber-200 bg-yellow-50/50 flex flex-col shadow-sm">
      <div className="p-4 border-b border-amber-200">
        <h2 className="text-xs text-stone-700 uppercase tracking-wider font-medium">Pipeline</h2>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        {sections.map((section) => {
          const Icon = section.icon;
          const isActive = currentSection === section.id;

          return (
            <button
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded mb-1 transition-colors ${
                isActive
                  ? "bg-green-700 text-white"
                  : "bg-amber-100/50 text-stone-900 hover:bg-amber-100"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm">{section.label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 bg-white rounded-full" />
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
