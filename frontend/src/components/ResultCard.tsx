interface Props {
  success: boolean;
  message: string;
  onBack: () => void;
}

export function ResultCard({ success, message, onBack }: Props) {
  return (
    <div className="flex flex-col items-center gap-6 w-full max-w-md">
      <div
        className={`w-24 h-24 rounded-full flex items-center justify-center text-5xl shadow-md ${
          success ? "bg-green-100" : "bg-red-100"
        }`}
      >
        {success ? "✓" : "✗"}
      </div>
      <p
        className={`text-xl font-semibold text-center ${
          success ? "text-green-700" : "text-red-600"
        }`}
      >
        {message}
      </p>
      <button
        onClick={onBack}
        className="w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 transition text-white text-lg font-semibold py-4"
      >
        Ana Sayfaya Dön
      </button>
    </div>
  );
}
