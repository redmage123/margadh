import { AlertCircle, RefreshCw } from 'lucide-react';
import './ErrorState.css';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  showRetry?: boolean;
}

export const ErrorState = ({
  title = 'Something went wrong',
  message = 'We encountered an error loading this content. Please try again.',
  onRetry,
  showRetry = true,
}: ErrorStateProps) => {
  return (
    <div className="error-state">
      <div className="error-state-icon">
        <AlertCircle size={48} />
      </div>
      <h3 className="error-state-title">{title}</h3>
      <p className="error-state-message">{message}</p>
      {showRetry && onRetry && (
        <button onClick={onRetry} className="btn btn-primary">
          <RefreshCw size={16} />
          Try Again
        </button>
      )}
    </div>
  );
};

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
}

export const EmptyState = ({ icon, title, message, action }: EmptyStateProps) => {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state-icon">{icon}</div>}
      <h3 className="empty-state-title">{title}</h3>
      {message && <p className="empty-state-message">{message}</p>}
      {action && (
        <button onClick={action.onClick} className="btn btn-primary">
          {action.icon}
          {action.label}
        </button>
      )}
    </div>
  );
};
