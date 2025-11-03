/**
 * Advanced Analytics Service
 * Calculates comprehensive metrics from content data
 */

import type { Content, Platform, ContentType } from '@/types';

export interface AnalyticsSummary {
  // Overall metrics
  totalContent: number;
  totalPublished: number;
  totalDrafts: number;
  totalInReview: number;
  totalApproved: number;

  // Engagement metrics
  totalViews: number;
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  totalImpressions: number;
  avgEngagementRate: number;

  // Performance metrics
  totalEngagements: number;
  bestPerformingContent: Content | null;
  worstPerformingContent: Content | null;

  // Time-based metrics
  publishedThisWeek: number;
  publishedThisMonth: number;
  publishedLastWeek: number;
  weekOverWeekGrowth: number;

  // Quality metrics
  avgBrandVoiceScore: number;
  avgSeoScore: number;
}

export interface PlatformAnalytics {
  platform: Platform;
  contentCount: number;
  publishedCount: number;
  totalViews: number;
  totalEngagements: number;
  avgEngagementRate: number;
  topContent: Content | null;
}

export interface ContentTypeAnalytics {
  type: ContentType;
  count: number;
  avgEngagementRate: number;
  totalViews: number;
  totalEngagements: number;
}

export interface TimeSeriesData {
  date: string;
  views: number;
  engagements: number;
  content: number;
}

export interface PerformanceInsight {
  type: 'success' | 'warning' | 'info';
  title: string;
  message: string;
  action?: string;
}

/**
 * Calculate comprehensive analytics summary
 */
export function calculateAnalyticsSummary(content: Content[]): AnalyticsSummary {
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
  const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  // Status counts
  const totalDrafts = content.filter(c => c.status === 'draft').length;
  const totalInReview = content.filter(c => c.status === 'review').length;
  const totalApproved = content.filter(c => c.status === 'approved').length;
  const publishedContent = content.filter(c => c.status === 'published');

  // Time-based counts
  const publishedThisWeek = publishedContent.filter(c =>
    new Date(c.published_at || c.created_at) >= oneWeekAgo
  ).length;

  const publishedLastWeek = publishedContent.filter(c => {
    const date = new Date(c.published_at || c.created_at);
    return date >= twoWeeksAgo && date < oneWeekAgo;
  }).length;

  const publishedThisMonth = publishedContent.filter(c =>
    new Date(c.published_at || c.created_at) >= oneMonthAgo
  ).length;

  // Engagement metrics
  let totalViews = 0;
  let totalLikes = 0;
  let totalComments = 0;
  let totalShares = 0;
  let totalImpressions = 0;
  let engagementRateSum = 0;
  let engagementRateCount = 0;

  let bestContent: Content | null = null;
  let bestEngagement = 0;
  let worstContent: Content | null = null;
  let worstEngagement = Infinity;

  publishedContent.forEach(c => {
    if (c.analytics) {
      totalViews += c.analytics.views || 0;
      totalLikes += c.analytics.likes || 0;
      totalComments += c.analytics.comments || 0;
      totalShares += c.analytics.shares || 0;
      totalImpressions += c.analytics.impressions || 0;

      if (c.analytics.engagement_rate !== undefined) {
        engagementRateSum += c.analytics.engagement_rate;
        engagementRateCount++;
      }

      const engagements = (c.analytics.likes || 0) + (c.analytics.comments || 0) + (c.analytics.shares || 0);
      if (engagements > bestEngagement) {
        bestEngagement = engagements;
        bestContent = c;
      }
      if (engagements < worstEngagement && engagements > 0) {
        worstEngagement = engagements;
        worstContent = c;
      }
    }
  });

  // Quality scores
  const contentWithBrandVoice = content.filter(c => c.brand_voice_score !== undefined);
  const avgBrandVoiceScore = contentWithBrandVoice.length > 0
    ? contentWithBrandVoice.reduce((sum, c) => sum + (c.brand_voice_score || 0), 0) / contentWithBrandVoice.length
    : 0;

  const contentWithSeo = content.filter(c => c.seo_score !== undefined);
  const avgSeoScore = contentWithSeo.length > 0
    ? contentWithSeo.reduce((sum, c) => sum + (c.seo_score || 0), 0) / contentWithSeo.length
    : 0;

  // Calculate week-over-week growth
  const weekOverWeekGrowth = publishedLastWeek > 0
    ? ((publishedThisWeek - publishedLastWeek) / publishedLastWeek) * 100
    : publishedThisWeek > 0 ? 100 : 0;

  return {
    totalContent: content.length,
    totalPublished: publishedContent.length,
    totalDrafts,
    totalInReview,
    totalApproved,
    totalViews,
    totalLikes,
    totalComments,
    totalShares,
    totalImpressions,
    avgEngagementRate: engagementRateCount > 0 ? engagementRateSum / engagementRateCount : 0,
    totalEngagements: totalLikes + totalComments + totalShares,
    bestPerformingContent: bestContent,
    worstPerformingContent: worstContent,
    publishedThisWeek,
    publishedThisMonth,
    publishedLastWeek,
    weekOverWeekGrowth,
    avgBrandVoiceScore,
    avgSeoScore,
  };
}

/**
 * Calculate analytics by platform
 */
export function calculatePlatformAnalytics(content: Content[]): PlatformAnalytics[] {
  const platforms: Platform[] = ['linkedin', 'twitter', 'blog', 'email'];

  return platforms.map(platform => {
    const platformContent = content.filter(c => c.platform === platform);
    const publishedContent = platformContent.filter(c => c.status === 'published');

    let totalViews = 0;
    let totalEngagements = 0;
    let engagementRateSum = 0;
    let engagementRateCount = 0;
    let topContent: Content | null = null;
    let maxEngagement = 0;

    publishedContent.forEach(c => {
      if (c.analytics) {
        totalViews += c.analytics.views || 0;
        const engagements = (c.analytics.likes || 0) + (c.analytics.comments || 0) + (c.analytics.shares || 0);
        totalEngagements += engagements;

        if (c.analytics.engagement_rate !== undefined) {
          engagementRateSum += c.analytics.engagement_rate;
          engagementRateCount++;
        }

        if (engagements > maxEngagement) {
          maxEngagement = engagements;
          topContent = c;
        }
      }
    });

    return {
      platform,
      contentCount: platformContent.length,
      publishedCount: publishedContent.length,
      totalViews,
      totalEngagements,
      avgEngagementRate: engagementRateCount > 0 ? engagementRateSum / engagementRateCount : 0,
      topContent,
    };
  });
}

/**
 * Calculate analytics by content type
 */
export function calculateContentTypeAnalytics(content: Content[]): ContentTypeAnalytics[] {
  const types: ContentType[] = ['blog', 'social', 'email', 'whitepaper', 'case_study'];

  return types.map(type => {
    const typeContent = content.filter(c => c.type === type && c.status === 'published');

    let totalViews = 0;
    let totalEngagements = 0;
    let engagementRateSum = 0;
    let engagementRateCount = 0;

    typeContent.forEach(c => {
      if (c.analytics) {
        totalViews += c.analytics.views || 0;
        totalEngagements += (c.analytics.likes || 0) + (c.analytics.comments || 0) + (c.analytics.shares || 0);

        if (c.analytics.engagement_rate !== undefined) {
          engagementRateSum += c.analytics.engagement_rate;
          engagementRateCount++;
        }
      }
    });

    return {
      type,
      count: typeContent.length,
      avgEngagementRate: engagementRateCount > 0 ? engagementRateSum / engagementRateCount : 0,
      totalViews,
      totalEngagements,
    };
  }).filter(t => t.count > 0);
}

/**
 * Generate time series data for the last 30 days
 */
export function generateTimeSeriesData(content: Content[]): TimeSeriesData[] {
  const days: TimeSeriesData[] = [];
  const now = new Date();

  for (let i = 29; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];

    const dayContent = content.filter(c => {
      const contentDate = new Date(c.published_at || c.created_at);
      return contentDate.toISOString().split('T')[0] === dateStr;
    });

    let views = 0;
    let engagements = 0;

    dayContent.forEach(c => {
      if (c.analytics) {
        views += c.analytics.views || 0;
        engagements += (c.analytics.likes || 0) + (c.analytics.comments || 0) + (c.analytics.shares || 0);
      }
    });

    days.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      views,
      engagements,
      content: dayContent.length,
    });
  }

  return days;
}

/**
 * Generate AI-powered insights
 */
export function generateInsights(
  summary: AnalyticsSummary,
  platformAnalytics: PlatformAnalytics[],
  typeAnalytics: ContentTypeAnalytics[]
): PerformanceInsight[] {
  const insights: PerformanceInsight[] = [];

  // Week-over-week growth insight
  if (summary.weekOverWeekGrowth > 20) {
    insights.push({
      type: 'success',
      title: 'Strong Growth Momentum',
      message: `Publishing is up ${summary.weekOverWeekGrowth.toFixed(0)}% this week. Keep up the great work!`,
    });
  } else if (summary.weekOverWeekGrowth < -20) {
    insights.push({
      type: 'warning',
      title: 'Publishing Slowdown',
      message: `Publishing is down ${Math.abs(summary.weekOverWeekGrowth).toFixed(0)}% this week. Consider increasing output.`,
      action: 'Schedule more content',
    });
  }

  // Content in review insight
  if (summary.totalInReview > 5) {
    insights.push({
      type: 'warning',
      title: 'Review Bottleneck',
      message: `${summary.totalInReview} pieces awaiting review. Speed up approvals to maintain publishing cadence.`,
      action: 'Review pending content',
    });
  }

  // Best platform insight
  const bestPlatform = platformAnalytics.reduce((best, current) =>
    current.avgEngagementRate > best.avgEngagementRate ? current : best
  );
  if (bestPlatform.avgEngagementRate > 0) {
    insights.push({
      type: 'success',
      title: `${bestPlatform.platform.charAt(0).toUpperCase() + bestPlatform.platform.slice(1)} is Winning`,
      message: `${bestPlatform.avgEngagementRate.toFixed(1)}% avg engagement rate. Consider focusing more content here.`,
    });
  }

  // Quality scores insight
  if (summary.avgBrandVoiceScore > 0 && summary.avgBrandVoiceScore < 70) {
    insights.push({
      type: 'warning',
      title: 'Brand Voice Needs Attention',
      message: `Average brand voice score is ${summary.avgBrandVoiceScore.toFixed(0)}%. Review brand guidelines.`,
      action: 'Improve brand alignment',
    });
  }

  if (summary.avgSeoScore > 0 && summary.avgSeoScore < 70) {
    insights.push({
      type: 'info',
      title: 'SEO Optimization Opportunity',
      message: `Average SEO score is ${summary.avgSeoScore.toFixed(0)}%. Focus on keywords and structure.`,
      action: 'Optimize for SEO',
    });
  }

  // Content type performance
  const bestType = typeAnalytics.reduce((best, current) =>
    current.avgEngagementRate > best.avgEngagementRate ? current : best
  , typeAnalytics[0]);

  if (bestType && bestType.avgEngagementRate > 0) {
    const typeLabel = bestType.type === 'case_study' ? 'Case Studies' :
                      bestType.type === 'social' ? 'Social Posts' :
                      bestType.type.charAt(0).toUpperCase() + bestType.type.slice(1) + 's';
    insights.push({
      type: 'info',
      title: `${typeLabel} Performing Well`,
      message: `${bestType.avgEngagementRate.toFixed(1)}% engagement rate. Create more ${typeLabel.toLowerCase()}.`,
    });
  }

  // Draft accumulation insight
  if (summary.totalDrafts > summary.totalPublished * 0.5) {
    insights.push({
      type: 'warning',
      title: 'Too Many Drafts',
      message: `${summary.totalDrafts} drafts are piling up. Review and publish or archive.`,
      action: 'Review drafts',
    });
  }

  return insights;
}

/**
 * Calculate ROI score for content
 * Based on engagement relative to content type and platform averages
 */
export function calculateROIScore(content: Content, platformAvg: number, typeAvg: number): number {
  if (!content.analytics) return 0;

  const engagements = (content.analytics.likes || 0) +
                     (content.analytics.comments || 0) +
                     (content.analytics.shares || 0);

  const views = content.analytics.views || 1;
  const contentEngagementRate = (engagements / views) * 100;

  // Score based on performance vs. averages
  let score = 50; // baseline

  if (contentEngagementRate > platformAvg * 1.5) score += 25;
  else if (contentEngagementRate > platformAvg) score += 15;
  else if (contentEngagementRate < platformAvg * 0.5) score -= 25;
  else if (contentEngagementRate < platformAvg) score -= 15;

  if (contentEngagementRate > typeAvg * 1.5) score += 25;
  else if (contentEngagementRate > typeAvg) score += 15;
  else if (contentEngagementRate < typeAvg * 0.5) score -= 25;
  else if (contentEngagementRate < typeAvg) score -= 15;

  return Math.max(0, Math.min(100, score));
}
