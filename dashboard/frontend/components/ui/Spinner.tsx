export function Spinner({ className }: { className?: string }) {
  return (
    <div className={`flex items-center justify-center py-10 ${className ?? ""}`}>
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-baseline border-t-series-1" />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-1 py-10 text-center">
      <p className="text-sm font-medium text-status-critical">Failed to load</p>
      <p className="max-w-sm text-xs text-text-muted">{message}</p>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-1 py-10 text-center">
      <p className="text-sm text-text-secondary">{message}</p>
    </div>
  );
}
