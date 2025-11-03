/**
 * Multi-Stage Approval Workflow Types
 * Supports complex approval chains for enterprise marketing teams
 */

export type ApprovalRole =
  | 'content_creator'
  | 'content_reviewer'
  | 'legal_reviewer'
  | 'marketing_manager'
  | 'cmo'
  | 'compliance_officer';

export type ApprovalAction =
  | 'submit'
  | 'approve'
  | 'reject'
  | 'request_changes'
  | 'skip';

export type ApprovalStageStatus =
  | 'pending'
  | 'in_progress'
  | 'approved'
  | 'rejected'
  | 'skipped'
  | 'changes_requested';

export interface ApprovalStage {
  id: string;
  name: string;
  description: string;
  role: ApprovalRole;
  order: number;
  required: boolean;
  status: ApprovalStageStatus;
  assigned_to?: string; // User ID
  assigned_to_name?: string; // User display name
  completed_at?: string;
  completed_by?: string; // User ID
  completed_by_name?: string; // User display name
}

export interface ApprovalComment {
  id: string;
  stage_id: string;
  user_id: string;
  user_name: string;
  user_role: ApprovalRole;
  action: ApprovalAction;
  comment: string;
  created_at: string;
  mentions?: string[]; // User IDs of mentioned users
}

export interface ApprovalRequest {
  id: string;
  content_id: string;
  content_title: string;
  workflow_id: string;
  workflow_name: string;
  current_stage_id: string;
  status: 'pending' | 'in_progress' | 'approved' | 'rejected' | 'cancelled';
  created_at: string;
  created_by: string; // User ID
  created_by_name: string; // User display name
  updated_at: string;
  completed_at?: string;
  stages: ApprovalStage[];
  comments: ApprovalComment[];
}

export interface ApprovalWorkflow {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  stages: Omit<ApprovalStage, 'id' | 'status' | 'completed_at' | 'completed_by' | 'completed_by_name'>[];
  applicable_content_types?: string[]; // If null, applies to all
  applicable_platforms?: string[]; // If null, applies to all
}

export interface ApprovalHistory {
  id: string;
  content_id: string;
  approval_request_id: string;
  stage_id: string;
  stage_name: string;
  user_id: string;
  user_name: string;
  user_role: ApprovalRole;
  action: ApprovalAction;
  comment?: string;
  previous_status: ApprovalStageStatus;
  new_status: ApprovalStageStatus;
  created_at: string;
}

export interface ApprovalNotification {
  id: string;
  type: 'approval_request' | 'approval_approved' | 'approval_rejected' | 'changes_requested' | 'mention';
  content_id: string;
  content_title: string;
  approval_request_id: string;
  from_user_id: string;
  from_user_name: string;
  to_user_id: string;
  message: string;
  read: boolean;
  created_at: string;
}

// Mock users for demo purposes
export interface User {
  id: string;
  name: string;
  email: string;
  role: ApprovalRole;
  avatar?: string;
}

// Helper functions
export function getNextStage(request: ApprovalRequest): ApprovalStage | null {
  const currentIndex = request.stages.findIndex(s => s.id === request.current_stage_id);
  if (currentIndex === -1 || currentIndex === request.stages.length - 1) {
    return null;
  }
  return request.stages[currentIndex + 1];
}

export function canUserApprove(user: User, stage: ApprovalStage): boolean {
  return user.role === stage.role || user.role === 'cmo'; // CMO can approve any stage
}

export function getStageIcon(role: ApprovalRole): string {
  const icons: Record<ApprovalRole, string> = {
    content_creator: '✍️',
    content_reviewer: '👀',
    legal_reviewer: '⚖️',
    marketing_manager: '📊',
    cmo: '👔',
    compliance_officer: '🛡️',
  };
  return icons[role] || '👤';
}

export function getActionColor(action: ApprovalAction): string {
  const colors: Record<ApprovalAction, string> = {
    submit: 'primary',
    approve: 'success',
    reject: 'error',
    request_changes: 'warning',
    skip: 'secondary',
  };
  return colors[action] || 'secondary';
}

export function getStatusColor(status: ApprovalStageStatus): string {
  const colors: Record<ApprovalStageStatus, string> = {
    pending: 'secondary',
    in_progress: 'info',
    approved: 'success',
    rejected: 'error',
    skipped: 'secondary',
    changes_requested: 'warning',
  };
  return colors[status] || 'secondary';
}
