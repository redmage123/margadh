import { useState, useEffect } from 'react';
import {
  Check,
  X,
  RefreshCw,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  Linkedin,
  Twitter,
} from 'lucide-react';
import { getOAuthStatus, authorizeOAuth, revokeOAuth } from '@/services/api';
import type { OAuthIntegration, Platform } from '@/types';
import './OAuthSettings.css';

const OAuthSettings = () => {
  const [integrations, setIntegrations] = useState<Record<Platform, OAuthIntegration> | null>(null);
  const [loading, setLoading] = useState(true);
  const [processingPlatform, setProcessingPlatform] = useState<Platform | null>(null);

  useEffect(() => {
    fetchOAuthStatus();
  }, []);

  const fetchOAuthStatus = async () => {
    try {
      const data = await getOAuthStatus();
      setIntegrations(data);
    } catch (error) {
      console.error('Failed to fetch OAuth status:', error);
      // Initialize with default disconnected state
      setIntegrations({
        linkedin: {
          platform: 'linkedin',
          is_connected: false,
          expires_at: null,
        },
        twitter: {
          platform: 'twitter',
          is_connected: false,
          expires_at: null,
        },
        blog: {
          platform: 'blog',
          is_connected: false,
          expires_at: null,
        },
        email: {
          platform: 'email',
          is_connected: false,
          expires_at: null,
        },
      } as Record<Platform, OAuthIntegration>);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platform: Platform) => {
    setProcessingPlatform(platform);
    try {
      const { authorization_url } = await authorizeOAuth(platform);
      // Open authorization URL in new window
      window.open(authorization_url, '_blank', 'width=600,height=700');

      // Poll for connection status
      const pollInterval = setInterval(async () => {
        const data = await getOAuthStatus();
        if (data[platform].is_connected) {
          clearInterval(pollInterval);
          setIntegrations(data);
          setProcessingPlatform(null);
        }
      }, 2000);

      // Stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setProcessingPlatform(null);
      }, 300000);
    } catch (error) {
      console.error(`Failed to connect ${platform}:`, error);
      alert(`Failed to connect ${platform}`);
      setProcessingPlatform(null);
    }
  };

  const handleDisconnect = async (platform: Platform) => {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return;

    setProcessingPlatform(platform);
    try {
      await revokeOAuth(platform);
      await fetchOAuthStatus();
    } catch (error) {
      console.error(`Failed to disconnect ${platform}:`, error);
      alert(`Failed to disconnect ${platform}`);
    } finally {
      setProcessingPlatform(null);
    }
  };

  const getPlatformIcon = (platform: Platform) => {
    switch (platform) {
      case 'linkedin':
        return <Linkedin size={24} />;
      case 'twitter':
        return <Twitter size={24} />;
      default:
        return <ExternalLink size={24} />;
    }
  };

  const getPlatformColor = (platform: Platform): string => {
    const colors: Partial<Record<Platform, string>> = {
      linkedin: '#0077B5',
      twitter: '#1DA1F2',
      blog: '#667eea',
      email: '#764ba2',
    };
    return colors[platform] || '#667eea';
  };

  const isTokenExpiringSoon = (expiresAt: string | null): boolean => {
    if (!expiresAt) return false;
    const expiryDate = new Date(expiresAt);
    const now = new Date();
    const daysUntilExpiry = (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    return daysUntilExpiry < 7;
  };

  if (loading) {
    return (
      <div className="oauth-loading">
        <div className="spinner"></div>
        <p>Loading integrations...</p>
      </div>
    );
  }

  return (
    <div className="oauth-settings">
      <div className="oauth-header">
        <div>
          <h1>Platform Integrations</h1>
          <p className="text-secondary">
            Connect your social media accounts to publish content directly
          </p>
        </div>
        <button onClick={fetchOAuthStatus} className="btn btn-secondary">
          <RefreshCw size={16} />
          Refresh Status
        </button>
      </div>

      {/* Integration Cards */}
      <div className="integrations-grid">
        {integrations &&
          Object.entries(integrations).map(([platform, integration]) => {
            const platformKey = platform as Platform;
            const isProcessing = processingPlatform === platformKey;

            return (
              <div
                key={platform}
                className={`integration-card card ${
                  integration.is_connected ? 'connected' : 'disconnected'
                }`}
              >
                <div className="integration-header">
                  <div
                    className="platform-icon"
                    style={{ backgroundColor: getPlatformColor(platformKey) }}
                  >
                    {getPlatformIcon(platformKey)}
                  </div>
                  <div className="platform-info">
                    <h3 className="platform-name">
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </h3>
                    <div className="connection-status">
                      {integration.is_connected ? (
                        <>
                          <CheckCircle size={16} className="status-icon connected" />
                          <span className="status-text connected">Connected</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle size={16} className="status-icon disconnected" />
                          <span className="status-text disconnected">Not Connected</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {integration.is_connected && (
                  <div className="integration-details">
                    {integration.user_id && (
                      <div className="detail-row">
                        <span className="detail-label">User ID:</span>
                        <span className="detail-value">{integration.user_id}</span>
                      </div>
                    )}
                    {integration.expires_at && (
                      <div className="detail-row">
                        <span className="detail-label">Expires:</span>
                        <span
                          className={`detail-value ${
                            isTokenExpiringSoon(integration.expires_at) ? 'expiring-soon' : ''
                          }`}
                        >
                          {new Date(integration.expires_at).toLocaleDateString()}
                          {isTokenExpiringSoon(integration.expires_at) && (
                            <span className="badge badge-warning badge-sm ml-sm">
                              Expiring Soon
                            </span>
                          )}
                        </span>
                      </div>
                    )}
                    {integration.scopes && (
                      <div className="detail-row">
                        <span className="detail-label">Permissions:</span>
                        <div className="scopes-list">
                          {integration.scopes.map((scope, idx) => (
                            <span key={idx} className="badge badge-secondary badge-sm">
                              {scope}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="integration-actions">
                  {integration.is_connected ? (
                    <button
                      onClick={() => handleDisconnect(platformKey)}
                      disabled={isProcessing}
                      className="btn btn-danger btn-block"
                    >
                      <X size={16} />
                      {isProcessing ? 'Disconnecting...' : 'Disconnect'}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleConnect(platformKey)}
                      disabled={isProcessing}
                      className="btn btn-primary btn-block"
                    >
                      <Check size={16} />
                      {isProcessing ? 'Connecting...' : 'Connect'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
      </div>

      {/* Info Card */}
      <div className="card info-card">
        <div className="info-icon">
          <AlertCircle size={24} />
        </div>
        <div className="info-content">
          <h3>About Platform Integrations</h3>
          <ul>
            <li>
              <strong>LinkedIn:</strong> Post updates, articles, and engage with your
              professional network
            </li>
            <li>
              <strong>Twitter:</strong> Share tweets and threads to reach a wider audience
            </li>
            <li>
              <strong>Blog:</strong> Publish long-form content directly to your company blog
            </li>
            <li>
              <strong>Email:</strong> Send newsletters and campaigns to your subscriber list
            </li>
          </ul>
          <p className="info-note">
            <strong>Security:</strong> All tokens are encrypted and stored securely. We only
            request the minimum permissions needed to publish content on your behalf.
          </p>
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="card troubleshooting-card">
        <h3>Troubleshooting</h3>
        <div className="troubleshooting-content">
          <div className="troubleshooting-item">
            <h4>Connection failed?</h4>
            <p>
              Make sure pop-ups are enabled in your browser. If the authorization window was
              blocked, click the Connect button again.
            </p>
          </div>
          <div className="troubleshooting-item">
            <h4>Token expired?</h4>
            <p>
              Simply disconnect and reconnect to refresh your access token. The system will
              automatically attempt to refresh tokens before they expire.
            </p>
          </div>
          <div className="troubleshooting-item">
            <h4>Missing permissions?</h4>
            <p>
              Disconnect and reconnect to grant additional permissions. Make sure to approve
              all requested scopes during authorization.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OAuthSettings;
