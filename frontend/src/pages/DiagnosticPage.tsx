import { useRef, useState } from "react";
import { useCamera } from "../hooks/useCamera";
import { useFrameCapture } from "../hooks/useFrameCapture";
import { useLiveAnalysis } from "../hooks/useLiveAnalysis";
import { api } from "../api/client";
import type { ChallengeType } from "../components/ChallengeFlow";

const CAPTURE_DURATION_S = 3;
const CAPTURE_INTERVAL_MS = 100;

interface ChallengeCardResult {
  passed: boolean;
  score: number;
  message: string;
}

interface Props {
  onBack: () => void;
}

const CHALLENGES: { type: ChallengeType; label: string; icon: string; hint: string }[] = [
  { type: "blink",          label: "Göz Kırpma",    icon: "👁️", hint: "Gözlerinizi yavaşça kırpın" },
  { type: "eye_movement",   label: "Göz Hareketi",  icon: "👀", hint: "Gözlerinizi sağa/sola çevirin" },
  { type: "head_movement",  label: "Kafa Hareketi", icon: "↔️", hint: "Başınızı sağa/sola çevirin" },
  { type: "mouth_movement", label: "Ağız Hareketi", icon: "👄", hint: "Ağzınızı açıp kapayın" },
];

function GaugeBar({ value, max, threshold, label, unit = "" }: {
  value: number; max: number; threshold?: number; label: string; unit?: string;
}) {
  const pct = Math.min(value / max, 1) * 100;
  const tPct = threshold ? Math.min(threshold / max, 1) * 100 : null;
  const ok = threshold === undefined || value >= threshold;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs font-mono">
        <span className="text-neutral-400">{label}</span>
        <span className={ok ? "text-green-400" : "text-red-400"}>
          {value.toFixed(3)}{unit}
        </span>
      </div>
      <div className="relative h-3 bg-neutral-700 rounded-full overflow-visible">
        <div
          className={`h-full rounded-full transition-all duration-100 ${ok ? "bg-green-500" : "bg-red-500"}`}
          style={{ width: `${pct}%` }}
        />
        {tPct !== null && (
          <div
            className="absolute top-0 h-full w-0.5 bg-yellow-400 opacity-70"
            style={{ left: `${tPct}%` }}
          />
        )}
      </div>
    </div>
  );
}

function AngleMeter({ value, label }: { value: number; label: string }) {
  const deg = (value * 180 / Math.PI).toFixed(1);
  const norm = Math.max(-1, Math.min(1, value / 0.5));
  const x = 50 + norm * 45;
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs font-mono">
        <span className="text-neutral-400">{label}</span>
        <span className="text-blue-300">{deg}°</span>
      </div>
      <div className="relative h-3 bg-neutral-700 rounded-full">
        <div className="absolute top-0 bottom-0 left-1/2 w-px bg-neutral-500" />
        <div
          className="absolute top-0.5 bottom-0.5 w-2 bg-blue-400 rounded-full transition-all duration-100"
          style={{ left: `calc(${x}% - 4px)` }}
        />
      </div>
    </div>
  );
}

export function DiagnosticPage({ onBack }: Props) {
  const videoRef  = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { ready, error } = useCamera();
  const { captureSingleFrame } = useFrameCapture(videoRef);

  const [analysisOn, setAnalysisOn] = useState(true);
  const { data, fps } = useLiveAnalysis(videoRef, canvasRef, analysisOn && ready);

  // Challenge test state: bir map (type → durum)
  const [cardStates, setCardStates] = useState<
    Record<ChallengeType, { running: boolean; countdown: number; result: ChallengeCardResult | null }>
  >({
    blink:          { running: false, countdown: 0, result: null },
    eye_movement:   { running: false, countdown: 0, result: null },
    head_movement:  { running: false, countdown: 0, result: null },
    mouth_movement: { running: false, countdown: 0, result: null },
  });

  function runChallenge(type: ChallengeType) {
    setCardStates(s => ({ ...s, [type]: { running: true, countdown: CAPTURE_DURATION_S, result: null } }));

    const buf: { frame: string; timestamp_ms: number }[] = [];
    const start = Date.now();

    // Countdown timer
    let cd = CAPTURE_DURATION_S;
    const cdTimer = setInterval(() => {
      cd--;
      setCardStates(s => ({ ...s, [type]: { ...s[type], countdown: cd } }));
    }, 1000);

    // Frame capture
    const capTimer = setInterval(() => {
      const f = captureSingleFrame(start);
      if (f) buf.push(f);
    }, CAPTURE_INTERVAL_MS);

    setTimeout(async () => {
      clearInterval(cdTimer);
      clearInterval(capTimer);
      try {
        const res = await api.checkChallenge(type, buf);
        setCardStates(s => ({
          ...s,
          [type]: { running: false, countdown: 0, result: { passed: res.passed, score: res.score, message: res.message } },
        }));
      } catch {
        setCardStates(s => ({
          ...s,
          [type]: { running: false, countdown: 0, result: { passed: false, score: 0, message: "Bağlantı hatası" } },
        }));
      }
    }, CAPTURE_DURATION_S * 1000);
  }

  const thr = data?.thresholds;

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Başlık */}
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="text-sm text-neutral-400 hover:text-neutral-600 flex items-center gap-1">
          ← Geri
        </button>
        <h2 className="text-lg font-bold text-neutral-800">🔬 Test Laboratuvarı</h2>
        <button
          onClick={() => setAnalysisOn(v => !v)}
          className={`text-xs font-semibold px-3 py-1 rounded-full border transition ${
            analysisOn
              ? "bg-green-100 border-green-300 text-green-700"
              : "bg-neutral-100 border-neutral-300 text-neutral-500"
          }`}
        >
          {analysisOn ? "● CANLI" : "○ DURDUR"}
        </button>
      </div>

      {/* Kamera erişim hatası */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-center space-y-2">
          <p className="text-red-700 font-semibold text-sm">📷 Kamera Erişilemiyor</p>
          <p className="text-red-600 text-xs leading-relaxed">{error}</p>
          <div className="bg-red-100 rounded-xl p-3 text-left text-xs text-red-800 space-y-1">
            <p className="font-semibold">Nasıl çözülür?</p>
            <p>① Tarayıcı adres çubuğundaki 🔒 veya 📷 simgesine tıklayın</p>
            <p>② "Kamera" iznini <b>İzin Ver</b> olarak değiştirin</p>
            <p>③ Sayfayı yenileyin</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="text-xs bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl font-medium transition"
          >
            Sayfayı Yenile
          </button>
        </div>
      )}

      {/* Kamera + Canvas overlay */}
      {!error && (
      <div className="relative rounded-2xl overflow-hidden bg-black shadow-md border border-neutral-200">
        <video
          ref={videoRef}
          autoPlay muted playsInline
          className="w-full block"
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />

        {/* FPS + yüz durum badge */}
        <div className="absolute top-2 left-2 flex gap-2 z-10">
          <span className="bg-black/60 text-white text-xs px-2 py-0.5 rounded-full font-mono">
            {fps} fps
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
            data?.face_detected
              ? "bg-green-600/80 text-white"
              : "bg-red-600/80 text-white"
          }`}>
            {data?.face_detected ? "✓ Yüz" : "✗ Yüz yok"}
          </span>
        </div>

        {/* Analiz durduruldu banner */}
        {!analysisOn && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center z-10">
            <span className="text-white font-bold text-lg">Analiz durduruldu</span>
          </div>
        )}
      </div>
      )}

      {/* Metrikler */}
      <div className="bg-neutral-900 rounded-2xl p-4 flex flex-col gap-3">
        <p className="text-xs text-neutral-500 font-semibold uppercase tracking-wider">Canlı Metrikler</p>

        <GaugeBar
          label="EAR (Göz açıklığı)"
          value={data?.ear ?? 0}
          max={0.45}
          threshold={thr?.ear}
          unit=""
        />
        <GaugeBar
          label="MAR (Ağız açıklığı)"
          value={data?.mar ?? 0}
          max={0.3}
          threshold={thr?.mar}
        />
        <AngleMeter
          label="Kafa Yaw (yatay dönüş)"
          value={data?.head_yaw ?? 0}
        />
        <AngleMeter
          label="Kafa Pitch (dikey eğim)"
          value={data?.head_pitch ?? 0}
        />

        <div className="flex justify-between text-xs font-mono mt-1">
          <span className="text-neutral-500">Göz arası mesafe</span>
          <span className="text-neutral-300">{data?.eye_dist?.toFixed(0) ?? "—"} px</span>
        </div>

        {/* Eşik referansları */}
        <div className="flex gap-3 pt-1 border-t border-neutral-700 mt-1">
          <span className="text-xs text-neutral-500">Eşikler →</span>
          <span className="text-xs text-yellow-400">EAR: {thr?.ear ?? "—"}</span>
          <span className="text-xs text-yellow-400">MAR Δ: {thr?.mar ?? "—"}</span>
          <span className="text-xs text-yellow-400">Kafa: {thr?.head ? (thr.head * 180 / Math.PI).toFixed(1) + "°" : "—"}</span>
        </div>
      </div>

      {/* Challenge Test Kartları */}
      <div className="grid grid-cols-2 gap-3">
        {CHALLENGES.map(({ type, label, icon, hint }) => {
          const state = cardStates[type];
          const res   = state.result;
          return (
            <div
              key={type}
              className={`rounded-2xl border p-4 flex flex-col gap-2 transition ${
                res
                  ? res.passed
                    ? "bg-green-50 border-green-200"
                    : "bg-red-50 border-red-200"
                  : "bg-white border-neutral-200"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl">{icon}</span>
                <div>
                  <p className="text-sm font-semibold text-neutral-800">{label}</p>
                  <p className="text-xs text-neutral-400">{hint}</p>
                </div>
              </div>

              {/* Skor çubuğu */}
              {res && (
                <div className="flex flex-col gap-0.5">
                  <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${res.passed ? "bg-green-500" : "bg-red-400"}`}
                      style={{ width: `${Math.round(res.score * 100)}%` }}
                    />
                  </div>
                  <p className={`text-xs font-medium ${res.passed ? "text-green-700" : "text-red-600"}`}>
                    {res.passed ? "✓" : "✗"} {res.message} ({Math.round(res.score * 100)}%)
                  </p>
                </div>
              )}

              {/* Sayım */}
              {state.running && (
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                    {state.countdown}
                  </div>
                  <span className="text-xs text-indigo-600 font-medium">Hareketi yapın...</span>
                </div>
              )}

              <button
                onClick={() => runChallenge(type)}
                disabled={state.running}
                className="mt-auto rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-xs font-semibold py-2 transition"
              >
                {state.running ? "Test ediliyor..." : res ? "Tekrar Test Et" : "Test Et"}
              </button>
            </div>
          );
        })}
      </div>

      {/* Kamera hazır değilse uyarı */}
      {!ready && !error && (
        <p className="text-center text-sm text-neutral-400">Kamera açılıyor...</p>
      )}
    </div>
  );
}
