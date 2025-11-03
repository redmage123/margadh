// Core types for AI Marketing Director

export type Platform = 'linkedin' | 'twitter' | 'blog' | 'email';
export type PlatformWithAll = Platform | 'all';
export type ContentType = 'blog' | 'social' | 'email' | 'whitepaper' | 'case_study';
export type ContentStatus = 'draft' | 'review' | 'approved' | 'published' | 'rejected';

export interface Content {
  id: string;
  type: ContentType;
  title: string;
  body: string;
  platform?: Platform;
  status: ContentStatus;
  created_at: string;
  published_at?: string;
  brand_voice_score?: number;
  seo_score?: number;
  analytics?: ContentAnalytics;
  tags?: string[];
  metadata?: {
    target_audience?: string;
    keywords?: string;
    cta?: string;
    [key: string]: any;
  };
}

export interface ContentAnalytics {
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
  impressions?: number;
}

export interface OAuthIntegration {
  platform: Platform;
  configured?: boolean;
  connected?: boolean;
  is_connected: boolean;
  user_id?: string;
  username?: string;
  expires_at?: string | null;
  scopes?: string[];
  details?: {
    name?: string;
    followers?: number;
    organization_id?: string;
  };
  error?: string;
}

export interface DashboardMetrics {
  total_content: number;
  published_this_week: number;
  avg_engagement_rate: number;
  total_reach: number;
  pending_review: number;
}

export interface TopicSuggestion {
  title: string;
  why_now: string;
  target_audience: string;
  key_angles: string[];
  differentiation: string;
  seo_keywords: string[];
}

export interface Campaign {
  id: string;
  name?: string;
  objective: string;
  status: 'planning' | 'active' | 'paused' | 'completed' | 'cancelled';
  start_date?: string;
  end_date?: string;
  timeframe?: string;
  created_at: string;
  content_pieces?: Array<{
    id: string;
    title: string;
    type: ContentType;
    status: ContentStatus;
  }>;
  tasks?: Array<{
    id: string;
    description: string;
    status: string;
    assigned_to?: string;
  }>;
  target_metrics?: Record<string, number>;
  actual_metrics?: Record<string, number>;
}

export interface Task {
  id: string;
  type: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  completed_at?: string;
}

// Re-export approval types
export type {
  ApprovalWorkflow,
  ApprovalRequest,
  ApprovalStage,
  ApprovalComment,
  ApprovalAction,
  ApprovalRole,
  ApprovalStageStatus,
  User,
} from './approval';

// Re-export collaboration types
export type {
  Comment,
  Mention,
  Attachment,
  ContentVersion,
  ContentDiff,
  Activity,
  ActivityType,
  CollaborationStats,
} from './collaboration';

export {
  parseMentions,
  highlightMentions,
  calculateTextDiff,
  getActivityDescription,
  getActivityIcon,
  formatRelativeTime,
} from './collaboration';
