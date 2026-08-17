import { useState } from "react";
import { Link } from "react-router-dom";
import { Search as SearchIcon, Loader2 } from "lucide-react";
import { API } from "../api/client";
import { StatusBadge } from "../components/Badges";

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await API.search(q.trim());
      setResults(res.data.results);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="page-title">Historical incident search</h1>
        <p className="text-ink-soft text-sm mt-1.5">Search across ticket title, description, category and resolution.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          className="input-field"
          placeholder="e.g. Outlook login failure, VPN drops, MFA..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button className="btn-primary shrink-0">
          {loading ? <Loader2 size={14} className="animate-spin" /> : <SearchIcon size={14} />}
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      <div className="space-y-3">
        {results.map((r) => (
          <Link key={r.ticket_id} to={`/tickets/${r.ticket_id}`} className="card p-4 flex items-center justify-between gap-4 hover:border-accent-bright/40 transition-colors">
            <div className="min-w-0">
              <div className="text-accent font-mono text-sm font-semibold mb-1">{r.similarity}% match</div>
              <div className="font-medium text-ink">{r.title}</div>
              {r.resolution && <div className="text-sm text-ink-soft mt-1">Resolution: {r.resolution}</div>}
            </div>
            <StatusBadge status={r.status} />
          </Link>
        ))}
        {searched && !loading && results.length === 0 && (
          <p className="text-ink-faint text-sm">No matching incidents found.</p>
        )}
      </div>
    </div>
  );
}
