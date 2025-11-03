import axios from 'axios';
import type {
  Content,
  OAuthIntegration,
  DashboardMetrics,
  TopicSuggestion,
  Campaign,
  Task,
  Platform,
  ContentType,
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard
export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const response = await api.get('/dashboard/metrics');
  return response.data;
};

// Content
export const getContent = async (status?: string): Promise<Content[]> => {
  const params = status ? { status } : {};
  const response = await api.get('/content', { params });
  return response.data;
};

export const getContentById = async (id: string): Promise<Content> => {
  const response = await api.get(`/content/${id}`);
  return response.data;
};

export const createContent = async (data: Partial<Content>): Promise<Content> => {
  const response = await api.post('/content', data);
  return response.data;
};

export const updateContent = async (id: string, data: Partial<Content>): Promise<Content> => {
  const response = await api.put(`/content/${id}`, data);
  return response.data;
};

export const approveContent = async (id: string): Promise<Content> => {
  const response = await api.post(`/content/${id}/approve`);
  return response.data;
};

export const publishContent = async (id: string, platform: string): Promise<Content> => {
  const response = await api.post(`/content/${id}/publish`, { platform });
  return response.data;
};

export const deleteContent = async (id: string): Promise<void> => {
  await api.delete(`/content/${id}`);
};

export const generateContent = async (params: {
  topic: string;
  content_type: ContentType;
  platform: string;
  target_audience?: string;
}): Promise<{
  content: string;
  brand_voice_score: number;
  seo_score: number;
}> => {
  const response = await api.post('/content/generate', params);
  return response.data;
};

// Topic Suggestions
export const getTopicSuggestions = async (params: {
  content_type: ContentType;
  count?: number;
}): Promise<TopicSuggestion[]> => {
  const response = await api.post('/strategy/content-topics', params);
  return response.data.topics;
};

// OAuth Integrations
export const getOAuthStatus = async (): Promise<Record<Platform, OAuthIntegration>> => {
  const response = await api.get('/oauth/status');
  return response.data;
};

export const authorizeOAuth = async (platform: Platform): Promise<{ authorization_url: string }> => {
  const response = await api.post(`/oauth/${platform}/authorize`);
  return response.data;
};

export const revokeOAuth = async (platform: Platform): Promise<void> => {
  await api.delete(`/oauth/${platform}`);
};

// Campaigns
export const getCampaigns = async (): Promise<Campaign[]> => {
  const response = await api.get('/campaigns');
  return response.data;
};

export const createCampaign = async (data: {
  objective: string;
  timeframe: string;
}): Promise<Campaign> => {
  const response = await api.post('/campaigns', data);
  return response.data;
};

// Tasks
export const getTasks = async (status?: string): Promise<Task[]> => {
  const params = status ? { status } : {};
  const response = await api.get('/tasks', { params });
  return response.data;
};

// Social Media
export const createLinkedInPost = async (data: {
  topic: string;
  style?: string;
  publish?: boolean;
}): Promise<Content> => {
  const response = await api.post('/social/linkedin/posts', data);
  return response.data;
};

export const createTwitterThread = async (data: {
  topic: string;
  thread_length?: number;
  publish?: boolean;
}): Promise<Content> => {
  const response = await api.post('/social/twitter/threads', data);
  return response.data;
};

export default api;
