import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Edit, Trash2, Check } from 'lucide-react';
import { getContent, deleteContent, approveContent } from '@/services/api';
import type { Content, ContentStatus } from '@/types';
import './ContentLibrary.css';

const ContentLibrary = () => {
  const [content, setContent] = useState<Content[]>([]);
  const [filteredContent, setFilteredContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ContentStatus | 'all'>('all');

  useEffect(() => {
    fetchContent();
  }, []);

  useEffect(() => {
    filterContent();
  }, [content, searchQuery, statusFilter]);

  const fetchContent = async () => {
    try {
      const data = await getContent();
      setContent(data);
    } catch (error) {
      console.error('Failed to fetch content:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterContent = () => {
    let filtered = content;

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter((item) => item.status === statusFilter);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (item) =>
          item.title.toLowerCase().includes(query) ||
          item.body.toLowerCase().includes(query)
      );
    }

    setFilteredContent(filtered);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this content?')) return;

    try {
      await deleteContent(id);
      setContent(content.filter((item) => item.id !== id));
    } catch (error) {
      console.error('Failed to delete content:', error);
      alert('Failed to delete content');
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await approveContent(id);
      setContent(
        content.map((item) =>
          item.id === id ? { ...item, status: 'approved' as ContentStatus } : item
        )
      );
    } catch (error) {
      console.error('Failed to approve content:', error);
      alert('Failed to approve content');
    }
  };

  if (loading) {
    return (
      <div className="content-loading">
        <div className="spinner"></div>
        <p>Loading content...</p>
      </div>
    );
  }

  return (
    <div className="content-library">
      <div className="library-header">
        <div>
          <h1>Content Library</h1>
          <p className="text-secondary">
            Manage all your marketing content in one place
          </p>
        </div>
        <Link to="/content/new" className="btn btn-primary">
          <Plus size={20} />
          Create New
        </Link>
      </div>

      {/* Filters */}
      <div className="filters-bar card">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <Filter size={16} />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as ContentStatus | 'all')}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="review">Review</option>
            <option value="approved">Approved</option>
            <option value="published">Published</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Content Grid */}
      {filteredContent.length > 0 ? (
        <div className="content-grid">
          {filteredContent.map((item) => (
            <div key={item.id} className="content-card card">
              <div className="content-card-header">
                <div className="content-type-badge badge badge-primary">
                  {item.type}
                </div>
                <span className={`status-badge badge badge-${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </div>

              <h3 className="content-card-title">{item.title}</h3>
              <p className="content-card-excerpt">
                {item.body.substring(0, 150)}...
              </p>

              <div className="content-card-meta">
                <span className="text-tertiary text-sm">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
                {item.brand_voice_score && (
                  <span className="score-badge">
                    Voice: {item.brand_voice_score}%
                  </span>
                )}
                {item.seo_score && (
                  <span className="score-badge">
                    SEO: {item.seo_score}%
                  </span>
                )}
              </div>

              <div className="content-card-actions">
                {item.status === 'review' && (
                  <button
                    onClick={() => handleApprove(item.id)}
                    className="btn btn-success btn-sm"
                    title="Approve"
                  >
                    <Check size={16} />
                  </button>
                )}
                <Link
                  to={`/content/${item.id}/edit`}
                  className="btn btn-secondary btn-sm"
                  title="Edit"
                >
                  <Edit size={16} />
                </Link>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="btn btn-danger btn-sm"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state card">
          <p>No content found</p>
          {searchQuery || statusFilter !== 'all' ? (
            <button
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('all');
              }}
              className="btn btn-secondary"
            >
              Clear Filters
            </button>
          ) : (
            <Link to="/content/new" className="btn btn-primary">
              <Plus size={20} />
              Create Your First Content
            </Link>
          )}
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

export default ContentLibrary;
