import { useEffect, useState } from "react";
import { Plus, X, Save, Pencil, Trash2, Tag, Search as SearchIcon, Loader2 } from "lucide-react";
import { API } from "../api/client";
import { useAuth } from "../context/AuthContext";

function ArticleModal({ article, onClose, onSaved }) {
  const [form, setForm] = useState(article || { title: "", content: "", tags: [] });
  const [tagsInput, setTagsInput] = useState((article?.tags || []).join(", "));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = { ...form, tags: tagsInput.split(",").map((t) => t.trim()).filter(Boolean) };
    if (article?.id) {
      await API.updateKB(article.id, payload);
    } else {
      await API.createKB(payload);
    }
    onSaved();
  };

  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-[2px] flex items-center justify-center p-4 z-50">
      <div className="card w-full max-w-lg p-6 shadow-pop">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-semibold text-lg text-ink">{article ? "Edit" : "New"} article</h2>
          <button onClick={onClose} className="text-ink-faint hover:text-ink">
            <X size={18} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input required placeholder="Title" className="input-field" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <textarea required placeholder="Content" rows={6} className="input-field" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
          <input placeholder="Tags (comma separated)" className="input-field" value={tagsInput} onChange={(e) => setTagsInput(e.target.value)} />
          <button type="submit" className="btn-primary w-full">
            <Save size={14} /> Save article
          </button>
        </form>
      </div>
    </div>
  );
}

export default function KnowledgeBase() {
  const { user } = useAuth();
  const [articles, setArticles] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const load = () => {
    setLoading(true);
    API.listKB(q).then((res) => setArticles(res.data.articles)).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleDelete = async (id) => {
    if (!confirm("Delete this article?")) return;
    await API.deleteKB(id);
    load();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="page-title">Knowledge base</h1>
        {user?.role === "admin" && (
          <button onClick={() => { setEditing(null); setModalOpen(true); }} className="btn-primary">
            <Plus size={15} /> Add article
          </button>
        )}
      </div>

      <form onSubmit={(e) => { e.preventDefault(); load(); }} className="flex gap-2">
        <input className="input-field" placeholder="Search articles..." value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn-secondary shrink-0">
          <SearchIcon size={14} /> Search
        </button>
      </form>

      {loading && (
        <p className="text-ink-faint text-sm flex items-center gap-2">
          <Loader2 size={14} className="animate-spin" /> Loading
        </p>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {articles.map((a) => (
          <div key={a.id} className="card p-4">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-display font-semibold text-ink">{a.title}</h3>
              {user?.role === "admin" && (
                <div className="flex gap-1 shrink-0">
                  <button onClick={() => { setEditing(a); setModalOpen(true); }} className="text-ink-faint hover:text-accent p-1">
                    <Pencil size={14} />
                  </button>
                  <button onClick={() => handleDelete(a.id)} className="text-ink-faint hover:text-signal-critical p-1">
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </div>
            <p className="text-ink-soft text-sm mt-2 line-clamp-3 leading-relaxed">{a.content}</p>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {a.tags?.map((t) => (
                <span key={t} className="badge bg-paper text-ink-soft border border-line">
                  <Tag size={11} /> {t}
                </span>
              ))}
            </div>
          </div>
        ))}
        {!loading && articles.length === 0 && <p className="text-ink-faint text-sm">No articles yet.</p>}
      </div>

      {modalOpen && (
        <ArticleModal
          article={editing}
          onClose={() => setModalOpen(false)}
          onSaved={() => { setModalOpen(false); load(); }}
        />
      )}
    </div>
  );
}
