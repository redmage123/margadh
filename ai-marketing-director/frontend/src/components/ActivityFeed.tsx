import { useState, useEffect } from 'react';
import {
  Activity as ActivityIcon,
  MessageCircle,
  FileText,
  CheckCircle,
  XCircle,
  GitBranch,
  UserPlus,
  Edit,
  Trash2,
  Send,
  AlertCircle,
} from 'lucide-react';
import type { Activity } from '@/types/collaboration';
import { getActivities } from '@/services/collaboration';
import { formatRelativeTime, getActivityDescription } from '@/types/collaboration';
import './ActivityFeed.css';

interface ActivityFeedProps {
  contentId: string;
  limit?: number;
}

export const ActivityFeed = ({ contentId, limit }: ActivityFeedProps) => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchActivities();
  }, [contentId]);

  const fetchActivities = async () => {
    setLoading(true);
    try {
      let data = await getActivities(contentId);

      if (limit) {
        data = data.slice(0, limit);
      }

      setActivities(data);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredActivities = activities.filter(activity => {
    if (filter === 'all') return true;

    const categoryMap: Record<string, string[]> = {
      content: ['content_created', 'content_updated', 'content_published', 'content_deleted'],
      comments: ['comment_added', 'user_mentioned'],
      approvals: ['approval_submitted', 'approval_approved', 'approval_rejected'],
      versions: ['version_created'],
      assignments: ['user_assigned', 'status_changed'],
    };

    return categoryMap[filter]?.includes(activity.type) || false;
  });

  if (loading) {
    return (
      <div className="activity-feed-loading">
        <ActivityIcon className="animate-spin" size={24} />
        <p>Loading activity feed...</p>
      </div>
    );
  }

  return (
    <div className="activity-feed">
      <div className="activity-feed-header">
        <h3 className="activity-feed-title">
          <ActivityIcon size={20} />
          Activity Feed ({activities.length})
        </h3>

        {activities.length > 10 && (
          <div className="activity-filters">
            <button
              onClick={() => setFilter('all')}
              className={`filter-chip ${filter === 'all' ? 'filter-chip-active' : ''}`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('content')}
              className={`filter-chip ${filter === 'content' ? 'filter-chip-active' : ''}`}
            >
              Content
            </button>
            <button
              onClick={() => setFilter('comments')}
              className={`filter-chip ${filter === 'comments' ? 'filter-chip-active' : ''}`}
            >
              Comments
            </button>
            <button
              onClick={() => setFilter('approvals')}
              className={`filter-chip ${filter === 'approvals' ? 'filter-chip-active' : ''}`}
            >
              Approvals
            </button>
            <button
              onClick={() => setFilter('versions')}
              className={`filter-chip ${filter === 'versions' ? 'filter-chip-active' : ''}`}
            >
              Versions
            </button>
          </div>
        )}
      </div>

      {filteredActivities.length === 0 ? (
        <div className="activity-feed-empty">
          <AlertCircle size={48} />
          <p>No activity yet</p>
        </div>
      ) : (
        <div className="activity-timeline">
          {filteredActivities.map((activity, index) => (
            <ActivityItem
              key={activity.id}
              activity={activity}
              isLast={index === filteredActivities.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Activity Item Component
interface ActivityItemProps {
  activity: Activity;
  isLast: boolean;
}

const ActivityItem = ({ activity, isLast }: ActivityItemProps) => {
  const icon = getActivityTypeIcon(activity.type);
  const description = getActivityDescription(activity);

  return (
    <div className="activity-item">
      <div className="activity-icon-wrapper">
        <div className={`activity-icon activity-icon-${getCategoryForType(activity.type)}`}>
          {icon}
        </div>
        {!isLast && <div className="activity-timeline-line" />}
      </div>

      <div className="activity-content">
        <div className="activity-header">
          <div className="activity-user">
            <span className="activity-user-name">{activity.user_name}</span>
            <span className="activity-description">{description}</span>
          </div>
          <span className="activity-time">{formatRelativeTime(activity.created_at)}</span>
        </div>

        {activity.metadata && (
          <ActivityMetadata activity={activity} />
        )}
      </div>
    </div>
  );
};

// Activity Metadata Component
const ActivityMetadata = ({ activity }: { activity: Activity }) => {
  const { type, metadata } = activity;

  if (!metadata) return null;

  switch (type) {
    case 'comment_added':
      return (
        <div className="activity-metadata">
          <MessageCircle size={14} />
          <span className="activity-metadata-text">
            "{metadata.comment_text}"
          </span>
        </div>
      );

    case 'version_created':
      return (
        <div className="activity-metadata">
          <GitBranch size={14} />
          <span className="activity-metadata-text">
            {metadata.change_summary || `Version ${metadata.version}`}
            {metadata.restored_from && ` (restored from v${metadata.restored_from})`}
          </span>
        </div>
      );

    case 'status_changed':
      return (
        <div className="activity-metadata">
          <AlertCircle size={14} />
          <span className="activity-metadata-text">
            Changed to: <strong>{metadata.status}</strong>
          </span>
        </div>
      );

    case 'user_assigned':
      return (
        <div className="activity-metadata">
          <UserPlus size={14} />
          <span className="activity-metadata-text">
            Assigned to: <strong>{metadata.assigned_to}</strong>
          </span>
        </div>
      );

    case 'approval_submitted':
    case 'approval_approved':
    case 'approval_rejected':
      return (
        <div className="activity-metadata">
          {metadata.comment && (
            <>
              <MessageCircle size={14} />
              <span className="activity-metadata-text">
                "{metadata.comment}"
              </span>
            </>
          )}
        </div>
      );

    default:
      return null;
  }
};

// Helper functions
function getActivityTypeIcon(type: string) {
  const iconMap: Record<string, JSX.Element> = {
    content_created: <FileText size={16} />,
    content_updated: <Edit size={16} />,
    content_published: <Send size={16} />,
    content_deleted: <Trash2 size={16} />,
    comment_added: <MessageCircle size={16} />,
    user_mentioned: <AlertCircle size={16} />,
    status_changed: <AlertCircle size={16} />,
    approval_submitted: <Send size={16} />,
    approval_approved: <CheckCircle size={16} />,
    approval_rejected: <XCircle size={16} />,
    version_created: <GitBranch size={16} />,
    user_assigned: <UserPlus size={16} />,
  };

  return iconMap[type] || <ActivityIcon size={16} />;
}

function getCategoryForType(type: string): string {
  const categoryMap: Record<string, string> = {
    content_created: 'content',
    content_updated: 'content',
    content_published: 'content',
    content_deleted: 'content',
    comment_added: 'comment',
    user_mentioned: 'comment',
    status_changed: 'status',
    approval_submitted: 'approval',
    approval_approved: 'approval',
    approval_rejected: 'approval',
    version_created: 'version',
    user_assigned: 'assignment',
  };

  return categoryMap[type] || 'default';
}
