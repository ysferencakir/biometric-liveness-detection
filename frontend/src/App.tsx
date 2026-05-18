import { useState } from "react";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { UsersPage } from "./pages/UsersPage";
import { DiagnosticPage } from "./pages/DiagnosticPage";

type Page = "home" | "login" | "register" | "users" | "diagnostic";

export default function App() {
  const [page, setPage] = useState<Page>("home");

  return (
    <div className="min-h-screen bg-linear-to-b from-blue-700 to-blue-900 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-neutral-100 rounded-3xl shadow-2xl flex items-center justify-center min-h-[600px]">
        <div className="flex flex-col items-center justify-center px-10 py-12 w-full">
          {page === "home"       && <HomePage onNavigate={setPage} />}
          {page === "login"      && <LoginPage onBack={() => setPage("home")} />}
          {page === "register"   && <RegisterPage onBack={() => setPage("home")} />}
          {page === "users"      && <UsersPage onBack={() => setPage("home")} />}
          {page === "diagnostic" && <DiagnosticPage onBack={() => setPage("home")} />}
        </div>
      </div>
    </div>
  );
}
