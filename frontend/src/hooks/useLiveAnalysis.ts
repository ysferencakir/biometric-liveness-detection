import { useEffect, useRef, useState, useCallback } from "react";
import type { RefObject } from "react";
import { api } from "../api/client";

export type DiagnoseResult = Awaited<ReturnType<typeof api.diagnose>>;

const INTERVAL_MS = 200; // 5 fps analiz

export function useLiveAnalysis(
  videoRef: RefObject<HTMLVideoElement | null>,
  canvasRef: RefObject<HTMLCanvasElement | null>,
  enabled: boolean
) {
  const [data, setData] = useState<DiagnoseResult | null>(null);
  const [fps, setFps]   = useState(0);
  const busy = useRef(false);
  const frameCount = useRef(0);
  const lastFpsTick = useRef(Date.now());

  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return null;
    const c = document.createElement("canvas");
    c.width  = video.videoWidth;
    c.height = video.videoHeight;
    c.getContext("2d")!.drawImage(video, 0, 0);
    return c.toDataURL("image/jpeg", 0.6).split(",")[1];
  }, [videoRef]);

  // Canvas'a landmark çiz
  const drawOverlay = useCallback((result: DiagnoseResult) => {
    const canvas = canvasRef.current;
    const video  = videoRef.current;
    if (!canvas || !video) return;

    // Canvas boyutunu video gösterim boyutuna eşitle
    canvas.width  = video.offsetWidth;
    canvas.height = video.offsetHeight;

    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!result.face_detected || !result.landmarks?.length) return;

    const W = canvas.width;
    const H = canvas.height;
    const lm = result.landmarks;
    const px = (pt: [number, number]) => [pt[0] * W, pt[1] * H] as [number, number];
    const lmpx = (i: number) => [lm[i][0] * W, lm[i][1] * H] as [number, number];

    // ── Yardımcı çizim fonksiyonları ──────────────────────────────────────
    function polyline(indices: number[], color: string, width = 1) {
      if (indices.length < 2) return;
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      const [x0, y0] = lmpx(indices[0]);
      ctx.moveTo(x0, y0);
      for (let i = 1; i < indices.length; i++) {
        const [x, y] = lmpx(indices[i]);
        ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    function polylineNorm(pts: [number,number][], color: string, width = 1.5, close = false) {
      if (pts.length < 2) return;
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.moveTo(...px(pts[0]));
      pts.slice(1).forEach(p => ctx.lineTo(...px(p)));
      if (close) ctx.closePath();
      ctx.stroke();
    }

    function dot(pt: [number, number], color: string, r = 3) {
      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.arc(...px(pt), r, 0, Math.PI * 2);
      ctx.fill();
    }

    // ── Yüz konturu ───────────────────────────────────────────────────────
    const FACE_OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,
                       397,365,379,378,400,377,152,148,176,149,150,136,
                       172,58,132,93,234,127,162,21,54,103,67,109,10];
    polyline(FACE_OVAL, "rgba(150,150,200,0.5)", 1);

    // ── Kaş ───────────────────────────────────────────────────────────────
    polyline([70,63,105,66,107,55,65,52,53,46], "rgba(180,180,255,0.6)", 1);
    polyline([300,293,334,296,336,285,295,282,283,276], "rgba(180,180,255,0.6)", 1);

    // ── Burun ─────────────────────────────────────────────────────────────
    polyline([168,6,197,195,5,4,45,220,115], "rgba(180,180,180,0.5)", 1);
    polyline([193,168,417,351,419,197], "rgba(180,180,180,0.5)", 1);

    // ── Göz konturları ────────────────────────────────────────────────────
    const LEFT_EYE_OUTLINE  = [362,382,381,380,374,373,390,249,263,466,388,387,386,385,384,398,362];
    const RIGHT_EYE_OUTLINE = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246,33];
    polyline(LEFT_EYE_OUTLINE,  "rgba(100,200,255,0.85)", 1.5);
    polyline(RIGHT_EYE_OUTLINE, "rgba(100,200,255,0.85)", 1.5);

    // ── EAR ölçüm çizgileri (sol göz) ─────────────────────────────────────
    const earColor = result.ear < result.thresholds.ear ? "#ff4444" : "#44ff88";
    if (result.key_points?.left_ear?.length === 6) {
      const [p1,,p3,,p5,p6] = result.key_points.left_ear as [number,number][];
      const [,,p2,,p4] = result.key_points.left_ear as [number,number][];
      // Yatay (yüzey mesafesi)
      ctx.setLineDash([3, 3]);
      polylineNorm([p1, p3 as [number,number]], earColor, 1);
      // Dikey çizgiler
      polylineNorm([p6, p2], earColor, 1.5);
      polylineNorm([p5, p4], earColor, 1.5);
      ctx.setLineDash([]);
    }

    // ── EAR ölçüm çizgileri (sağ göz) ────────────────────────────────────
    if (result.key_points?.right_ear?.length === 6) {
      const [p1,,p3,,p5,p6] = result.key_points.right_ear as [number,number][];
      const [,,p2,,p4] = result.key_points.right_ear as [number,number][];
      ctx.setLineDash([3, 3]);
      polylineNorm([p1, p3 as [number,number]], earColor, 1);
      polylineNorm([p6, p2], earColor, 1.5);
      polylineNorm([p5, p4], earColor, 1.5);
      ctx.setLineDash([]);
    }

    // ── Ağız konturu ──────────────────────────────────────────────────────
    if (result.key_points?.mouth?.length) {
      const mouthColor = "rgba(255,160,80,0.85)";
      const mouth = result.key_points.mouth as [number,number][];
      polylineNorm([...mouth, mouth[0]], mouthColor, 1.5, false);
    }

    // ── İris noktaları ────────────────────────────────────────────────────
    if (result.iris?.left)  dot(result.iris.left  as [number,number], "#00eeff", 4);
    if (result.iris?.right) dot(result.iris.right as [number,number], "#00eeff", 4);

    // ── EAR / MAR metin overlay ───────────────────────────────────────────
    ctx.font = `bold ${Math.max(11, W * 0.022)}px monospace`;
    ctx.textAlign = "left";

    function label(text: string, x: number, y: number, ok: boolean) {
      ctx.fillStyle = "rgba(0,0,0,0.55)";
      ctx.fillRect(x - 2, y - 14, ctx.measureText(text).width + 6, 18);
      ctx.fillStyle = ok ? "#44ff88" : "#ff4444";
      ctx.fillText(text, x, y);
    }

    const eyeY = result.iris?.left_center ? result.iris.left_center[1] * H - 18 : H * 0.2;
    label(`EAR ${result.ear.toFixed(3)}`, W * 0.02, eyeY, result.ear >= result.thresholds.ear);

    const mouthY = result.key_points?.mouth?.[0]
      ? (result.key_points.mouth[0] as [number,number])[1] * H - 10
      : H * 0.75;
    label(`MAR ${result.mar.toFixed(3)}`, W * 0.02, mouthY, result.mar >= result.thresholds.mar);

    // ── Kafa açısı ok göstergesi ──────────────────────────────────────────
    const cx = W * 0.93, cy = H * 0.08, r = Math.min(W, H) * 0.055;
    ctx.beginPath();
    ctx.strokeStyle = "rgba(200,200,255,0.4)";
    ctx.lineWidth = 1;
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    const yaw = result.head_yaw;
    ctx.beginPath();
    ctx.strokeStyle = "#aaddff";
    ctx.lineWidth = 2;
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(yaw) * r * 0.9, cy + Math.sin(yaw) * r * 0.9);
    ctx.stroke();

    ctx.fillStyle = "rgba(150,200,255,0.8)";
    ctx.font = `${Math.max(9, W * 0.016)}px monospace`;
    ctx.textAlign = "center";
    ctx.fillText(`${(yaw * 180 / Math.PI).toFixed(1)}°`, cx, cy + r + 12);
  }, [canvasRef, videoRef]);

  useEffect(() => {
    if (!enabled) {
      setData(null);
      return;
    }

    const interval = setInterval(async () => {
      if (busy.current) return;
      const frame = captureFrame();
      if (!frame) return;
      busy.current = true;
      try {
        const result = await api.diagnose(frame);
        setData(result);
        drawOverlay(result);

        // FPS hesabı
        frameCount.current++;
        const now = Date.now();
        if (now - lastFpsTick.current >= 1000) {
          setFps(frameCount.current);
          frameCount.current = 0;
          lastFpsTick.current = now;
        }
      } catch {
        // sessiz hata — ağ yoksa overlay temizle
      } finally {
        busy.current = false;
      }
    }, INTERVAL_MS);

    return () => clearInterval(interval);
  }, [enabled, captureFrame, drawOverlay]);

  return { data, fps };
}
