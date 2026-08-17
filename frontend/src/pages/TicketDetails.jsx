import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  BrainCircuit,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Trash2,
  Save,
  Bot,
  Loader2,
  Send,
} from "lucide-react";
import { API, UPLOADS_BASE } from "../api/client";
import { StatusBadge, PriorityBadge } from "../components/Badges";

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-ink-faint mb-1">
        <span>{label}</span>
        <span className="font-mono">{value ?? 0}/100</span>
      </div>
      <div className="h-1.5 bg-line-soft rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${value ?? 0}%` }} />
      </div>
    </div>
  );
}

export default function TicketDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chat, setChat] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [similar, setSimilar] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [resolveDraft, setResolveDraft] = useState(null);
  const [resolveForm, setResolveForm] = useState(null);
  const chatEndRef = useRef(null);

  const load = async () => {
    setLoading(true);
    const [t, c] = await Promise.all([API.getTicket(id), API.getChat(id)]);
    setTicket(t.data);
    setChat(c.data.messages);
    setLoading(false);
  };

  useEffect(() => { load(); }, [id]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chat]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await API.analyzeTicket(id);
      setTicket((t) => ({ ...t, ai_analysis: res.data.ai_analysis }));
      setSimilar(res.data.similar_incidents || []);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatInput("");
    setChat((c) => [...c, { role: "user", content: msg, created_at: new Date() }]);
    setChatLoading(true);
    try {
      const res = await API.askAssistant(id, msg);
      setChat((c) => [...c, { role: "assistant", content: res.data.reply, created_at: new Date() }]);
      if (res.data.similar_incidents) setSimilar(res.data.similar_incidents);
    } finally {
      setChatLoading(false);
    }
  };

  const handleStatusChange = async (status) => {
    const res = await API.updateTicket(id, { status });
    setTicket(res.data);
  };

  const handleDraftResolution = async () => {
    const res = await API.draftResolution(id);
    setResolveDraft(res.data.draft);
    setResolveForm(res.data.draft);
  };

  const handleSaveResolution = async (e) => {
    e.preventDefault();
    await API.saveResolution(id, resolveForm);
    setResolveDraft(null);
    load();
  };

  const handleDelete = async () => {
    if (!confirm("Delete this ticket permanently?")) return;
    await API.deleteTicket(id);
    navigate("/tickets");
  };

  if (loading || !ticket) {
    return (
      <p className="text-ink-faint text-sm flex items-center gap-2">
        <Loader2 size={14} className="animate-spin" /> Loading ticket
      </p>
    );
  }

  const a = ticket.ai_analysis || {};

  return (
    <div className="space-y-6">
      <button onClick={() => navigate("/tickets")} className="text-sm text-ink-faint hover:text-ink-soft flex items-center gap-1.5">
        <ArrowLeft size={14} /> Back to tickets
      </button>

      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="page-title">{ticket.title}</h1>
          <div className="flex items-center gap-2 mt-2.5">
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
            <span className="text-xs text-ink-faint">{ticket.category}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <select className="input-field w-auto" value={ticket.status} onChange={(e) => handleStatusChange(e.target.value)}>
            {["Open", "In Progress", "Resolved"].map((s) => <option key={s}>{s}</option>)}
          </select>
          <button onClick={handleDelete} className="icon-btn hover:text-signal-critical hover:border-signal-critical/40">
            <Trash2 size={15} />
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left column: details + AI analysis */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-5">
            <h2 className="font-display font-semibold text-ink mb-3 flex items-center gap-2">
              <FileText size={16} strokeWidth={1.75} className="text-ink-faint" /> Description
            </h2>
            <p className="text-ink-soft text-sm whitespace-pre-wrap leading-relaxed">{ticket.description}</p>
            <div className="text-xs text-ink-faint mt-3">
              Reported by {ticket.reporter_name} ({ticket.reporter_email})
            </div>
            {ticket.screenshot_url && (
              <img
                src={`${UPLOADS_BASE}${ticket.screenshot_url}`}
                alt="Screenshot"
                className="mt-4 rounded-lg border border-line max-h-96 object-contain"
              />
            )}
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-display font-semibold text-ink flex items-center gap-2">
                <BrainCircuit size={16} strokeWidth={1.75} className="text-ink-faint" /> AI analysis
              </h2>
              <button onClick={handleAnalyze} disabled={analyzing} className="btn-secondary text-sm">
                <RefreshCw size={13} className={analyzing ? "animate-spin" : ""} />
                {analyzing ? "Analyzing..." : "Re-analyze"}
              </button>
            </div>
            {a.summary ? (
              <div className="space-y-4">
                <p className="text-ink-soft text-sm leading-relaxed">{a.summary}</p>
                <div className="grid sm:grid-cols-2 gap-3 text-sm">
                  <div><span className="text-ink-faint">Root cause: </span><span className="text-ink">{a.root_cause}</span></div>
                  <div><span className="text-ink-faint">Suggested fix: </span><span className="text-ink">{a.suggested_resolution}</span></div>
                </div>
                <div className="grid sm:grid-cols-3 gap-4 pt-2">
                  <ScoreBar label="Business impact" value={a.business_impact_score} color="bg-signal-critical" />
                  <ScoreBar label="Urgency" value={a.urgency_score} color="bg-signal-high" />
                  <ScoreBar label="Complexity" value={a.complexity_score} color="bg-accent" />
                </div>
              </div>
            ) : (
              <p className="text-ink-faint text-sm">No analysis yet — click re-analyze to generate one.</p>
            )}
          </div>

          {similar.length > 0 && (
            <div className="card p-5">
              <h2 className="font-display font-semibold text-ink mb-3 flex items-center gap-2">
                <AlertTriangle size={16} strokeWidth={1.75} className="text-ink-faint" /> Similar incidents
              </h2>
              <div className="space-y-2">
                {similar.map((s) => (
                  <div key={s.ticket_id} className="flex items-center justify-between text-sm px-3 py-2.5 rounded-lg bg-paper">
                    <div>
                      <div className="font-medium text-ink">{s.title}</div>
                      {s.resolution && <div className="text-xs text-ink-faint mt-0.5">Fix: {s.resolution.slice(0, 80)}</div>}
                    </div>
                    <span className="text-accent font-mono text-xs shrink-0 ml-3">{s.similarity}% match</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-display font-semibold text-ink flex items-center gap-2">
                <CheckCircle2 size={16} strokeWidth={1.75} className="text-ink-faint" /> Resolution
              </h2>
              {ticket.status !== "Resolved" && !resolveDraft && (
                <button onClick={handleDraftResolution} className="btn-secondary text-sm">
                  <Bot size={13} /> Draft with AI
                </button>
              )}
            </div>
            {resolveDraft ? (
              <form onSubmit={handleSaveResolution} className="space-y-3">
                {["root_cause", "actions_taken", "resolution_summary", "outcome"].map((field) => (
                  <div key={field}>
                    <label className="text-xs text-ink-faint uppercase tracking-wide">{field.replace("_", " ")}</label>
                    <textarea
                      className="input-field mt-1"
                      rows={2}
                      value={resolveForm[field] || ""}
                      onChange={(e) => setResolveForm({ ...resolveForm, [field]: e.target.value })}
                    />
                  </div>
                ))}
                <div className="flex gap-2">
                  <button type="submit" className="btn-primary">
                    <Save size={14} /> Save & resolve
                  </button>
                  <button type="button" onClick={() => setResolveDraft(null)} className="btn-secondary">Cancel</button>
                </div>
              </form>
            ) : (
              <p className="text-ink-faint text-sm">
                {ticket.status === "Resolved" ? "Ticket resolved." : "Not resolved yet."}
              </p>
            )}
          </div>
        </div>

        {/* Right column: AI Assistant chat */}
        <div className="card p-5 flex flex-col h-[640px]">
          <h2 className="font-display font-semibold text-ink mb-3 flex items-center gap-2">
            <Bot size={16} strokeWidth={1.75} className="text-ink-faint" /> Ask AI assistant
          </h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {chat.length === 0 && (
              <p className="text-ink-faint text-sm">Ask about root cause, next steps, or how to fix this issue.</p>
            )}
            {chat.map((m, i) => (
              <div key={i} className={`text-sm rounded-lg px-3 py-2 whitespace-pre-wrap leading-relaxed ${m.role === "user" ? "bg-accent-soft text-ink ml-6" : "bg-paper text-ink-soft mr-2"}`}>
                {m.content}
              </div>
            ))}
            {chatLoading && (
              <div className="text-ink-faint text-sm flex items-center gap-2">
                <Loader2 size={13} className="animate-spin" /> Thinking
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleAsk} className="mt-3 flex gap-2">
            <input
              className="input-field"
              placeholder="Ask a question..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="submit" className="btn-primary shrink-0 px-3" disabled={chatLoading}>
              <Send size={15} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
