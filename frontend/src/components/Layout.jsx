import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutGrid,
  Ticket,
  Search as SearchIcon,
  BookOpen,
  BarChart3,
  UserRound,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid },
  { to: "/tickets", label: "Tickets", icon: Ticket },
  { to: "/search", label: "Search", icon: SearchIcon },
  { to: "/knowledge-base", label: "Knowledge Base", icon: BookOpen },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/profile", label: "Profile", icon: UserRound },
];

export default function Layout({ children }) {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex bg-paper">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 hidden md:flex flex-col border-r border-line bg-white px-4 py-6">
        <div className="flex items-center gap-3 px-2 mb-8">
          <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center text-white font-display font-semibold text-sm">
            AC
          </div>
          <div>
            <div className="font-display font-semibold text-[15px] leading-tight text-ink">AI Support</div>
            <div className="text-ink-faint text-xs leading-tight -mt-0.5 tracking-wide uppercase">Copilot</div>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-accent-soft text-accent"
                      : "text-ink-soft hover:text-ink hover:bg-paper"
                  }`
                }
              >
                <Icon size={17} strokeWidth={2} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-line pt-4 mt-4">
          <div className="flex items-center gap-3 px-2 mb-3">
            <div className="w-9 h-9 rounded-full bg-accent-soft flex items-center justify-center text-accent font-display font-semibold">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium truncate text-ink">{user?.name}</div>
              <div className="text-xs text-ink-faint capitalize">{user?.role}</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 px-5 py-6 md:px-10 md:py-9">
        <div className="max-w-6xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
