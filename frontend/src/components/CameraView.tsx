import { useCamera } from "../hooks/useCamera";
import { useFrameCapture } from "../hooks/useFrameCapture";

interface Props {
  onCapture: (frames: string[]) => void;
  buttonLabel?: string;
  disabled?: boolean;
  frameCount?: number;
}

export function CameraView({
  onCapture,
  buttonLabel = "Devam Et",
  disabled = false,
  frameCount = 20,
}: Props) {
  const { videoRef, ready, error } = useCamera();
  const { captureFrames } = useFrameCapture(videoRef);

  function handleCapture() {
    const frames = captureFrames(frameCount);
    onCapture(frames);
  }

  if (error) {
    return (
      <p className="text-red-500 text-center text-sm">{error}</p>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full rounded-2xl shadow-md border border-neutral-300"
      />
      <button
        onClick={handleCapture}
        disabled={!ready || disabled}
        className="w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition text-white text-lg font-semibold py-4"
      >
        {!ready ? "Kamera açılıyor..." : disabled ? "İşleniyor..." : buttonLabel}
      </button>
    </div>
  );
}
