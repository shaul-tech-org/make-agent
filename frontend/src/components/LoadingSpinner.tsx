export default function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClass = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3",
  }[size];

  return (
    <span
      className={`inline-block ${sizeClass} border-text-muted border-t-accent rounded-full animate-spin`}
      role="status"
      aria-label="Loading"
    />
  );
}
