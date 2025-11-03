/**
 * Collaboration Features Types
 * Supports commenting, @mentions, version history, and activity tracking
 */

import type { User } from './approval';

export type ActivityType =
  | 'content_created'
  | 'content_updated'
  | 'content_published'
  | 'content_deleted'
  | 'comment_added'
  | 'user_mentioned'
  | 'status_changed'
  | 'approval_submitted'
  | 'approval_approved'
  | 'approval_rejected'
  | 'version_created'
  | 'user_assigned';

export interface Comment {
  id: string;
  content_id: string;
  user_id: string;
  user_name: string;
  user_avatar?: string;
  text: string;
  mentions: string[]; // User IDs mentioned in comment
  parent_id?: string; // For threaded replies
  created_at: string;
  updated_at?: string;
  edited: boolean;
  resolved: boolean;
  attachments?: Attachment[];
}

export interface Mention {
  id: string;
  user_id: string;
  mentioned_by: string;
  mentioned_by_name: string;
  comment_id: string;
  content_id: string;
  content_title: string;
  text: string; // Comment text with context
  read: boolean;
  created_at: string;
}

export interface Attachment {
  id: string;
  name: string;
  url: string;
  type: string;
  size: number;
  uploaded_by: string;
  uploaded_at: string;
}

export interface ContentVersion {
  id: string;
  content_id: string;
  version_number: number;
  title: string;
  body: string;
  metadata?: Record<string, any>;
  created_by: string;
  created_by_name: string;
  created_at: string;
  change_summary?: string;
  is_current: boolean;
}

export interface ContentDiff {
  field: string;
  old_value: string;
  new_value: string;
  change_type: 'added' | 'removed' | 'modified';
}

export interface Activity {
  id: string;
  content_id: string;
  type: ActivityType;
  user_id: string;
  user_name: string;
  user_avatar?: string;
  description: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface CollaborationStats {
  total_comments: number;
  total_versions: number;
  total_collaborators: number;
  last_activity: string;
  active_commenters: User[];
}

// Helper functions

/**
 * Parse text for @mentions
 * Returns array of mentioned user IDs
 */
export function parseMentions(text: string, users: User[]): string[] {
  const mentionRegex = /@(\w+)/g;
  const matches = text.match(mentionRegex);

  if (!matches) return [];

  const mentioned: string[] = [];
  matches.forEach(match => {
    const username = match.substring(1);
    const user = users.find(u =>
      u.name.toLowerCase().replace(/\s+/g, '') === username.toLowerCase()
    );
    if (user && !mentioned.includes(user.id)) {
      mentioned.push(user.id);
    }
  });

  return mentioned;
}

/**
 * Highlight @mentions in text
 */
export function highlightMentions(text: string, users: User[]): string {
  const mentionRegex = /@(\w+)/g;
  return text.replace(mentionRegex, (match) => {
    const username = match.substring(1);
    const user = users.find(u =>
      u.name.toLowerCase().replace(/\s+/g, '') === username.toLowerCase()
    );
    if (user) {
      return `<span class="mention">@${user.name}</span>`;
    }
    return match;
  });
}

/**
 * Calculate diff between two text values
 */
export function calculateTextDiff(oldText: string, newText: string): ContentDiff[] {
  const diffs: ContentDiff[] = [];

  // Simple line-by-line diff
  const oldLines = oldText.split('\n');
  const newLines = newText.split('\n');

  const maxLength = Math.max(oldLines.length, newLines.length);

  for (let i = 0; i < maxLength; i++) {
    const oldLine = oldLines[i] || '';
    const newLine = newLines[i] || '';

    if (oldLine !== newLine) {
      if (!oldLine) {
        diffs.push({
          field: `line-${i + 1}`,
          old_value: '',
          new_value: newLine,
          change_type: 'added',
        });
      } else if (!newLine) {
        diffs.push({
          field: `line-${i + 1}`,
          old_value: oldLine,
          new_value: '',
          change_type: 'removed',
        });
      } else {
        diffs.push({
          field: `line-${i + 1}`,
          old_value: oldLine,
          new_value: newLine,
          change_type: 'modified',
        });
      }
    }
  }

  return diffs;
}

/**
 * Generate activity description
 */
export function getActivityDescription(activity: Activity): string {
  const descriptions: Record<ActivityType, string> = {
    content_created: `created this content`,
    content_updated: `updated this content`,
    content_published: `published this content`,
    content_deleted: `deleted this content`,
    comment_added: `added a comment`,
    user_mentioned: `mentioned you`,
    status_changed: `changed status to ${activity.metadata?.status || 'unknown'}`,
    approval_submitted: `submitted for approval`,
    approval_approved: `approved this content`,
    approval_rejected: `rejected this content`,
    version_created: `created version ${activity.metadata?.version || 'unknown'}`,
    user_assigned: `assigned ${activity.metadata?.assigned_to || 'someone'}`,
  };

  return descriptions[activity.type] || 'performed an action';
}

/**
 * Get activity icon
 */
export function getActivityIcon(type: ActivityType): string {
  const icons: Record<ActivityType, string> = {
    content_created: '✨',
    content_updated: '✏️',
    content_published: '🚀',
    content_deleted: '🗑️',
    comment_added: '💬',
    user_mentioned: '👤',
    status_changed: '🔄',
    approval_submitted: '📤',
    approval_approved: '✅',
    approval_rejected: '❌',
    version_created: '📝',
    user_assigned: '👥',
  };

  return icons[type] || '📌';
}

/**
 * Format relative time
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

  return date.toLocaleDateString();
}
