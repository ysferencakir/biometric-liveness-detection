import { useState } from "react";
import logo from "./assets/emu-logo.png";

export default function FaceAppLoginPage() {
  const [step, setStep] = useState<"home" | "student">("home");
  const [studentId, setStudentId] = useState("");

  return (
    <div className="min-h-screen bg-linear-to-b from-blue-700 to-blue-900 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-neutral-100 rounded-3xl shadow-2xl flex items-center justify-center min-h-150">
        <div className="flex flex-col items-center justify-center px-10 py-12 relative w-full">
          
          {/* EMU Logo */}
          <div className="mb-10 flex items-center justify-center">
            <img
            src={logo}
            alt="EMU Logo"
            className="w-60 h-60 object-contain"
            />
          </div>

          {step === "home" ? (
            <button
              onClick={() => setStep("student")}
              className="w-full max-w-md rounded-[28px] bg-indigo-600 hover:bg-indigo-700 transition text-white text-2xl font-semibold py-6 shadow-lg"
            >
              FaceApp ile Giriş
            </button>
          ) : (
            <div className="w-full max-w-md">
              <h2 className="text-2xl font-semibold text-neutral-800 text-center mb-6">
                Öğrenci Numaranızı Giriniz
              </h2>

              <div className="bg-white rounded-3xl shadow-md p-6 border border-neutral-200">
                <label className="block text-sm font-medium text-neutral-600 mb-2">
                  Öğrenci Numarası
                </label>
                <input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  placeholder="Örn: 20231234"
                  className="w-full rounded-xl border border-neutral-300 px-4 py-4 text-lg outline-none focus:ring-2 focus:ring-indigo-500"
                />

                <button className="mt-5 w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 transition text-white text-lg font-semibold py-4">
                  Devam Et
                </button>

                <button
                  onClick={() => setStep("home")}
                  className="mt-3 w-full rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 transition text-neutral-700 text-base font-medium py-3"
                >
                  Geri Dön
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
