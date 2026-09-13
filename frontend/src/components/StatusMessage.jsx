export function StatusMessage({ children, error, onRetry }) {
  if (error) {
    return (
      <div className="status status--error" role="alert">
        <p>{error.message || 'Something went wrong.'}</p>
        {onRetry && error.status !== 404 && (
          <button type="button" className="button" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    );
  }
  return (
    <div className="status" role="status">
      {children}
    </div>
  );
}
