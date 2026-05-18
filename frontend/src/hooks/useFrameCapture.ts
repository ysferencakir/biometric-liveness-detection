import type { RefObject } from "react";

export function useFrameCapture(videoRef: RefObject<HTMLVideoElement | null>) {
  function _canvas() {
    const video = videoRef.current;
    if (!video) return null;
    const c = document.createElement("canvas");
    c.width  = video.videoWidth  || 640;
    c.height = video.videoHeight || 480;
    return { canvas: c, ctx: c.getContext("2d")!, video };
  }

  /** Tek frame yak — zamanlı toplama için kullanılır */
  function captureSingleFrame(startTime: number): { frame: string; timestamp_ms: number } | null {
    const r = _canvas();
    if (!r) return null;
    r.ctx.drawImage(r.video, 0, 0);
    return {
      frame: r.canvas.toDataURL("image/jpeg", 0.7).split(",")[1],
      timestamp_ms: Date.now() - startTime,
    };
  }

  /** Eski senkron yakalama — yüz tanıma (hareketsiz çekim) için */
  function captureFrames(count = 20): string[] {
    const r = _canvas();
    if (!r) return [];
    const frames: string[] = [];
    for (let i = 0; i < count; i++) {
      r.ctx.drawImage(r.video, 0, 0);
      frames.push(r.canvas.toDataURL("image/jpeg", 0.7).split(",")[1]);
    }
    return frames;
  }

  /** Eski uyumluluk için — artık kullanılmıyor ama RegisterPage vb. için korunuyor */
  function captureFramesWithTimestamp(
    count = 30
  ): { frame: string; timestamp_ms: number }[] {
    const r = _canvas();
    if (!r) return [];
    const start = Date.now();
    const frames = [];
    for (let i = 0; i < count; i++) {
      r.ctx.drawImage(r.video, 0, 0);
      frames.push({
        frame: r.canvas.toDataURL("image/jpeg", 0.7).split(",")[1],
        timestamp_ms: Date.now() - start,
      });
    }
    return frames;
  }

  return { captureFrames, captureFramesWithTimestamp, captureSingleFrame };
}
