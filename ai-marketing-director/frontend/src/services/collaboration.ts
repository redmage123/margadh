/**
 * Collaboration Service
 * Manages comments, mentions, version history, and activity tracking
 */

import type {
  Comment,
  Mention,
  ContentVersion,
  Activity,
  ActivityType,
  CollaborationStats,
  ContentDiff,
} from '@/types/collaboration';
import type { Content } from '@/types';
import { CURRENT_USER, MOCK_USERS } from './approvals';
import { parseMentions, calculateTextDiff } from '@/types/collaboration';

// In-memory storage (would be API calls in production)
let comments: Comment[] = [];
let mentions: Mention[] = [];
let versions: ContentVersion[] = [];
let activities: Activity[] = [];

/**
 * Comments API
 */

export async function getComments(contentId: string): Promise<Comment[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return comments
    .filter(c => c.content_id === contentId)
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
}

export async function addComment(
  contentId: string,
  text: string,
  parentId?: string
): Promise<Comment> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const mentionedUserIds = parseMentions(text, MOCK_USERS);

  const comment: Comment = {
    id: `comment-${Date.now()}`,
    content_id: contentId,
    user_id: CURRENT_USER.id,
    user_name: CURRENT_USER.name,
    text,
    mentions: mentionedUserIds,
    parent_id: parentId,
    created_at: new Date().toISOString(),
    edited: false,
    resolved: false,
  };

  comments.push(comment);

  // Create activity
  await createActivity(contentId, 'comment_added', {
    comment_id: comment.id,
    comment_text: text.substring(0, 100),
  });

  // Create mentions
  for (const userId of mentionedUserIds) {
    await createMention(userId, comment);
  }

  return comment;
}

export async function updateComment(commentId: string, text: string): Promise<Comment> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const comment = comments.find(c => c.id === commentId);
  if (!comment) throw new Error('Comment not found');

  const mentionedUserIds = parseMentions(text, MOCK_USERS);

  comment.text = text;
  comment.mentions = mentionedUserIds;
  comment.updated_at = new Date().toISOString();
  comment.edited = true;

  // Create new mentions
  for (const userId of mentionedUserIds) {
    const existingMention = mentions.find(
      m => m.comment_id === commentId && m.user_id === userId
    );
    if (!existingMention) {
      await createMention(userId, comment);
    }
  }

  return comment;
}

export async function deleteComment(commentId: string): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 200));
  comments = comments.filter(c => c.id !== commentId);
  mentions = mentions.filter(m => m.comment_id !== commentId);
}

export async function resolveComment(commentId: string): Promise<Comment> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const comment = comments.find(c => c.id === commentId);
  if (!comment) throw new Error('Comment not found');

  comment.resolved = true;
  return comment;
}

export async function unresolveComment(commentId: string): Promise<Comment> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const comment = comments.find(c => c.id === commentId);
  if (!comment) throw new Error('Comment not found');

  comment.resolved = false;
  return comment;
}

/**
 * Mentions API
 */

async function createMention(userId: string, comment: Comment): Promise<void> {
  const mention: Mention = {
    id: `mention-${Date.now()}-${userId}`,
    user_id: userId,
    mentioned_by: comment.user_id,
    mentioned_by_name: comment.user_name,
    comment_id: comment.id,
    content_id: comment.content_id,
    content_title: 'Content Title', // Would be fetched from content
    text: comment.text,
    read: false,
    created_at: new Date().toISOString(),
  };

  mentions.push(mention);

  // Create activity
  await createActivity(comment.content_id, 'user_mentioned', {
    mentioned_user: userId,
    comment_id: comment.id,
  });
}

export async function getMentions(userId: string): Promise<Mention[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return mentions
    .filter(m => m.user_id === userId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

export async function markMentionAsRead(mentionId: string): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 100));
  const mention = mentions.find(m => m.id === mentionId);
  if (mention) {
    mention.read = true;
  }
}

export async function getUnreadMentionsCount(userId: string): Promise<number> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return mentions.filter(m => m.user_id === userId && !m.read).length;
}

/**
 * Version History API
 */

export async function createVersion(content: Content, changeSummary?: string): Promise<ContentVersion> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const existingVersions = versions.filter(v => v.content_id === content.id);
  const versionNumber = existingVersions.length + 1;

  // Mark previous versions as not current
  existingVersions.forEach(v => {
    v.is_current = false;
  });

  const version: ContentVersion = {
    id: `version-${Date.now()}`,
    content_id: content.id,
    version_number: versionNumber,
    title: content.title,
    body: content.body,
    metadata: content.metadata,
    created_by: CURRENT_USER.id,
    created_by_name: CURRENT_USER.name,
    created_at: new Date().toISOString(),
    change_summary: changeSummary,
    is_current: true,
  };

  versions.push(version);

  // Create activity
  await createActivity(content.id, 'version_created', {
    version: versionNumber,
    change_summary: changeSummary,
  });

  return version;
}

export async function getVersions(contentId: string): Promise<ContentVersion[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return versions
    .filter(v => v.content_id === contentId)
    .sort((a, b) => b.version_number - a.version_number);
}

export async function getVersion(versionId: string): Promise<ContentVersion | null> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return versions.find(v => v.id === versionId) || null;
}

export async function compareVersions(
  versionId1: string,
  versionId2: string
): Promise<ContentDiff[]> {
  await new Promise(resolve => setTimeout(resolve, 100));

  const version1 = versions.find(v => v.id === versionId1);
  const version2 = versions.find(v => v.id === versionId2);

  if (!version1 || !version2) {
    throw new Error('Version not found');
  }

  const diffs: ContentDiff[] = [];

  // Compare title
  if (version1.title !== version2.title) {
    diffs.push({
      field: 'title',
      old_value: version1.title,
      new_value: version2.title,
      change_type: 'modified',
    });
  }

  // Compare body
  const bodyDiffs = calculateTextDiff(version1.body, version2.body);
  diffs.push(...bodyDiffs);

  return diffs;
}

export async function restoreVersion(versionId: string): Promise<ContentVersion> {
  await new Promise(resolve => setTimeout(resolve, 200));

  const version = versions.find(v => v.id === versionId);
  if (!version) throw new Error('Version not found');

  // Mark all versions as not current
  versions.forEach(v => {
    if (v.content_id === version.content_id) {
      v.is_current = false;
    }
  });

  // Create new version from restored content
  const restoredVersion: ContentVersion = {
    id: `version-${Date.now()}`,
    content_id: version.content_id,
    version_number: versions.filter(v => v.content_id === version.content_id).length + 1,
    title: version.title,
    body: version.body,
    metadata: version.metadata,
    created_by: CURRENT_USER.id,
    created_by_name: CURRENT_USER.name,
    created_at: new Date().toISOString(),
    change_summary: `Restored from version ${version.version_number}`,
    is_current: true,
  };

  versions.push(restoredVersion);

  // Create activity
  await createActivity(version.content_id, 'version_created', {
    version: restoredVersion.version_number,
    restored_from: version.version_number,
  });

  return restoredVersion;
}

/**
 * Activity Feed API
 */

export async function createActivity(
  contentId: string,
  type: ActivityType,
  metadata?: Record<string, any>
): Promise<Activity> {
  const activity: Activity = {
    id: `activity-${Date.now()}`,
    content_id: contentId,
    type,
    user_id: CURRENT_USER.id,
    user_name: CURRENT_USER.name,
    description: '', // Will be generated by helper
    metadata,
    created_at: new Date().toISOString(),
  };

  activities.push(activity);
  return activity;
}

export async function getActivities(contentId: string): Promise<Activity[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return activities
    .filter(a => a.content_id === contentId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

export async function getRecentActivities(limit: number = 10): Promise<Activity[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return activities
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, limit);
}

/**
 * Collaboration Stats API
 */

export async function getCollaborationStats(contentId: string): Promise<CollaborationStats> {
  await new Promise(resolve => setTimeout(resolve, 100));

  const contentComments = comments.filter(c => c.content_id === contentId);
  const contentVersions = versions.filter(v => v.content_id === contentId);
  const contentActivities = activities.filter(a => a.content_id === contentId);

  // Get unique collaborators
  const collaboratorIds = new Set<string>();
  contentComments.forEach(c => collaboratorIds.add(c.user_id));
  contentVersions.forEach(v => collaboratorIds.add(v.created_by));
  contentActivities.forEach(a => collaboratorIds.add(a.user_id));

  // Get active commenters
  const commenterCounts = new Map<string, number>();
  contentComments.forEach(c => {
    commenterCounts.set(c.user_id, (commenterCounts.get(c.user_id) || 0) + 1);
  });

  const activeCommenters = Array.from(commenterCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([userId]) => MOCK_USERS.find(u => u.id === userId))
    .filter(Boolean) as any[];

  const lastActivity = contentActivities.length > 0
    ? contentActivities[contentActivities.length - 1].created_at
    : new Date().toISOString();

  return {
    total_comments: contentComments.length,
    total_versions: contentVersions.length,
    total_collaborators: collaboratorIds.size,
    last_activity: lastActivity,
    active_commenters: activeCommenters,
  };
}

/**
 * Initialize with mock data
 */
export function initializeMockCollaboration() {
  comments = [];
  mentions = [];
  versions = [];
  activities = [];
}
