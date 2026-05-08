import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Props {
  onBack: () => void;
}

export function UsersPage({ onBack }: Props) {
  const [users, setUsers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  async function fetchUsers() {
    setLoading(true);
    try {
      const res = await api.listUsers();
      setUsers(res.users);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(name: string) {
    setDeleting(name);
    try {
      await api.deleteUser(name);
      setUsers((prev) => prev.filter((u) => u !== name));
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Silme başarısız");
    } finally {
      setDeleting(null);
    }
  }

  useEffect(() => { fetchUsers(); }, []);

  return (
    <div className="flex flex-col w-full max-w-md gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-neutral-800">Kayıtlı Kullanıcılar</h2>
        <button
          onClick={fetchUsers}
          className="text-sm text-indigo-600 hover:underline"
        >
          Yenile
        </button>
      </div>

      {loading && (
        <p className="text-center text-neutral-400 py-8">Yükleniyor...</p>
      )}

      {!loading && users.length === 0 && (
        <div className="bg-white rounded-2xl border border-neutral-200 p-8 text-center text-neutral-400">
          Henüz kayıtlı kullanıcı yok.
        </div>
      )}

      {!loading && users.length > 0 && (
        <ul className="flex flex-col gap-2">
          {users.map((user) => (
            <li
              key={user}
              className="flex items-center justify-between bg-white rounded-xl border border-neutral-200 px-4 py-3 shadow-sm"
            >
              <span className="text-neutral-800 font-medium">{user}</span>
              <button
                onClick={() => handleDelete(user)}
                disabled={deleting === user}
                className="text-sm text-red-500 hover:text-red-700 disabled:opacity-50 font-medium"
              >
                {deleting === user ? "Siliniyor..." : "Sil"}
              </button>
            </li>
          ))}
        </ul>
      )}

      <button
        onClick={onBack}
        className="mt-2 w-full rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 transition text-neutral-700 text-base font-medium py-3"
      >
        Geri Dön
      </button>
    </div>
  );
}
