import { useState } from "react";
import { CameraView } from "../components/CameraView";
import { ResultCard } from "../components/ResultCard";
import { api } from "../api/client";

type Step = "name" | "camera" | "result";

interface Props {
  onBack: () => void;
}

export function RegisterPage({ onBack }: Props) {
  const [step, setStep] = useState<Step>("name");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  async function handleCapture(frames: string[]) {
    setLoading(true);
    try {
      const res = await api.register(name.trim(), frames);
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
      <h2 className="text-2xl font-semibold text-neutral-800">Yüz Kaydı</h2>

      {step === "name" && (
        <div className="bg-white rounded-3xl shadow-md p-6 border border-neutral-200 w-full">
          <label className="block text-sm font-medium text-neutral-600 mb-2">
            Ad Soyad veya Öğrenci Numarası
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Örn: Ahmet Yılmaz"
            className="w-full rounded-xl border border-neutral-300 px-4 py-4 text-lg outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={() => setStep("camera")}
            disabled={!name.trim()}
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
          <p className="text-neutral-500 text-sm">
            Kameraya bakın — yüzünüz kaydedilecek
          </p>
          <CameraView
            onCapture={handleCapture}
            buttonLabel="Kayıt Ol"
            disabled={loading}
            frameCount={25}
          />
          <button
            onClick={() => setStep("name")}
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
