import { FlaskConical, ClipboardList, Activity, Flag } from "lucide-react";

type DashboardSection = "intake" | "planning" | "runtime" | "outcomes";

interface SidebarProps {
  currentSection: DashboardSection;
  onSectionChange: (section: DashboardSection) => void;
  sectionSubtabs: Record<DashboardSection, Array<{ id: string; label: string }>>;
  currentSubtab: Record<DashboardSection, string>;
  onSubtabChange: (section: DashboardSection, tabId: string) => void;
}

const sections = [
  { id: "intake", label: "Intake & Prior Work", icon: FlaskConical },
  { id: "planning", label: "Planning Pipeline", icon: ClipboardList },
  { id: "runtime", label: "Runtime Pipeline", icon: Activity },
  { id: "outcomes", label: "Outcomes & Provenance", icon: Flag },
] as const;

export function Sidebar({
  currentSection,
  onSectionChange,
  sectionSubtabs,
  currentSubtab,
  onSubtabChange,
}: SidebarProps) {
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
            <div key={section.id}>
              <button
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
              {isActive && (
                <div className="ml-3 mb-2 mt-1 space-y-1 border-l border-amber-300 pl-2">
                  {sectionSubtabs[section.id].map((tab) => {
                    const tabActive = currentSubtab[section.id] === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => onSubtabChange(section.id, tab.id)}
                        className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
                          tabActive
                            ? "bg-green-600 text-white"
                            : "text-stone-700 hover:bg-amber-100"
                        }`}
                      >
                        {tab.label}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
