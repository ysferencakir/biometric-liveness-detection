import { useState } from "react";
import { CameraView } from "../components/CameraView";
import { ResultCard } from "../components/ResultCard";
import { api } from "../api/client";

type Step = "id" | "camera" | "result";

interface Props {
  onBack: () => void;
}

export function LoginPage({ onBack }: Props) {
  const [step, setStep] = useState<Step>("id");
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  async function handleCapture(frames: string[]) {
    setLoading(true);
    try {
      const res = await api.login(frames);
      setResult({ success: res.success, message: res.message });
    } catch (e: unknown) {
      setResult({ success: false, message: e instanceof Error ? e.message : "Bağlantı hatası" });
    } finally {
      setLoading(false);
      setStep("result");
    }
  }

  return (
    <div className="flex flex-col items-center w-full max-w-md gap-4">
      <h2 className="text-2xl font-semibold text-neutral-800">Giriş Yap</h2>

      {step === "id" && (
        <div className="bg-white rounded-3xl shadow-md p-6 border border-neutral-200 w-full">
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
          <button
            onClick={() => setStep("camera")}
            disabled={!studentId.trim()}
            className="mt-5 w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition text-white text-lg font-semibold py-4"
          >
            Devam Et
          </button>
          <button
            onClick={onBack}
            className="mt-3 w-full rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 transition text-neutral-700 text-base font-medium py-3"
          >
            Geri Dön
          </button>
        </div>
      )}

      {step === "camera" && (
        <>
          <p className="text-neutral-500 text-sm">Kameraya bakın ve giriş yapın</p>
          <CameraView
            onCapture={handleCapture}
            buttonLabel="Giriş Yap"
            disabled={loading}
            frameCount={20}
          />
          <button
            onClick={() => setStep("id")}
            className="w-full rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 transition text-neutral-700 text-base font-medium py-3"
          >
            Geri Dön
          </button>
        </>
      )}

      {step === "result" && result && (
        <ResultCard
          success={result.success}
          message={result.message}
          onBack={onBack}
        />
      )}
    </div>
  );
}
