export default function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-sm text-text-muted py-8 text-center">
      {message}
    </div>
  );
}
