import { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  MessageCircle,
  Send,
  SkipForward,
} from 'lucide-react';
import type { ApprovalRequest, ApprovalStage, ApprovalAction } from '@/types/approval';
import { getStageIcon, getStatusColor, canUserApprove } from '@/types/approval';
import { submitApprovalAction, CURRENT_USER } from '@/services/approvals';
import toast from 'react-hot-toast';
import './ApprovalWorkflow.css';

interface ApprovalWorkflowProps {
  request: ApprovalRequest;
  onUpdate: (request: ApprovalRequest) => void;
}

export const ApprovalWorkflow = ({ request, onUpdate }: ApprovalWorkflowProps) => {
  const [activeStageId, setActiveStageId] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleAction = async (stage: ApprovalStage, action: ApprovalAction) => {
    if (!comment.trim() && action !== 'skip') {
      toast.error('Please add a comment');
      return;
    }

    setSubmitting(true);
    const loadingToast = toast.loading(`Processing ${action}...`);

    try {
      const updated = await submitApprovalAction(
        request.id,
        stage.id,
        action,
        comment.trim()
      );

      onUpdate(updated);
      setComment('');
      setActiveStageId(null);

      const messages = {
        approve: 'Approved successfully',
        reject: 'Rejected successfully',
        request_changes: 'Changes requested',
        skip: 'Stage skipped',
        submit: 'Submitted',
      };

      toast.success(messages[action], { id: loadingToast });
    } catch (error) {
      console.error('Approval action failed:', error);
      toast.error('Failed to process action', { id: loadingToast });
    } finally {
      setSubmitting(false);
    }
  };

  const isStageActive = (stage: ApprovalStage) => {
    return stage.id === request.current_stage_id && request.status === 'in_progress';
  };

  const canApproveStage = (stage: ApprovalStage) => {
    return isStageActive(stage) && canUserApprove(CURRENT_USER, stage);
  };

  return (
    <div className="approval-workflow">
      <div className="approval-header">
        <div>
          <h3 className="approval-title">{request.workflow_name}</h3>
          <p className="approval-subtitle">
            Created by {request.created_by_name} on{' '}
            {new Date(request.created_at).toLocaleDateString()}
          </p>
        </div>
        <span className={`badge badge-${getRequestStatusColor(request.status)}`}>
          {formatRequestStatus(request.status)}
        </span>
      </div>

      <div className="approval-stages">
        {request.stages.map((stage, index) => {
          const isActive = isStageActive(stage);
          const canApprove = canApproveStage(stage);
          const isExpanded = activeStageId === stage.id;

          return (
            <div key={stage.id} className="stage-container">
              {/* Stage Card */}
              <div className={`stage-card ${isActive ? 'stage-active' : ''} ${stage.status === 'approved' ? 'stage-completed' : ''}`}>
                <div className="stage-number">{index + 1}</div>

                <div className="stage-content">
                  <div className="stage-header-row">
                    <div className="stage-info">
                      <div className="stage-title">
                        <span className="stage-icon">{getStageIcon(stage.role)}</span>
                        {stage.name}
                        {stage.required && <span className="required-badge">Required</span>}
                      </div>
                      <p className="stage-description">{stage.description}</p>
                    </div>

                    <div className="stage-status-section">
                      <span className={`badge badge-${getStatusColor(stage.status)}`}>
                        {getStatusIcon(stage.status)}
                        {formatStageStatus(stage.status)}
                      </span>
                    </div>
                  </div>

                  {stage.assigned_to_name && (
                    <div className="stage-assignee">
                      <span className="assignee-label">Assigned to:</span>
                      <span className="assignee-name">{stage.assigned_to_name}</span>
                    </div>
                  )}

                  {stage.completed_by_name && stage.completed_at && (
                    <div className="stage-completed">
                      <span className="completed-text">
                        {stage.status === 'approved' ? 'Approved' : 'Completed'} by{' '}
                        {stage.completed_by_name} on{' '}
                        {new Date(stage.completed_at).toLocaleString()}
                      </span>
                    </div>
                  )}

                  {/* Comments for this stage */}
                  {request.comments.filter(c => c.stage_id === stage.id).length > 0 && (
                    <div className="stage-comments">
                      {request.comments
                        .filter(c => c.stage_id === stage.id)
                        .map(c => (
                          <div key={c.id} className="comment-item">
                            <div className="comment-header">
                              <span className="comment-author">{c.user_name}</span>
                              <span className="comment-action">
                                {formatAction(c.action)}
                              </span>
                              <span className="comment-time">
                                {new Date(c.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="comment-text">{c.comment}</p>
                          </div>
                        ))}
                    </div>
                  )}

                  {/* Action buttons */}
                  {canApprove && !isExpanded && (
                    <button
                      onClick={() => setActiveStageId(stage.id)}
                      className="btn btn-primary btn-sm"
                    >
                      <MessageCircle size={16} />
                      Take Action
                    </button>
                  )}

                  {/* Action panel */}
                  {isExpanded && canApprove && (
                    <div className="action-panel">
                      <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Add your comments..."
                        className="action-textarea"
                        rows={3}
                      />

                      <div className="action-buttons">
                        <button
                          onClick={() => handleAction(stage, 'approve')}
                          disabled={submitting}
                          className="btn btn-success btn-sm"
                        >
                          <CheckCircle size={16} />
                          Approve
                        </button>

                        <button
                          onClick={() => handleAction(stage, 'request_changes')}
                          disabled={submitting}
                          className="btn btn-warning btn-sm"
                        >
                          <Send size={16} />
                          Request Changes
                        </button>

                        <button
                          onClick={() => handleAction(stage, 'reject')}
                          disabled={submitting}
                          className="btn btn-danger btn-sm"
                        >
                          <XCircle size={16} />
                          Reject
                        </button>

                        {!stage.required && (
                          <button
                            onClick={() => handleAction(stage, 'skip')}
                            disabled={submitting}
                            className="btn btn-secondary btn-sm"
                          >
                            <SkipForward size={16} />
                            Skip
                          </button>
                        )}

                        <button
                          onClick={() => {
                            setActiveStageId(null);
                            setComment('');
                          }}
                          disabled={submitting}
                          className="btn btn-secondary btn-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Connector line */}
              {index < request.stages.length - 1 && (
                <div className="stage-connector">
                  <div className={`connector-line ${stage.status === 'approved' ? 'connector-completed' : ''}`} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Helper functions
function getRequestStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'warning',
    in_progress: 'info',
    approved: 'success',
    rejected: 'error',
    cancelled: 'secondary',
  };
  return colors[status] || 'secondary';
}

function formatRequestStatus(status: string): string {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatStageStatus(status: string): string {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatAction(action: string): string {
  return action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getStatusIcon(status: string) {
  const icons: Record<string, JSX.Element> = {
    pending: <Clock size={14} />,
    in_progress: <AlertCircle size={14} />,
    approved: <CheckCircle size={14} />,
    rejected: <XCircle size={14} />,
    skipped: <SkipForward size={14} />,
    changes_requested: <MessageCircle size={14} />,
  };
  return icons[status] || null;
}
