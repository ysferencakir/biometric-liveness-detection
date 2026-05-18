import logo from "../assets/emu-logo.png";

type Page = "home" | "login" | "register" | "users" | "diagnostic";

interface Props {
  onNavigate: (page: Page) => void;
}

export function HomePage({ onNavigate }: Props) {
  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-md">
      <img src={logo} alt="EMU Logo" className="w-48 h-48 object-contain" />

      <div className="flex flex-col gap-3 w-full">
        <button
          onClick={() => onNavigate("login")}
          className="w-full rounded-2xl bg-indigo-600 hover:bg-indigo-700 transition text-white text-xl font-semibold py-5 shadow-md"
        >
          Giriş Yap
        </button>
        <button
          onClick={() => onNavigate("register")}
          className="w-full rounded-2xl bg-white hover:bg-neutral-50 border border-indigo-300 transition text-indigo-700 text-xl font-semibold py-5 shadow-sm"
        >
          Kayıt Ol
        </button>
        <button
          onClick={() => onNavigate("users")}
          className="w-full rounded-2xl bg-neutral-200 hover:bg-neutral-300 transition text-neutral-700 text-base font-medium py-4"
        >
          Kullanıcı Yönetimi
        </button>
        <button
          onClick={() => onNavigate("diagnostic")}
          className="w-full rounded-2xl bg-neutral-100 hover:bg-neutral-200 border border-dashed border-neutral-300 transition text-neutral-500 text-sm font-medium py-3 flex items-center justify-center gap-2"
        >
          🔬 Test Laboratuvarı
        </button>
      </div>
    </div>
  );
}
