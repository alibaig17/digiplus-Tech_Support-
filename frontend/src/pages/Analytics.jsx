import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { ClipboardList, CircleDot, Clock, CheckCircle2, Flame, Flame as FireIcon, Loader2 } from "lucide-react";
import { API } from "../api/client";

const COLORS = ["#28345E", "#B8752A", "#9C7F14", "#2F7D57", "#B23B32", "#3E5CC4"];

const TOOLTIP_STYLE = {
  background: "#FFFFFF",
  border: "1px solid #E6E4DD",
  borderRadius: 10,
  fontSize: 13,
  color: "#15171E",
  boxShadow: "0 8px 24px rgba(21,23,30,0.08)",
};

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    API.analyticsOverview().then((res) => setData(res.data));
  }, []);

  if (!data) {
    return (
      <p className="text-ink-faint text-sm flex items-center gap-2">
        <Loader2 size={14} className="animate-spin" /> Loading analytics
      </p>
    );
  }

  const statusData = Object.entries(data.by_status).map(([name, value]) => ({ name, value }));
  const categoryData = Object.entries(data.by_category).map(([name, value]) => ({ name, value }));
  const priorityData = Object.entries(data.by_priority).map(([name, value]) => ({ name, value }));

  const cards = [
    { label: "Total tickets", value: data.total_tickets, icon: ClipboardList },
    { label: "Open", value: data.open_tickets, icon: CircleDot },
    { label: "In progress", value: data.in_progress_tickets, icon: Clock },
    { label: "Resolved", value: data.resolved_tickets, icon: CheckCircle2 },
    { label: "Critical", value: data.critical_tickets, icon: Flame },
  ];

  return (
    <div className="space-y-6">
      <h1 className="page-title">Analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className="card p-4">
              <Icon size={18} strokeWidth={1.75} className="text-ink-faint mb-3" />
              <div className="text-2xl font-display font-semibold text-ink">{c.value}</div>
              <div className="text-xs text-ink-faint mt-1">{c.label}</div>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="font-display font-semibold text-ink mb-4">Tickets by status</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3}>
                {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold text-ink mb-4">Tickets by priority</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={priorityData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3}>
                {priorityData.map((_, i) => <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5 lg:col-span-2">
          <h2 className="font-display font-semibold text-ink mb-4">Tickets by category</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#EFEEE8" />
              <XAxis dataKey="name" stroke="#8A8F9A" fontSize={12} />
              <YAxis stroke="#8A8F9A" fontSize={12} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "#F7F7F3" }} />
              <Bar dataKey="value" fill="#28345E" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5 lg:col-span-2">
          <h2 className="font-display font-semibold text-ink mb-4 flex items-center gap-2">
            <FireIcon size={16} strokeWidth={1.75} className="text-ink-faint" /> Most common issues
          </h2>
          <div className="space-y-2">
            {data.most_common_issues.map((i, idx) => (
              <div key={i.issue} className="flex items-center gap-3">
                <span className="text-ink-faint w-5 text-sm font-mono">{idx + 1}.</span>
                <span className="flex-1 text-sm text-ink">{i.issue}</span>
                <span className="text-accent font-mono text-sm">{i.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
