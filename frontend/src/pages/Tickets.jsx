import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, X, AlertTriangle, Paperclip, Loader2 } from "lucide-react";
import { API } from "../api/client";
import { StatusBadge, PriorityBadge, PRIORITY_RAIL } from "../components/Badges";

const CATEGORIES = ["General", "Network", "Software", "Hardware", "Access/Auth", "Email", "Browser", "VS Code/Dev Tools", "Application Crash"];

function NewTicketModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ title: "", description: "", reporter_name: "", reporter_email: "", category: "General", priority: "Medium" });
  const [screenshot, setScreenshot] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [similar, setSimilar] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      if (screenshot) fd.append("screenshot", screenshot);
      const res = await API.createTicket(fd);
      if (res.data.similar_incidents?.length) {
        setSimilar(res.data.similar_incidents);
      }
      onCreated(res.data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create ticket");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-[2px] flex items-center justify-center p-4 z-50">
      <div className="card w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto shadow-pop">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-semibold text-lg text-ink">New support ticket</h2>
          <button onClick={onClose} className="text-ink-faint hover:text-ink">
            <X size={18} />
          </button>
        </div>

        {similar.length > 0 && (
          <div className="mb-4 p-3 rounded-lg bg-signal-medium-soft border border-signal-medium/25">
            <p className="text-signal-medium text-sm font-medium mb-1 flex items-center gap-1.5">
              <AlertTriangle size={14} /> Similar incidents found
            </p>
            {similar.slice(0, 3).map((s) => (
              <div key={s.ticket_id} className="text-xs text-ink-soft">
                {s.similarity}% match — {s.title} {s.resolution ? `(fix: ${s.resolution.slice(0, 60)}...)` : ""}
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <input required placeholder="Title" className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <textarea required placeholder="Describe the issue..." rows={3} className="input-field" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input required placeholder="Your name" className="input-field" value={form.reporter_name} onChange={(e) => setForm({ ...form, reporter_name: e.target.value })} />
            <input required type="email" placeholder="Your email" className="input-field" value={form.reporter_email} onChange={(e) => setForm({ ...form, reporter_email: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <select className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
            <select className="input-field" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
              {["Low", "Medium", "High", "Critical"].map((p) => <option key={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm text-ink-soft mb-1.5 flex items-center gap-1.5">
              <Paperclip size={13} /> Screenshot (optional)
            </label>
            <input type="file" accept="image/*" onChange={(e) => setScreenshot(e.target.files[0])} className="text-sm text-ink-soft" />
          </div>
          {error && <p className="text-signal-critical text-sm">{error}</p>}
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting && <Loader2 size={14} className="animate-spin" />}
            {submitting ? "Creating & analyzing..." : "Create ticket"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filters, setFilters] = useState({ status: "", priority: "" });

  const load = () => {
    setLoading(true);
    API.listTickets(Object.fromEntries(Object.entries(filters).filter(([, v]) => v)))
      .then((res) => setTickets(res.data.tickets))
      .finally(() => setLoading(false));
  };

  useEffect(load, [filters]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="page-title">Tickets</h1>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={15} /> New ticket
        </button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <select className="input-field w-auto" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All statuses</option>
          {["Open", "In Progress", "Resolved"].map((s) => <option key={s}>{s}</option>)}
        </select>
        <select className="input-field w-auto" value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
          <option value="">All priorities</option>
          {["Low", "Medium", "High", "Critical"].map((p) => <option key={p}>{p}</option>)}
        </select>
      </div>

      <div className="card divide-y divide-line-soft">
        {loading && (
          <p className="p-5 text-ink-faint text-sm flex items-center gap-2">
            <Loader2 size={14} className="animate-spin" /> Loading tickets
          </p>
        )}
        {!loading && tickets.length === 0 && <p className="p-5 text-ink-faint text-sm">No tickets found.</p>}
        {tickets.map((t) => (
          <Link key={t.id} to={`/tickets/${t.id}`} className="priority-rail flex items-center justify-between gap-3 pl-6 pr-5 py-4 hover:bg-paper transition-colors">
            <span className={`absolute left-3 top-2 bottom-2 w-[3px] rounded-full ${PRIORITY_RAIL[t.priority] || "bg-line"}`} />
            <div className="min-w-0">
              <div className="font-medium truncate text-ink text-sm">{t.title}</div>
              <div className="text-xs text-ink-faint truncate mt-0.5">{t.category} &middot; {t.reporter_name} &middot; {new Date(t.created_at).toLocaleDateString()}</div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <PriorityBadge priority={t.priority} />
              <StatusBadge status={t.status} />
            </div>
          </Link>
        ))}
      </div>

      {showModal && (
        <NewTicketModal
          onClose={() => setShowModal(false)}
          onCreated={() => {
            setShowModal(false);
            load();
          }}
        />
      )}
    </div>
  );
}
