import type { RefObject } from "react";

export function useFrameCapture(videoRef: RefObject<HTMLVideoElement | null>) {
  function captureFrames(count = 20): string[] {
    const video = videoRef.current;
    if (!video) return [];
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d")!;
    const frames: string[] = [];
    for (let i = 0; i < count; i++) {
      ctx.drawImage(video, 0, 0);
      frames.push(canvas.toDataURL("image/jpeg", 0.7).split(",")[1]);
    }
    return frames;
  }

  function captureFramesWithTimestamp(
    count = 30
  ): { frame: string; timestamp_ms: number }[] {
    const video = videoRef.current;
    if (!video) return [];
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d")!;
    const start = Date.now();
    const frames = [];
    for (let i = 0; i < count; i++) {
      ctx.drawImage(video, 0, 0);
      frames.push({
        frame: canvas.toDataURL("image/jpeg", 0.7).split(",")[1],
        timestamp_ms: Date.now() - start,
      });
    }
    return frames;
  }

  return { captureFrames, captureFramesWithTimestamp };
}
