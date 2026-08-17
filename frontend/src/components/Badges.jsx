import { Circle, CircleDot, CheckCircle2, Flame } from "lucide-react";

const STATUS_STYLES = {
  Open: "bg-signal-high-soft text-signal-high",
  "In Progress": "bg-signal-medium-soft text-signal-medium",
  Resolved: "bg-signal-low-soft text-signal-low",
};

const PRIORITY_STYLES = {
  Low: "bg-signal-low-soft text-signal-low",
  Medium: "bg-signal-medium-soft text-signal-medium",
  High: "bg-signal-high-soft text-signal-high",
  Critical: "bg-signal-critical-soft text-signal-critical",
};

// Shared source of truth for the priority-rail signature element used
// across ticket lists, so the same color always means the same thing.
export const PRIORITY_RAIL = {
  Low: "bg-signal-low",
  Medium: "bg-signal-medium",
  High: "bg-signal-high",
  Critical: "bg-signal-critical",
};

const STATUS_ICON = { Open: CircleDot, "In Progress": Circle, Resolved: CheckCircle2 };
const PRIORITY_ICON = { Low: Circle, Medium: Circle, High: Circle, Critical: Flame };

export function StatusBadge({ status }) {
  const Icon = STATUS_ICON[status] || Circle;
  return (
    <span className={`badge ${STATUS_STYLES[status] || "bg-paper text-ink-soft"}`}>
      <Icon size={12} strokeWidth={2.5} />
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const Icon = PRIORITY_ICON[priority] || Circle;
  return (
    <span className={`badge ${PRIORITY_STYLES[priority] || "bg-paper text-ink-soft"}`}>
      <Icon size={12} strokeWidth={2.5} />
      {priority}
    </span>
  );
}
