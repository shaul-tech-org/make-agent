export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="px-3 py-2 text-sm bg-error/10 text-error border border-error/20 rounded-md">
      {message}
    </div>
  );
}
