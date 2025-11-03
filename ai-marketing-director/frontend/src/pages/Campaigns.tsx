import { useState, useEffect } from 'react';
import { Plus, Calendar, Target, TrendingUp, Users, Clock } from 'lucide-react';
import { getCampaigns, createCampaign } from '@/services/api';
import type { Campaign } from '@/types';
import './Campaigns.css';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);

  const [newCampaign, setNewCampaign] = useState({
    objective: '',
    timeframe: '',
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const data = await getCampaigns();
      setCampaigns(data);
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newCampaign.objective || !newCampaign.timeframe) {
      alert('Please fill in all fields');
      return;
    }

    setCreating(true);
    try {
      await createCampaign(newCampaign);
      setShowCreateModal(false);
      setNewCampaign({ objective: '', timeframe: '' });
      await fetchCampaigns();
    } catch (error) {
      console.error('Failed to create campaign:', error);
      alert('Failed to create campaign');
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      planning: 'info',
      active: 'success',
      paused: 'warning',
      completed: 'primary',
      cancelled: 'error',
    };
    return colors[status] || 'info';
  };

  if (loading) {
    return (
      <div className="campaigns-loading">
        <div className="spinner"></div>
        <p>Loading campaigns...</p>
      </div>
    );
  }

  return (
    <div className="campaigns">
      <div className="campaigns-header">
        <div>
          <h1>Marketing Campaigns</h1>
          <p className="text-secondary">Plan and manage your marketing campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <Plus size={20} />
          Create Campaign
        </button>
      </div>

      {/* Campaign Stats */}
      {campaigns.length > 0 && (
        <div className="campaign-stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(102, 126, 234, 0.1)' }}>
              <Target size={24} style={{ color: 'var(--primary)' }} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{campaigns.length}</div>
              <div className="stat-label">Total Campaigns</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
              <TrendingUp size={24} style={{ color: 'var(--success)' }} />
            </div>
            <div className="stat-content">
              <div className="stat-value">
                {campaigns.filter((c) => c.status === 'active').length}
              </div>
              <div className="stat-label">Active</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
              <Clock size={24} style={{ color: 'var(--warning)' }} />
            </div>
            <div className="stat-content">
              <div className="stat-value">
                {campaigns.filter((c) => c.status === 'planning').length}
              </div>
              <div className="stat-label">Planning</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(102, 126, 234, 0.1)' }}>
              <Users size={24} style={{ color: 'var(--primary)' }} />
            </div>
            <div className="stat-content">
              <div className="stat-value">
                {campaigns.reduce((sum, c) => sum + (c.content_pieces?.length || 0), 0)}
              </div>
              <div className="stat-label">Content Pieces</div>
            </div>
          </div>
        </div>
      )}

      {/* Campaigns List */}
      {campaigns.length > 0 ? (
        <div className="campaigns-list">
          {campaigns.map((campaign) => (
            <div key={campaign.id} className="campaign-card card">
              <div className="campaign-header">
                <div className="campaign-title-section">
                  <h3 className="campaign-title">{campaign.objective}</h3>
                  <span className={`badge badge-${getStatusColor(campaign.status)}`}>
                    {campaign.status}
                  </span>
                </div>
                {campaign.timeframe && (
                  <div className="campaign-date">
                    <Calendar size={16} />
                    <span>{campaign.timeframe}</span>
                  </div>
                )}
              </div>

              {campaign.content_pieces && campaign.content_pieces.length > 0 && (
                <div className="campaign-content">
                  <h4 className="content-section-title">Content Pieces</h4>
                  <div className="content-pieces-grid">
                    {campaign.content_pieces.map((piece, idx) => (
                      <div key={idx} className="content-piece-chip">
                        <span className="badge badge-secondary badge-sm">
                          {piece.type}
                        </span>
                        <span className="content-piece-title">{piece.title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {campaign.tasks && campaign.tasks.length > 0 && (
                <div className="campaign-tasks">
                  <h4 className="tasks-section-title">Tasks</h4>
                  <div className="tasks-list">
                    {campaign.tasks.map((task, idx) => (
                      <div key={idx} className="task-item">
                        <div className="task-checkbox">
                          <input
                            type="checkbox"
                            checked={task.status === 'completed'}
                            readOnly
                          />
                        </div>
                        <span className="task-description">{task.description}</span>
                        <span className={`badge badge-${getStatusColor(task.status)} badge-sm`}>
                          {task.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="campaign-footer">
                <div className="campaign-meta">
                  <span className="text-tertiary text-sm">
                    Created {new Date(campaign.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="campaign-actions">
                  <button className="btn btn-secondary btn-sm">View Details</button>
                  <button className="btn btn-primary btn-sm">Edit</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state card">
          <Target size={48} className="empty-icon" />
          <h3>No campaigns yet</h3>
          <p>Create your first marketing campaign to get started</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary"
          >
            <Plus size={20} />
            Create Campaign
          </button>
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Campaign</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn btn-secondary btn-sm"
              >
                Cancel
              </button>
            </div>

            <form onSubmit={handleCreateCampaign} className="modal-content">
              <div className="form-group">
                <label htmlFor="objective">Campaign Objective</label>
                <input
                  type="text"
                  id="objective"
                  value={newCampaign.objective}
                  onChange={(e) =>
                    setNewCampaign({ ...newCampaign, objective: e.target.value })
                  }
                  placeholder="e.g., Launch new AI product, Q1 lead generation"
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="timeframe">Timeframe</label>
                <input
                  type="text"
                  id="timeframe"
                  value={newCampaign.timeframe}
                  onChange={(e) =>
                    setNewCampaign({ ...newCampaign, timeframe: e.target.value })
                  }
                  placeholder="e.g., Q1 2024, Jan - Mar 2024"
                  className="form-control"
                  required
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="btn btn-primary"
                >
                  {creating ? 'Creating...' : 'Create Campaign'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Campaigns;
