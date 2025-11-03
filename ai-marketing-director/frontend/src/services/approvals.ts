/**
 * Approval Workflow Service
 * Manages multi-stage approval processes for content
 */

import type {
  ApprovalWorkflow,
  ApprovalRequest,
  ApprovalStage,
  ApprovalComment,
  ApprovalAction,
  User,
  ApprovalRole,
  ApprovalStageStatus,
} from '@/types/approval';

// Mock users for demonstration
export const MOCK_USERS: User[] = [
  {
    id: 'user-1',
    name: 'John Creator',
    email: 'john@example.com',
    role: 'content_creator',
  },
  {
    id: 'user-2',
    name: 'Sarah Reviewer',
    email: 'sarah@example.com',
    role: 'content_reviewer',
  },
  {
    id: 'user-3',
    name: 'Mike Legal',
    email: 'mike@example.com',
    role: 'legal_reviewer',
  },
  {
    id: 'user-4',
    name: 'Lisa Manager',
    email: 'lisa@example.com',
    role: 'marketing_manager',
  },
  {
    id: 'user-5',
    name: 'David CMO',
    email: 'david@example.com',
    role: 'cmo',
  },
];

// Current logged-in user (mock)
export const CURRENT_USER: User = MOCK_USERS[0]; // Content Creator

// Default approval workflows
export const DEFAULT_WORKFLOWS: ApprovalWorkflow[] = [
  {
    id: 'workflow-standard',
    name: 'Standard Approval',
    description: 'Standard 2-stage approval for regular content',
    is_active: true,
    is_default: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    stages: [
      {
        name: 'Content Review',
        description: 'Initial content quality and brand voice review',
        role: 'content_reviewer',
        order: 1,
        required: true,
        assigned_to: 'user-2',
        assigned_to_name: 'Sarah Reviewer',
      },
      {
        name: 'Manager Approval',
        description: 'Marketing manager final approval',
        role: 'marketing_manager',
        order: 2,
        required: true,
        assigned_to: 'user-4',
        assigned_to_name: 'Lisa Manager',
      },
    ],
  },
  {
    id: 'workflow-legal',
    name: 'Legal Review Required',
    description: 'Includes legal review for sensitive content',
    is_active: true,
    is_default: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    stages: [
      {
        name: 'Content Review',
        description: 'Initial content quality review',
        role: 'content_reviewer',
        order: 1,
        required: true,
        assigned_to: 'user-2',
        assigned_to_name: 'Sarah Reviewer',
      },
      {
        name: 'Legal Review',
        description: 'Legal compliance and risk assessment',
        role: 'legal_reviewer',
        order: 2,
        required: true,
        assigned_to: 'user-3',
        assigned_to_name: 'Mike Legal',
      },
      {
        name: 'Manager Approval',
        description: 'Marketing manager approval',
        role: 'marketing_manager',
        order: 3,
        required: true,
        assigned_to: 'user-4',
        assigned_to_name: 'Lisa Manager',
      },
    ],
    applicable_content_types: ['whitepaper', 'case_study'],
  },
  {
    id: 'workflow-executive',
    name: 'Executive Approval',
    description: 'Full approval chain including CMO for high-impact content',
    is_active: true,
    is_default: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    stages: [
      {
        name: 'Content Review',
        description: 'Content quality review',
        role: 'content_reviewer',
        order: 1,
        required: true,
        assigned_to: 'user-2',
        assigned_to_name: 'Sarah Reviewer',
      },
      {
        name: 'Legal Review',
        description: 'Legal compliance review',
        role: 'legal_reviewer',
        order: 2,
        required: true,
        assigned_to: 'user-3',
        assigned_to_name: 'Mike Legal',
      },
      {
        name: 'Manager Approval',
        description: 'Marketing manager approval',
        role: 'marketing_manager',
        order: 3,
        required: true,
        assigned_to: 'user-4',
        assigned_to_name: 'Lisa Manager',
      },
      {
        name: 'CMO Approval',
        description: 'Final executive approval',
        role: 'cmo',
        order: 4,
        required: true,
        assigned_to: 'user-5',
        assigned_to_name: 'David CMO',
      },
    ],
  },
];

// In-memory storage for approval requests (would be API calls in production)
let approvalRequests: ApprovalRequest[] = [];

/**
 * Get all approval workflows
 */
export async function getWorkflows(): Promise<ApprovalWorkflow[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  return DEFAULT_WORKFLOWS;
}

/**
 * Get workflow by ID
 */
export async function getWorkflow(id: string): Promise<ApprovalWorkflow | null> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return DEFAULT_WORKFLOWS.find(w => w.id === id) || null;
}

/**
 * Get default workflow for content type
 */
export async function getDefaultWorkflow(contentType?: string): Promise<ApprovalWorkflow> {
  await new Promise(resolve => setTimeout(resolve, 100));

  // Find workflow that applies to this content type
  if (contentType) {
    const specific = DEFAULT_WORKFLOWS.find(
      w => w.is_active && w.applicable_content_types?.includes(contentType)
    );
    if (specific) return specific;
  }

  // Return default workflow
  return DEFAULT_WORKFLOWS.find(w => w.is_default)!;
}

/**
 * Create approval request for content
 */
export async function createApprovalRequest(
  contentId: string,
  contentTitle: string,
  workflowId: string
): Promise<ApprovalRequest> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const workflow = await getWorkflow(workflowId);
  if (!workflow) throw new Error('Workflow not found');

  const stages: ApprovalStage[] = workflow.stages.map((template, index) => ({
    id: `stage-${Date.now()}-${index}`,
    name: template.name,
    description: template.description,
    role: template.role,
    order: template.order,
    required: template.required,
    status: index === 0 ? 'in_progress' : 'pending',
    assigned_to: template.assigned_to,
    assigned_to_name: template.assigned_to_name,
  }));

  const request: ApprovalRequest = {
    id: `request-${Date.now()}`,
    content_id: contentId,
    content_title: contentTitle,
    workflow_id: workflowId,
    workflow_name: workflow.name,
    current_stage_id: stages[0].id,
    status: 'in_progress',
    created_at: new Date().toISOString(),
    created_by: CURRENT_USER.id,
    created_by_name: CURRENT_USER.name,
    updated_at: new Date().toISOString(),
    stages,
    comments: [],
  };

  approvalRequests.push(request);
  return request;
}

/**
 * Get approval request by ID
 */
export async function getApprovalRequest(id: string): Promise<ApprovalRequest | null> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return approvalRequests.find(r => r.id === id) || null;
}

/**
 * Get approval request by content ID
 */
export async function getApprovalRequestByContent(contentId: string): Promise<ApprovalRequest | null> {
  await new Promise(resolve => setTimeout(resolve, 100));
  const requests = approvalRequests.filter(r => r.content_id === contentId);
  // Return most recent active request
  return requests.find(r => r.status === 'in_progress' || r.status === 'pending') || requests[requests.length - 1] || null;
}

/**
 * Get all approval requests (with optional filtering)
 */
export async function getApprovalRequests(filter?: {
  status?: string;
  assigned_to?: string;
}): Promise<ApprovalRequest[]> {
  await new Promise(resolve => setTimeout(resolve, 100));

  let filtered = [...approvalRequests];

  if (filter?.status) {
    filtered = filtered.filter(r => r.status === filter.status);
  }

  if (filter?.assigned_to) {
    filtered = filtered.filter(r => {
      const currentStage = r.stages.find(s => s.id === r.current_stage_id);
      return currentStage?.assigned_to === filter.assigned_to;
    });
  }

  return filtered.sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  );
}

/**
 * Submit approval action (approve, reject, request changes)
 */
export async function submitApprovalAction(
  requestId: string,
  stageId: string,
  action: ApprovalAction,
  comment: string,
  userId: string = CURRENT_USER.id
): Promise<ApprovalRequest> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const request = approvalRequests.find(r => r.id === requestId);
  if (!request) throw new Error('Approval request not found');

  const stageIndex = request.stages.findIndex(s => s.id === stageId);
  if (stageIndex === -1) throw new Error('Stage not found');

  const stage = request.stages[stageIndex];
  const user = MOCK_USERS.find(u => u.id === userId) || CURRENT_USER;

  // Add comment
  const newComment: ApprovalComment = {
    id: `comment-${Date.now()}`,
    stage_id: stageId,
    user_id: userId,
    user_name: user.name,
    user_role: user.role,
    action,
    comment,
    created_at: new Date().toISOString(),
  };
  request.comments.push(newComment);

  // Update stage status
  let newStatus: ApprovalStageStatus;
  switch (action) {
    case 'approve':
      newStatus = 'approved';
      stage.completed_at = new Date().toISOString();
      stage.completed_by = userId;
      stage.completed_by_name = user.name;

      // Move to next stage or complete
      if (stageIndex < request.stages.length - 1) {
        const nextStage = request.stages[stageIndex + 1];
        nextStage.status = 'in_progress';
        request.current_stage_id = nextStage.id;
      } else {
        request.status = 'approved';
        request.completed_at = new Date().toISOString();
      }
      break;

    case 'reject':
      newStatus = 'rejected';
      stage.completed_at = new Date().toISOString();
      stage.completed_by = userId;
      stage.completed_by_name = user.name;
      request.status = 'rejected';
      request.completed_at = new Date().toISOString();
      break;

    case 'request_changes':
      newStatus = 'changes_requested';
      request.status = 'pending'; // Send back to creator
      break;

    case 'skip':
      newStatus = 'skipped';
      stage.completed_at = new Date().toISOString();
      stage.completed_by = userId;
      stage.completed_by_name = user.name;

      // Move to next stage
      if (stageIndex < request.stages.length - 1) {
        const nextStage = request.stages[stageIndex + 1];
        nextStage.status = 'in_progress';
        request.current_stage_id = nextStage.id;
      }
      break;

    default:
      throw new Error('Invalid action');
  }

  stage.status = newStatus;
  request.updated_at = new Date().toISOString();

  return request;
}

/**
 * Resubmit content after changes
 */
export async function resubmitApprovalRequest(
  requestId: string,
  comment?: string
): Promise<ApprovalRequest> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const request = approvalRequests.find(r => r.id === requestId);
  if (!request) throw new Error('Approval request not found');

  // Find the stage that requested changes
  const changesRequestedStage = request.stages.find(s => s.status === 'changes_requested');
  if (changesRequestedStage) {
    changesRequestedStage.status = 'in_progress';
    request.current_stage_id = changesRequestedStage.id;
  } else {
    // Start from beginning
    request.stages[0].status = 'in_progress';
    request.current_stage_id = request.stages[0].id;
  }

  request.status = 'in_progress';
  request.updated_at = new Date().toISOString();

  if (comment) {
    const newComment: ApprovalComment = {
      id: `comment-${Date.now()}`,
      stage_id: request.current_stage_id,
      user_id: CURRENT_USER.id,
      user_name: CURRENT_USER.name,
      user_role: CURRENT_USER.role,
      action: 'submit',
      comment,
      created_at: new Date().toISOString(),
    };
    request.comments.push(newComment);
  }

  return request;
}

/**
 * Cancel approval request
 */
export async function cancelApprovalRequest(requestId: string): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const request = approvalRequests.find(r => r.id === requestId);
  if (request) {
    request.status = 'cancelled';
    request.completed_at = new Date().toISOString();
    request.updated_at = new Date().toISOString();
  }
}

/**
 * Get pending approvals for user
 */
export async function getPendingApprovalsForUser(userId: string): Promise<ApprovalRequest[]> {
  await new Promise(resolve => setTimeout(resolve, 100));

  return approvalRequests.filter(r => {
    if (r.status !== 'in_progress') return false;
    const currentStage = r.stages.find(s => s.id === r.current_stage_id);
    return currentStage?.assigned_to === userId && currentStage.status === 'in_progress';
  });
}

/**
 * Get user by role
 */
export function getUsersByRole(role: ApprovalRole): User[] {
  return MOCK_USERS.filter(u => u.role === role);
}

/**
 * Initialize with some mock data for demo
 */
export function initializeMockApprovals() {
  // This would be called on app startup to populate some demo data
  approvalRequests = [];
}
