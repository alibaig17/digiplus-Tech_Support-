import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ClipboardList,
  CircleDot,
  Clock,
  CheckCircle2,
  Flame,
  Plus,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { API } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { StatusBadge, PriorityBadge, PRIORITY_RAIL } from "../components/Badges";

export default function Dashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([API.analyticsOverview(), API.listTickets({ limit: 6 })])
      .then(([a, t]) => {
        setOverview(a.data);
        setRecent(t.data.tickets);
      })
      .finally(() => setLoading(false));
  }, []);

  const cards = overview
    ? [
        { label: "Total tickets", value: overview.total_tickets, icon: ClipboardList, tone: "text-ink" },
        { label: "Open", value: overview.open_tickets, icon: CircleDot, tone: "text-signal-high" },
        { label: "In progress", value: overview.in_progress_tickets, icon: Clock, tone: "text-signal-medium" },
        { label: "Resolved", value: overview.resolved_tickets, icon: CheckCircle2, tone: "text-signal-low" },
        { label: "Critical", value: overview.critical_tickets, icon: Flame, tone: "text-signal-critical" },
      ]
    : [];

  return (
    <div className="space-y-7">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="page-title">Welcome back, {user?.name?.split(" ")[0]}</h1>
          <p className="text-ink-soft text-sm mt-1.5">Here's what's happening across your support desk.</p>
        </div>
        <Link to="/tickets" className="btn-primary">
          <Plus size={15} /> New ticket
        </Link>
      </div>

      {loading ? (
        <p className="text-ink-faint text-sm flex items-center gap-2">
          <Loader2 size={14} className="animate-spin" /> Loading dashboard
        </p>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {cards.map((c) => {
              const Icon = c.icon;
              return (
                <div key={c.label} className="card p-4">
                  <Icon size={18} strokeWidth={1.75} className={`${c.tone} mb-3`} />
                  <div className={`text-2xl font-display font-semibold ${c.tone}`}>{c.value}</div>
                  <div className="text-xs text-ink-faint mt-1">{c.label}</div>
                </div>
              );
            })}
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display font-semibold text-lg text-ink">Recent tickets</h2>
              <Link to="/tickets" className="text-sm text-accent hover:text-accent-bright flex items-center gap-1">
                View all <ArrowRight size={13} />
              </Link>
            </div>
            <div className="divide-y divide-line-soft">
              {recent.length === 0 && <p className="text-ink-faint text-sm py-3">No tickets yet. Create your first one.</p>}
              {recent.map((t) => (
                <Link
                  key={t.id}
                  to={`/tickets/${t.id}`}
                  className="priority-rail flex items-center justify-between gap-3 py-3.5 px-2 -mx-2 rounded-lg hover:bg-paper transition-colors"
                >
                  <span className={`absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-full ${PRIORITY_RAIL[t.priority] || "bg-line"}`} />
                  <div className="min-w-0">
                    <div className="font-medium truncate text-ink text-sm">{t.title}</div>
                    <div className="text-xs text-ink-faint truncate mt-0.5">{t.category} &middot; {t.reporter_name}</div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <PriorityBadge priority={t.priority} />
                    <StatusBadge status={t.status} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
