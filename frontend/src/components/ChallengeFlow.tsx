import { useEffect, useRef, useState } from "react";
import { useCamera } from "../hooks/useCamera";
import { useFrameCapture } from "../hooks/useFrameCapture";
import { api } from "../api/client";

export type ChallengeType = "blink" | "eye_movement" | "head_movement" | "mouth_movement";

export interface ChallengeResult {
  challenge: ChallengeType;
  passed: boolean;
  score: number;
  message: string;
}

interface Challenge {
  type: ChallengeType;
  instruction: string;
  icon: string;
}

const ALL_CHALLENGES: Challenge[] = [
  { type: "blink",          instruction: "Gözlerinizi kırpın",          icon: "👁️" },
  { type: "eye_movement",   instruction: "Gözlerinizi yana çevirin",     icon: "👀" },
  { type: "head_movement",  instruction: "Başınızı sağa/sola çevirin",   icon: "↔️" },
  { type: "mouth_movement", instruction: "Ağzınızı açıp kapayın",        icon: "👄" },
];

// Kaç saniye boyunca frame toplanacak (sayım süresi)
const CAPTURE_DURATION_S = 3;
// Kaç ms'de bir frame yakalanacak → 3sn × 10fps = 30 frame (MediaPipe için yeterli)
const CAPTURE_INTERVAL_MS = 100;

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5);
}

interface Props {
  challengeCount?: number;
  onComplete: (results: ChallengeResult[], allPassed: boolean) => void;
  onCancel: () => void;
}

export function ChallengeFlow({ challengeCount = 2, onComplete, onCancel }: Props) {
  const challenges = useRef(shuffle(ALL_CHALLENGES).slice(0, challengeCount));
  const [index, setIndex]         = useState(0);
  const [phase, setPhase]         = useState<"instruction" | "capture" | "result">("instruction");
  const [countdown, setCountdown] = useState(CAPTURE_DURATION_S);
  const [stepResult, setStepResult] = useState<ChallengeResult | null>(null);
  const [allResults, setAllResults] = useState<ChallengeResult[]>([]);
  const [loading, setLoading]     = useState(false);

  const { videoRef, ready } = useCamera();
  const { captureSingleFrame } = useFrameCapture(videoRef);

  // frameBuffer: sayım boyunca toplanan frame'ler
  const frameBuffer = useRef<{ frame: string; timestamp_ms: number }[]>([]);
  const captureStart = useRef<number>(0);

  const current = challenges.current[index];

  // Sayım + eşzamanlı frame toplama
  useEffect(() => {
    if (phase !== "capture" || !ready) return;

    // Sayım başladığında buffer'ı sıfırla ve başlangıç zamanını kaydet
    frameBuffer.current = [];
    captureStart.current = Date.now();

    const countdownTimer = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          clearInterval(countdownTimer);
          return 0;
        }
        return c - 1;
      });
    }, 1000);

    // Her CAPTURE_INTERVAL_MS'de bir frame yakala
    const captureTimer = setInterval(() => {
      const f = captureSingleFrame(captureStart.current);
      if (f) frameBuffer.current.push(f);
    }, CAPTURE_INTERVAL_MS);

    // CAPTURE_DURATION_S saniye sonra toplamayı bitir ve API'ye gönder
    const doneTimer = setTimeout(() => {
      clearInterval(captureTimer);
      sendFrames();
    }, CAPTURE_DURATION_S * 1000);

    return () => {
      clearInterval(countdownTimer);
      clearInterval(captureTimer);
      clearTimeout(doneTimer);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, ready]);

  async function sendFrames() {
    setLoading(true);
    const frames = [...frameBuffer.current];
    try {
      const res = await api.checkChallenge(current.type, frames);
      const result: ChallengeResult = {
        challenge: current.type,
        passed: res.passed,
        score: res.score,
        message: res.message,
      };
      setStepResult(result);
      setAllResults((prev) => [...prev, result]);
    } catch {
      const result: ChallengeResult = {
        challenge: current.type,
        passed: false,
        score: 0,
        message: "Bağlantı hatası",
      };
      setStepResult(result);
      setAllResults((prev) => [...prev, result]);
    } finally {
      setLoading(false);
      setPhase("result");
    }
  }

  function startCapture() {
    setCountdown(CAPTURE_DURATION_S);
    setPhase("capture");
  }

  function nextChallenge() {
    if (index + 1 >= challenges.current.length) {
      const final = [...allResults];
      onComplete(final, final.every((r) => r.passed));
    } else {
      setIndex((i) => i + 1);
      setPhase("instruction");
      setCountdown(CAPTURE_DURATION_S);
      setStepResult(null);
    }
  }

  return (
    <div className="flex flex-col items-center w-full gap-4">
      {/* İlerleme */}
      <div className="flex gap-2">
        {challenges.current.map((_, i) => (
          <div
            key={i}
            className={`h-2 w-10 rounded-full transition-colors ${
              i < index ? "bg-green-500" : i === index ? "bg-indigo-500" : "bg-neutral-300"
            }`}
          />
        ))}
      </div>

      {/* Kamera */}
      <div className="relative w-full">
        <video
          ref={videoRef}
          autoPlay muted playsInline
          className="w-full rounded-2xl shadow-md border border-neutral-300"
        />

        {/* Geri sayım */}
        {phase === "capture" && countdown > 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="text-8xl font-black text-white drop-shadow-lg">{countdown}</span>
          </div>
        )}

        {/* Analiz ediliyor */}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-2xl">
            <span className="text-white text-lg font-semibold">Analiz ediliyor...</span>
          </div>
        )}
      </div>

      {/* Talimat aşaması */}
      {phase === "instruction" && (
        <div className="w-full bg-indigo-50 border border-indigo-200 rounded-2xl p-5 text-center">
          <div className="text-4xl mb-2">{current.icon}</div>
          <p className="text-lg font-semibold text-indigo-800">{current.instruction}</p>
          <p className="text-sm text-indigo-500 mt-1">
            Başlat'a basın — sayım süresince hareketi yapın
          </p>
          <button
            onClick={startCapture}
            disabled={!ready}
            className="mt-4 w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold py-3 transition"
          >
            {ready ? "Başlat" : "Kamera açılıyor..."}
          </button>
        </div>
      )}

      {/* Yakalama aşaması */}
      {phase === "capture" && (
        <div className="w-full bg-yellow-50 border border-yellow-200 rounded-2xl p-4 text-center">
          <p className="text-yellow-800 font-semibold text-lg">{current.instruction}</p>
          <p className="text-sm text-yellow-600 mt-1">
            Sayım süresince hareketi yapın!
          </p>
        </div>
      )}

      {/* Sonuç aşaması */}
      {phase === "result" && stepResult && (
        <div className={`w-full rounded-2xl p-4 text-center border ${
          stepResult.passed ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
        }`}>
          <div className="text-3xl mb-1">{stepResult.passed ? "✅" : "❌"}</div>
          <p className={`font-semibold ${stepResult.passed ? "text-green-700" : "text-red-600"}`}>
            {stepResult.message}
          </p>
          {!stepResult.passed && (
            <p className="text-xs text-neutral-400 mt-1">
              Tekrar denemek için ileri'ye basın
            </p>
          )}
          <button
            onClick={nextChallenge}
            className="mt-3 w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 transition"
          >
            {index + 1 >= challenges.current.length ? "Giriş Yap" : "Sonraki →"}
          </button>
        </div>
      )}

      <button onClick={onCancel} className="text-sm text-neutral-400 hover:text-neutral-600">
        İptal
      </button>
    </div>
  );
}
