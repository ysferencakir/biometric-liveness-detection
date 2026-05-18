import { useEffect, useRef, useState, useCallback } from "react";

export function useCamera() {
  const videoRef  = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Stream'i video element'e bağla — ref henüz yoksa tekrar dene
  const attachStream = useCallback((stream: MediaStream) => {
    streamRef.current = stream;
    const attach = () => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => setReady(true);
      } else {
        // Ref henüz mount olmadı, bir sonraki frame'de tekrar dene
        requestAnimationFrame(attach);
      }
    };
    attach();
  }, []);

  useEffect(() => {
    // Güvenli bağlam / tarayıcı desteği kontrolü
    if (!navigator?.mediaDevices?.getUserMedia) {
      setError("Bu tarayıcı kamera erişimini desteklemiyor ya da sayfa güvenli bir bağlantı (https / localhost) üzerinde değil.");
      return;
    }

    navigator.mediaDevices
      .getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } })
      .then(attachStream)
      .catch((err: DOMException) => {
        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
          setError("Kamera izni reddedildi. Tarayıcı adres çubuğundaki kamera simgesine tıklayarak izin verin.");
        } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
          setError("Kamera bulunamadı. Bir kameranın bağlı olduğundan emin olun.");
        } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
          setError("Kamera başka bir uygulama tarafından kullanılıyor. Diğer sekme/uygulamaları kapatıp tekrar deneyin.");
        } else {
          setError(`Kamera hatası: ${err.name} — ${err.message}`);
        }
      });

    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
      setReady(false);
    };
  }, [attachStream]);

  return { videoRef, ready, error };
}
