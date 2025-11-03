import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle,
  Clock,
  XCircle,
  AlertCircle,
  FileText,
  RefreshCw,
} from 'lucide-react';
import type { ApprovalRequest } from '@/types/approval';
import { getApprovalRequests, CURRENT_USER } from '@/services/approvals';
import { ApprovalWorkflow } from '@/components/ApprovalWorkflow';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import { ErrorState } from '@/components/ErrorState';
import './Approvals.css';

const Approvals = () => {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'my_approvals' | 'my_submissions'>('all');
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);

    try {
      let fetchedRequests = await getApprovalRequests();

      // Apply filters
      if (filter === 'my_approvals') {
        fetchedRequests = fetchedRequests.filter(r => {
          const currentStage = r.stages.find(s => s.id === r.current_stage_id);
          return currentStage?.assigned_to === CURRENT_USER.id && r.status === 'in_progress';
        });
      } else if (filter === 'my_submissions') {
        fetchedRequests = fetchedRequests.filter(r => r.created_by === CURRENT_USER.id);
      }

      setRequests(fetchedRequests);
    } catch (err) {
      console.error('Failed to fetch approval requests:', err);
      setError('Failed to load approval requests');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestUpdate = (updated: ApprovalRequest) => {
    setRequests(prev =>
      prev.map(r => (r.id === updated.id ? updated : r))
    );
    setSelectedRequest(updated);
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to Load Approvals"
        message={error}
        onRetry={fetchRequests}
      />
    );
  }

  return (
    <div className="approvals-page">
      <div className="approvals-header">
        <div>
          <h1>Approval Requests</h1>
          <p className="text-secondary">
            Manage content approval workflows and review pending requests
          </p>
        </div>
        <button
          onClick={fetchRequests}
          className="btn btn-secondary"
        >
          <RefreshCw size={20} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="approvals-filters">
        <div className="filter-buttons">
          <button
            onClick={() => setFilter('all')}
            className={`filter-btn ${filter === 'all' ? 'filter-active' : ''}`}
          >
            <FileText size={16} />
            All Requests
            <span className="filter-count">{requests.length}</span>
          </button>

          <button
            onClick={() => setFilter('my_approvals')}
            className={`filter-btn ${filter === 'my_approvals' ? 'filter-active' : ''}`}
          >
            <Clock size={16} />
            Pending My Approval
            <span className="filter-count">
              {requests.filter(r => {
                const currentStage = r.stages.find(s => s.id === r.current_stage_id);
                return currentStage?.assigned_to === CURRENT_USER.id && r.status === 'in_progress';
              }).length}
            </span>
          </button>

          <button
            onClick={() => setFilter('my_submissions')}
            className={`filter-btn ${filter === 'my_submissions' ? 'filter-active' : ''}`}
          >
            <FileText size={16} />
            My Submissions
            <span className="filter-count">
              {requests.filter(r => r.created_by === CURRENT_USER.id).length}
            </span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="approvals-content">
        {selectedRequest ? (
          <div className="approval-detail-view">
            <button
              onClick={() => setSelectedRequest(null)}
              className="btn btn-secondary btn-sm back-btn"
            >
              ← Back to List
            </button>

            <div className="approval-detail-header">
              <div>
                <h2 className="approval-detail-title">{selectedRequest.content_title}</h2>
                <Link
                  to={`/content/${selectedRequest.content_id}/edit`}
                  className="view-content-link"
                >
                  View Content →
                </Link>
              </div>
            </div>

            <ApprovalWorkflow
              request={selectedRequest}
              onUpdate={handleRequestUpdate}
            />
          </div>
        ) : (
          <>
            {requests.length === 0 ? (
              <div className="empty-state">
                <AlertCircle size={48} />
                <h3>No approval requests</h3>
                <p>
                  {filter === 'my_approvals'
                    ? 'You have no pending approvals at this time.'
                    : filter === 'my_submissions'
                    ? 'You haven\'t submitted any content for approval yet.'
                    : 'No approval requests have been created yet.'}
                </p>
              </div>
            ) : (
              <div className="approvals-list">
                {requests.map(request => (
                  <ApprovalCard
                    key={request.id}
                    request={request}
                    onClick={() => setSelectedRequest(request)}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Approval Card Component
interface ApprovalCardProps {
  request: ApprovalRequest;
  onClick: () => void;
}

const ApprovalCard = ({ request, onClick }: ApprovalCardProps) => {
  const currentStage = request.stages.find(s => s.id === request.current_stage_id);
  const completedStages = request.stages.filter(s => s.status === 'approved').length;
  const totalStages = request.stages.length;
  const progress = (completedStages / totalStages) * 100;

  const needsMyAction = currentStage?.assigned_to === CURRENT_USER.id && request.status === 'in_progress';

  return (
    <div
      className={`approval-card ${needsMyAction ? 'approval-card-urgent' : ''}`}
      onClick={onClick}
    >
      <div className="approval-card-header">
        <h3 className="approval-card-title">{request.content_title}</h3>
        <span className={`badge badge-${getStatusColor(request.status)}`}>
          {getStatusIcon(request.status)}
          {formatStatus(request.status)}
        </span>
      </div>

      <div className="approval-card-info">
        <div className="info-item">
          <span className="info-label">Workflow:</span>
          <span className="info-value">{request.workflow_name}</span>
        </div>

        {currentStage && request.status === 'in_progress' && (
          <div className="info-item">
            <span className="info-label">Current Stage:</span>
            <span className="info-value">{currentStage.name}</span>
          </div>
        )}

        <div className="info-item">
          <span className="info-label">Created by:</span>
          <span className="info-value">{request.created_by_name}</span>
        </div>

        <div className="info-item">
          <span className="info-label">Created:</span>
          <span className="info-value">
            {new Date(request.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="approval-progress">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${progress}%`,
              backgroundColor:
                request.status === 'approved' ? 'var(--success)' :
                request.status === 'rejected' ? 'var(--error)' :
                'var(--primary)',
            }}
          />
        </div>
        <span className="progress-text">
          {completedStages} of {totalStages} stages completed
        </span>
      </div>

      {needsMyAction && (
        <div className="action-needed-badge">
          <AlertCircle size={16} />
          Action Needed
        </div>
      )}
    </div>
  );
};

// Helper functions
function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'warning',
    in_progress: 'info',
    approved: 'success',
    rejected: 'error',
    cancelled: 'secondary',
  };
  return colors[status] || 'secondary';
}

function getStatusIcon(status: string) {
  const icons: Record<string, JSX.Element> = {
    pending: <Clock size={14} />,
    in_progress: <AlertCircle size={14} />,
    approved: <CheckCircle size={14} />,
    rejected: <XCircle size={14} />,
    cancelled: <XCircle size={14} />,
  };
  return icons[status] || null;
}

function formatStatus(status: string): string {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

export default Approvals;
