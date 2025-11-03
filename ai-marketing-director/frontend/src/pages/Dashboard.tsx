import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  FileText,
  Eye,
  Heart,
  AlertCircle,
  Plus,
  ThumbsUp,
  MessageCircle,
  Share2,
  Target,
  Lightbulb,
  ArrowUp,
  ArrowDown,
  Award,
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { getContent } from '@/services/api';
import type { Content } from '@/types';
import {
  calculateAnalyticsSummary,
  calculatePlatformAnalytics,
  calculateContentTypeAnalytics,
  generateTimeSeriesData,
  generateInsights,
} from '@/services/analytics';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import { ErrorState } from '@/components/ErrorState';
import './Dashboard.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const contentData = await getContent();
      setContent(contentData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard analytics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Calculate all analytics using the new service
  const analytics = useMemo(() => calculateAnalyticsSummary(content), [content]);
  const platformAnalytics = useMemo(() => calculatePlatformAnalytics(content), [content]);
  const typeAnalytics = useMemo(() => calculateContentTypeAnalytics(content), [content]);
  const timeSeriesData = useMemo(() => generateTimeSeriesData(content), [content]);
  const insights = useMemo(() =>
    generateInsights(analytics, platformAnalytics, typeAnalytics),
    [analytics, platformAnalytics, typeAnalytics]
  );

  const recentContent = useMemo(() =>
    content
      .filter(c => c.status === 'published')
      .sort((a, b) => new Date(b.published_at || b.created_at).getTime() -
                      new Date(a.published_at || a.created_at).getTime())
      .slice(0, 5),
    [content]
  );

  const topPerformingContent = useMemo(() =>
    content
      .filter(c => c.status === 'published' && c.analytics)
      .sort((a, b) => {
        const aEngagement = (a.analytics?.likes || 0) + (a.analytics?.comments || 0) + (a.analytics?.shares || 0);
        const bEngagement = (b.analytics?.likes || 0) + (b.analytics?.comments || 0) + (b.analytics?.shares || 0);
        return bEngagement - aEngagement;
      })
      .slice(0, 5),
    [content]
  );

  // Real-time chart data
  const performanceOverTimeData = {
    labels: timeSeriesData.map(d => d.date),
    datasets: [
      {
        label: 'Views',
        data: timeSeriesData.map(d => d.views),
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
      },
      {
        label: 'Engagements',
        data: timeSeriesData.map(d => d.engagements),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
      },
    ],
  };

  const platformPerformanceData = {
    labels: platformAnalytics.map(p => p.platform.charAt(0).toUpperCase() + p.platform.slice(1)),
    datasets: [
      {
        label: 'Content Count',
        data: platformAnalytics.map(p => p.contentCount),
        backgroundColor: 'rgba(102, 126, 234, 0.8)',
        borderColor: 'rgb(102, 126, 234)',
        borderWidth: 2,
      },
      {
        label: 'Avg Engagement %',
        data: platformAnalytics.map(p => p.avgEngagementRate),
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 2,
      },
    ],
  };

  const contentByTypeData = {
    labels: typeAnalytics.map(t => t.type.charAt(0).toUpperCase() + t.type.slice(1)),
    datasets: [
      {
        data: typeAnalytics.map(t => t.count),
        backgroundColor: [
          'rgba(102, 126, 234, 0.8)',
          'rgba(29, 161, 242, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
        borderColor: [
          'rgb(102, 126, 234)',
          'rgb(29, 161, 242)',
          'rgb(245, 158, 11)',
          'rgb(16, 185, 129)',
          'rgb(139, 92, 246)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleColor: '#fff',
        bodyColor: '#fff',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: number | string) => {
            if (typeof value === 'number' && value >= 1000) {
              return (value / 1000).toFixed(1) + 'k';
            }
            return value;
          },
        },
      },
    },
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to Load Dashboard"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Analytics Dashboard</h1>
          <p className="text-secondary">Comprehensive performance insights and metrics</p>
        </div>
        <Link to="/content/new" className="btn btn-primary">
          <Plus size={20} />
          Create Content
        </Link>
      </div>

      {/* Key Performance Indicators */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <FileText className="metric-icon" size={24} />
            {analytics.weekOverWeekGrowth !== 0 && (
              <span className={`badge ${analytics.weekOverWeekGrowth > 0 ? 'badge-success' : 'badge-error'}`}>
                {analytics.weekOverWeekGrowth > 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                {Math.abs(analytics.weekOverWeekGrowth).toFixed(0)}%
              </span>
            )}
          </div>
          <div className="metric-value">{analytics.totalPublished}</div>
          <div className="metric-label">Published Content</div>
          <div className="metric-sublabel">
            {analytics.publishedThisWeek} this week
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Eye className="metric-icon" size={24} />
            <span className="badge badge-info">Total</span>
          </div>
          <div className="metric-value">
            {analytics.totalViews >= 1000
              ? `${(analytics.totalViews / 1000).toFixed(1)}k`
              : analytics.totalViews}
          </div>
          <div className="metric-label">Total Views</div>
          <div className="metric-sublabel">
            {analytics.totalImpressions > 0 && `${(analytics.totalImpressions / 1000).toFixed(1)}k impressions`}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Heart className="metric-icon" size={24} />
            <span className="badge badge-primary">Avg</span>
          </div>
          <div className="metric-value">
            {analytics.avgEngagementRate.toFixed(1)}%
          </div>
          <div className="metric-label">Engagement Rate</div>
          <div className="metric-sublabel">
            {analytics.totalEngagements.toLocaleString()} total engagements
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <ThumbsUp className="metric-icon" size={24} />
            <span className="badge badge-success">Social</span>
          </div>
          <div className="metric-value">
            {analytics.totalLikes + analytics.totalComments + analytics.totalShares >= 1000
              ? `${((analytics.totalLikes + analytics.totalComments + analytics.totalShares) / 1000).toFixed(1)}k`
              : analytics.totalLikes + analytics.totalComments + analytics.totalShares}
          </div>
          <div className="metric-label">Social Interactions</div>
          <div className="metric-sublabel">
            {analytics.totalLikes} likes · {analytics.totalComments} comments · {analytics.totalShares} shares
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Target className="metric-icon" size={24} />
            <span className="badge badge-info">Quality</span>
          </div>
          <div className="metric-value">
            {analytics.avgBrandVoiceScore > 0 ? analytics.avgBrandVoiceScore.toFixed(0) : 'N/A'}
          </div>
          <div className="metric-label">Brand Voice Score</div>
          <div className="metric-sublabel">
            SEO: {analytics.avgSeoScore > 0 ? analytics.avgSeoScore.toFixed(0) : 'N/A'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <AlertCircle className="metric-icon" size={24} />
            {analytics.totalInReview > 5 && (
              <span className="badge badge-warning">Action</span>
            )}
          </div>
          <div className="metric-value">{analytics.totalInReview}</div>
          <div className="metric-label">Pending Review</div>
          <div className="metric-sublabel">
            {analytics.totalDrafts} drafts · {analytics.totalApproved} approved
          </div>
        </div>
      </div>

      {/* AI-Powered Insights */}
      {insights.length > 0 && (
        <div className="insights-section">
          <h2 className="section-title">
            <Lightbulb size={24} />
            AI-Powered Insights
          </h2>
          <div className="insights-grid">
            {insights.map((insight, index) => (
              <div key={index} className={`insight-card insight-${insight.type}`}>
                <div className="insight-header">
                  {insight.type === 'success' && <Award size={20} />}
                  {insight.type === 'warning' && <AlertCircle size={20} />}
                  {insight.type === 'info' && <Lightbulb size={20} />}
                  <h4>{insight.title}</h4>
                </div>
                <p className="insight-message">{insight.message}</p>
                {insight.action && (
                  <button className="btn btn-sm btn-secondary">
                    {insight.action}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Charts */}
      <div className="charts-grid">
        <div className="card chart-card chart-card-large">
          <div className="card-header">
            <h3 className="card-title">Performance Over Time (30 Days)</h3>
          </div>
          <div className="chart-container">
            <Line data={performanceOverTimeData} options={lineChartOptions} />
          </div>
        </div>

        <div className="card chart-card">
          <div className="card-header">
            <h3 className="card-title">Platform Performance</h3>
          </div>
          <div className="chart-container">
            <Bar data={platformPerformanceData} options={barChartOptions} />
          </div>
        </div>

        {typeAnalytics.length > 0 && (
          <div className="card chart-card">
            <div className="card-header">
              <h3 className="card-title">Content by Type</h3>
            </div>
            <div className="chart-container">
              <Doughnut data={contentByTypeData} options={doughnutOptions} />
            </div>
          </div>
        )}
      </div>

      {/* Platform Breakdown */}
      <div className="platform-analytics">
        <h2 className="section-title">
          <TrendingUp size={24} />
          Platform Breakdown
        </h2>
        <div className="platform-grid">
          {platformAnalytics.map((platform) => (
            <div key={platform.platform} className="platform-card card">
              <div className="platform-header">
                <h4 className="platform-name">
                  {platform.platform.charAt(0).toUpperCase() + platform.platform.slice(1)}
                </h4>
                <span className={`badge ${platform.publishedCount > 0 ? 'badge-success' : 'badge-secondary'}`}>
                  {platform.publishedCount} published
                </span>
              </div>
              <div className="platform-stats">
                <div className="stat-row">
                  <span className="stat-label">
                    <Eye size={16} />
                    Views
                  </span>
                  <span className="stat-value">{platform.totalViews.toLocaleString()}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">
                    <Heart size={16} />
                    Engagements
                  </span>
                  <span className="stat-value">{platform.totalEngagements.toLocaleString()}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">
                    <TrendingUp size={16} />
                    Engagement Rate
                  </span>
                  <span className="stat-value">{platform.avgEngagementRate.toFixed(1)}%</span>
                </div>
                {platform.topContent && (
                  <div className="platform-top-content">
                    <p className="text-xs text-secondary">Top Performer:</p>
                    <Link
                      to={`/content/${platform.topContent.id}/edit`}
                      className="top-content-link"
                    >
                      {platform.topContent.title}
                    </Link>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Performing Content */}
      {topPerformingContent.length > 0 && (
        <div className="top-performers-section">
          <h2 className="section-title">
            <Award size={24} />
            Top Performing Content
          </h2>
          <div className="card">
            <div className="performance-list">
              {topPerformingContent.map((item, index) => {
                const engagementRate = item.analytics?.engagement_rate || 0;

                return (
                  <div key={item.id} className="performance-item">
                    <div className="performance-rank">#{index + 1}</div>
                    <div className="performance-info">
                      <h4 className="performance-title">
                        <Link to={`/content/${item.id}/edit`}>
                          {item.title}
                        </Link>
                      </h4>
                      <div className="performance-meta">
                        <span className="badge badge-primary">{item.type}</span>
                        {item.platform && (
                          <span className="badge badge-secondary">{item.platform}</span>
                        )}
                        <span className="text-secondary">
                          {new Date(item.published_at || item.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="performance-stats">
                      <div className="stat-mini">
                        <Eye size={14} />
                        <span>{(item.analytics?.views || 0).toLocaleString()}</span>
                      </div>
                      <div className="stat-mini">
                        <ThumbsUp size={14} />
                        <span>{(item.analytics?.likes || 0).toLocaleString()}</span>
                      </div>
                      <div className="stat-mini">
                        <MessageCircle size={14} />
                        <span>{(item.analytics?.comments || 0).toLocaleString()}</span>
                      </div>
                      <div className="stat-mini">
                        <Share2 size={14} />
                        <span>{(item.analytics?.shares || 0).toLocaleString()}</span>
                      </div>
                      <div className="stat-mini highlight">
                        <Heart size={14} />
                        <span>{engagementRate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Recent Content */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Published Content</h3>
          <Link to="/content" className="btn btn-secondary btn-sm">
            View All
          </Link>
        </div>
        <div className="content-list">
          {recentContent.length > 0 ? (
            recentContent.map((item) => (
              <div key={item.id} className="content-item">
                <div className="content-info">
                  <h4 className="content-title">{item.title}</h4>
                  <div className="content-meta">
                    <span className={`badge badge-${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                    <span className="badge badge-secondary">{item.type}</span>
                    {item.platform && (
                      <span className="badge badge-info">{item.platform}</span>
                    )}
                    <span className="text-tertiary">
                      {new Date(item.published_at || item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <Link
                  to={`/content/${item.id}/edit`}
                  className="btn btn-secondary btn-sm"
                >
                  View
                </Link>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <FileText size={48} />
              <p>No published content yet. Create and publish your first piece!</p>
              <Link to="/content/new" className="btn btn-primary">
                <Plus size={20} />
                Create Content
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Action Items */}
      {analytics.totalInReview > 0 && (
        <div className="card alert-card">
          <div className="alert-icon">
            <AlertCircle size={24} />
          </div>
          <div className="alert-content">
            <h4>Action Required</h4>
            <p>
              You have {analytics.totalInReview} content piece{analytics.totalInReview > 1 ? 's' : ''} awaiting review.
              {analytics.totalDrafts > 10 && ` Plus ${analytics.totalDrafts} drafts that need attention.`}
            </p>
          </div>
          <Link to="/content?status=review" className="btn btn-primary">
            Review Now
          </Link>
        </div>
      )}
    </div>
  );
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    draft: 'info',
    review: 'warning',
    approved: 'success',
    published: 'primary',
    rejected: 'error',
  };
  return colors[status] || 'info';
};

export default Dashboard;
