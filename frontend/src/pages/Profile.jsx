import { useEffect, useState } from "react";
import { Users, Plus, Trash2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { API } from "../api/client";

export default function Profile() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ name: "", email: "", role: "engineer" });
  const [error, setError] = useState("");

  const loadUsers = () => {
    if (user?.role === "admin") {
      API.listUsers().then((res) => setUsers(res.data.users));
    }
  };

  useEffect(loadUsers, [user]);

  const handleAddUser = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await API.createUser(form);
      setForm({ name: "", email: "", role: "engineer" });
      loadUsers();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to add user");
    }
  };

  const handleDeleteUser = async (id) => {
    if (!confirm("Remove this user's access?")) return;
    await API.deleteUser(id);
    loadUsers();
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="page-title">Profile</h1>

      <div className="card p-5 flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-accent-soft flex items-center justify-center text-accent font-display font-semibold text-xl">
          {user?.name?.[0]?.toUpperCase()}
        </div>
        <div>
          <div className="font-medium text-lg text-ink">{user?.name}</div>
          <div className="text-ink-faint text-sm">{user?.email}</div>
          <span className="badge bg-accent-soft text-accent mt-1.5 capitalize">{user?.role}</span>
        </div>
      </div>

      {user?.role === "admin" && (
        <div className="card p-5">
          <h2 className="font-display font-semibold text-ink mb-4 flex items-center gap-2">
            <Users size={16} strokeWidth={1.75} className="text-ink-faint" /> Manage users
          </h2>

          <form onSubmit={handleAddUser} className="grid sm:grid-cols-4 gap-2 mb-5">
            <input required placeholder="Name" className="input-field sm:col-span-1" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input required type="email" placeholder="Email" className="input-field sm:col-span-1" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <select className="input-field sm:col-span-1" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="engineer">Engineer</option>
              <option value="admin">Admin</option>
            </select>
            <button className="btn-primary sm:col-span-1">
              <Plus size={14} /> Add
            </button>
          </form>
          {error && <p className="text-signal-critical text-sm mb-3">{error}</p>}

          <div className="divide-y divide-line-soft">
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between py-2.5">
                <div>
                  <div className="text-sm font-medium text-ink">{u.name}</div>
                  <div className="text-xs text-ink-faint">{u.email}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge bg-paper text-ink-soft border border-line capitalize">{u.role}</span>
                  {u.email !== user.email && (
                    <button onClick={() => handleDeleteUser(u.id)} className="text-ink-faint hover:text-signal-critical p-1">
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
