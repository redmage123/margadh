import './LoadingSkeleton.css';

interface SkeletonProps {
  width?: string;
  height?: string;
  borderRadius?: string;
  className?: string;
}

export const Skeleton = ({
  width = '100%',
  height = '20px',
  borderRadius = '4px',
  className = ''
}: SkeletonProps) => {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ width, height, borderRadius }}
    />
  );
};

export const CardSkeleton = () => {
  return (
    <div className="card skeleton-card">
      <div className="skeleton-header">
        <Skeleton width="40%" height="24px" />
        <Skeleton width="80px" height="24px" borderRadius="12px" />
      </div>
      <Skeleton width="100%" height="16px" />
      <Skeleton width="90%" height="16px" />
      <Skeleton width="70%" height="16px" />
      <div className="skeleton-footer">
        <Skeleton width="100px" height="32px" borderRadius="8px" />
        <Skeleton width="100px" height="32px" borderRadius="8px" />
      </div>
    </div>
  );
};

export const MetricCardSkeleton = () => {
  return (
    <div className="card skeleton-metric-card">
      <div className="skeleton-metric-icon">
        <Skeleton width="56px" height="56px" borderRadius="12px" />
      </div>
      <div className="skeleton-metric-content">
        <Skeleton width="80px" height="36px" />
        <Skeleton width="120px" height="16px" />
      </div>
    </div>
  );
};

export const TableSkeleton = ({ rows = 5 }: { rows?: number }) => {
  return (
    <div className="skeleton-table">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="skeleton-table-row">
          <Skeleton width="100%" height="60px" borderRadius="8px" />
        </div>
      ))}
    </div>
  );
};

export const ContentGridSkeleton = ({ items = 6 }: { items?: number }) => {
  return (
    <div className="content-grid">
      {Array.from({ length: items }).map((_, index) => (
        <CardSkeleton key={index} />
      ))}
    </div>
  );
};

export const DashboardSkeleton = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <Skeleton width="200px" height="32px" />
        <Skeleton width="150px" height="44px" borderRadius="8px" />
      </div>

      <div className="metrics-grid">
        {Array.from({ length: 4 }).map((_, index) => (
          <MetricCardSkeleton key={index} />
        ))}
      </div>

      <div className="charts-grid">
        <div className="card">
          <Skeleton width="150px" height="24px" />
          <Skeleton width="100%" height="300px" borderRadius="8px" />
        </div>
        <div className="card">
          <Skeleton width="150px" height="24px" />
          <Skeleton width="100%" height="300px" borderRadius="8px" />
        </div>
      </div>
    </div>
  );
};
