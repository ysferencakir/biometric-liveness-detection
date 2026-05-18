import { useState } from "react";
import { ChallengeFlow, type ChallengeResult } from "../components/ChallengeFlow";
import { CameraView } from "../components/CameraView";
import { api, type AuthenticateResponse } from "../api/client";

type Step = "id" | "challenges" | "recognition" | "result";

interface Props {
  onBack: () => void;
}

const MODULE_LABELS: Record<string, string> = {
  blink_detection: "Göz Kırpma",
  eye_movement:    "Göz Hareketi",
  head_movement:   "Kafa Hareketi",
  mouth_movement:  "Ağız Hareketi",
  hand_number:     "El Hareketi",
};

export function LoginPage({ onBack }: Props) {
  const [step, setStep] = useState<Step>("id");
  const [studentId, setStudentId] = useState("");
  const [challengeResults, setChallengeResults] = useState<ChallengeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuthenticateResponse | null>(null);

  function handleChallengesDone(results: ChallengeResult[], allPassed: boolean) {
    setChallengeResults(results);
    if (!allPassed) {
      // Challenge başarısız → direkt sonuç göster
      setResult({
        granted: false,
        reason: "Canlılık testi başarısız",
        liveness: results.map((r) => ({
          module_name: r.challenge,
          passed: r.passed,
          score: r.score,
          details: {},
        })),
      });
      setStep("result");
    } else {
      setStep("recognition");
    }
  }

  async function handleRecognition(frames: string[]) {
    setLoading(true);
    try {
      // Challenge adımı zaten geçildi → liveness_verified=true, sadece yüz tanıma yapılır
      const res = await api.authenticate(studentId.trim() || null, frames, true);
      setResult(res);
    } catch (e: unknown) {
      setResult({
        granted: false,
        reason: e instanceof Error ? e.message : "Bağlantı hatası",
        liveness: [],
      });
    } finally {
      setLoading(false);
      setStep("result");
    }
  }

  function reset() {
    setStep("id");
    setStudentId("");
    setChallengeResults([]);
    setResult(null);
  }

  return (
    <div className="flex flex-col items-center w-full max-w-md gap-4">
      <h2 className="text-2xl font-semibold text-neutral-800">Giriş Yap</h2>

      {/* ADIM 1: Öğrenci numarası */}
      {step === "id" && (
        <div className="bg-white rounded-3xl shadow-md p-6 border border-neutral-200 w-full">
          <label className="block text-sm font-medium text-neutral-600 mb-2">
            Öğrenci Numarası
          </label>
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && studentId.trim() && setStep("challenges")}
            placeholder="Örn: 20231234"
            className="w-full rounded-xl border border-neutral-300 px-4 py-4 text-lg outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={() => setStep("challenges")}
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

      {/* ADIM 2: Rastgele sırayla canlılık challenge'ları */}
      {step === "challenges" && (
        <ChallengeFlow
          challengeCount={2}
          onComplete={handleChallengesDone}
          onCancel={() => setStep("id")}
        />
      )}

      {/* ADIM 3: Yüz tanıma */}
      {step === "recognition" && (
        <>
          <div className="w-full bg-green-50 border border-green-200 rounded-2xl p-3 text-center">
            <p className="text-green-700 font-medium text-sm">
              ✓ Canlılık testleri geçildi — yüzünüzü kameraya gösterin
            </p>
          </div>
          <CameraView
            onCapture={handleRecognition}
            buttonLabel="Giriş Yap"
            disabled={loading}
            frameCount={25}
          />
          <button
            onClick={() => setStep("challenges")}
            className="w-full rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 transition text-neutral-700 text-base font-medium py-3"
          >
            Geri Dön
          </button>
        </>
      )}

      {/* ADIM 4: Sonuç */}
      {step === "result" && result && (
        <div className="flex flex-col items-center gap-4 w-full">
          <div className={`w-24 h-24 rounded-full flex items-center justify-center text-5xl shadow-md ${result.granted ? "bg-green-100" : "bg-red-100"}`}>
            {result.granted ? "✓" : "✗"}
          </div>
          <p className={`text-xl font-semibold text-center ${result.granted ? "text-green-700" : "text-red-600"}`}>
            {result.reason}
          </p>
          {result.recognition_score !== undefined && (
            <p className="text-sm text-neutral-500">
              Tanıma skoru: {(result.recognition_score * 100).toFixed(0)}%
            </p>
          )}

          {/* Challenge sonuçları */}
          {challengeResults.length > 0 && (
            <div className="w-full bg-white rounded-2xl border border-neutral-200 p-4 shadow-sm">
              <p className="text-xs font-semibold text-neutral-400 uppercase mb-3">Canlılık Testleri</p>
              <div className="flex flex-col gap-2">
                {challengeResults.map((r) => (
                  <div key={r.challenge} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-700">
                      {MODULE_LABELS[r.challenge] ?? r.challenge}
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-neutral-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${r.passed ? "bg-green-500" : "bg-red-400"}`}
                          style={{ width: `${Math.round(r.score * 100)}%` }}
                        />
                      </div>
                      <span className={`text-xs font-bold ${r.passed ? "text-green-600" : "text-red-500"}`}>
                        {r.passed ? "✓" : "✗"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={reset}
            className="w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 transition text-white text-lg font-semibold py-4"
          >
            Ana Sayfaya Dön
          </button>
        </div>
      )}
    </div>
  );
}
