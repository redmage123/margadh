import { useState, useEffect } from 'react';
import {
  History,
  ChevronRight,
  RotateCcw,
  GitCompare,
  CheckCircle,
  Clock,
} from 'lucide-react';
import type { ContentVersion, ContentDiff } from '@/types/collaboration';
import {
  getVersions,
  restoreVersion,
  compareVersions,
} from '@/services/collaboration';
import { formatRelativeTime } from '@/types/collaboration';
import toast from 'react-hot-toast';
import './VersionHistory.css';

interface VersionHistoryProps {
  contentId: string;
  onRestore?: (version: ContentVersion) => void;
}

export const VersionHistory = ({ contentId, onRestore }: VersionHistoryProps) => {
  const [versions, setVersions] = useState<ContentVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
  const [compareMode, setCompareMode] = useState(false);
  const [diff, setDiff] = useState<ContentDiff[]>([]);
  const [showDiff, setShowDiff] = useState(false);

  useEffect(() => {
    fetchVersions();
  }, [contentId]);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      const data = await getVersions(contentId);
      setVersions(data);
    } catch (error) {
      console.error('Failed to fetch versions:', error);
      toast.error('Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionId: string) => {
    if (!confirm('Restore this version? This will create a new version based on the selected one.')) {
      return;
    }

    try {
      const restored = await restoreVersion(versionId);
      setVersions([restored, ...versions.map(v => ({ ...v, is_current: false }))]);
      toast.success('Version restored successfully');
      if (onRestore) {
        onRestore(restored);
      }
    } catch (error) {
      console.error('Failed to restore version:', error);
      toast.error('Failed to restore version');
    }
  };

  const handleVersionSelect = (versionId: string) => {
    if (!compareMode) {
      setCompareMode(true);
      setSelectedVersions([versionId]);
      return;
    }

    if (selectedVersions.includes(versionId)) {
      const newSelected = selectedVersions.filter(id => id !== versionId);
      setSelectedVersions(newSelected);
      if (newSelected.length === 0) {
        setCompareMode(false);
      }
    } else if (selectedVersions.length < 2) {
      setSelectedVersions([...selectedVersions, versionId]);
    } else {
      toast.error('You can only compare two versions at a time');
    }
  };

  const handleCompare = async () => {
    if (selectedVersions.length !== 2) {
      toast.error('Please select exactly two versions to compare');
      return;
    }

    try {
      const diffs = await compareVersions(selectedVersions[0], selectedVersions[1]);
      setDiff(diffs);
      setShowDiff(true);
    } catch (error) {
      console.error('Failed to compare versions:', error);
      toast.error('Failed to compare versions');
    }
  };

  const cancelCompare = () => {
    setCompareMode(false);
    setSelectedVersions([]);
    setShowDiff(false);
    setDiff([]);
  };

  if (loading) {
    return (
      <div className="version-history-loading">
        <History className="animate-spin" size={24} />
        <p>Loading version history...</p>
      </div>
    );
  }

  if (showDiff) {
    return (
      <div className="version-diff-view">
        <div className="diff-header">
          <h3>
            <GitCompare size={20} />
            Version Comparison
          </h3>
          <button onClick={cancelCompare} className="btn btn-secondary btn-sm">
            Close Comparison
          </button>
        </div>

        <div className="diff-versions-info">
          {selectedVersions.map(versionId => {
            const version = versions.find(v => v.id === versionId);
            if (!version) return null;
            return (
              <div key={versionId} className="diff-version-card">
                <div className="version-badge">v{version.version_number}</div>
                <div>
                  <div className="version-author">{version.created_by_name}</div>
                  <div className="version-time">
                    {formatRelativeTime(version.created_at)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="diff-content">
          {diff.length === 0 ? (
            <div className="diff-empty">
              <CheckCircle size={48} />
              <p>No differences found between these versions</p>
            </div>
          ) : (
            <div className="diff-list">
              {diff.map((d, index) => (
                <div key={index} className={`diff-item diff-${d.change_type}`}>
                  <div className="diff-field">{d.field}</div>
                  <div className="diff-changes">
                    {d.change_type === 'modified' && (
                      <>
                        <div className="diff-old">
                          <span className="diff-label">Old:</span>
                          <pre>{d.old_value}</pre>
                        </div>
                        <ChevronRight size={16} className="diff-arrow" />
                        <div className="diff-new">
                          <span className="diff-label">New:</span>
                          <pre>{d.new_value}</pre>
                        </div>
                      </>
                    )}
                    {d.change_type === 'added' && (
                      <div className="diff-new">
                        <span className="diff-label">Added:</span>
                        <pre>{d.new_value}</pre>
                      </div>
                    )}
                    {d.change_type === 'removed' && (
                      <div className="diff-old">
                        <span className="diff-label">Removed:</span>
                        <pre>{d.old_value}</pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="version-history">
      <div className="version-history-header">
        <h3 className="version-history-title">
          <History size={20} />
          Version History ({versions.length})
        </h3>
        {compareMode && (
          <div className="compare-actions">
            <span className="compare-status">
              {selectedVersions.length} version{selectedVersions.length !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={handleCompare}
              disabled={selectedVersions.length !== 2}
              className="btn btn-primary btn-sm"
            >
              <GitCompare size={16} />
              Compare
            </button>
            <button onClick={cancelCompare} className="btn btn-secondary btn-sm">
              Cancel
            </button>
          </div>
        )}
      </div>

      {versions.length === 0 ? (
        <div className="version-history-empty">
          <Clock size={48} />
          <p>No version history available</p>
        </div>
      ) : (
        <div className="version-list">
          {versions.map(version => (
            <VersionItem
              key={version.id}
              version={version}
              isSelected={selectedVersions.includes(version.id)}
              compareMode={compareMode}
              onSelect={handleVersionSelect}
              onRestore={handleRestore}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Version Item Component
interface VersionItemProps {
  version: ContentVersion;
  isSelected: boolean;
  compareMode: boolean;
  onSelect: (id: string) => void;
  onRestore: (id: string) => void;
}

const VersionItem = ({
  version,
  isSelected,
  compareMode,
  onSelect,
  onRestore,
}: VersionItemProps) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`version-item ${isSelected ? 'version-selected' : ''} ${
        version.is_current ? 'version-current' : ''
      }`}
    >
      <div className="version-header">
        {compareMode && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => onSelect(version.id)}
            className="version-checkbox"
          />
        )}

        <div className="version-badge">v{version.version_number}</div>

        <div className="version-info">
          <div className="version-meta">
            <span className="version-author">{version.created_by_name}</span>
            <span className="version-time">{formatRelativeTime(version.created_at)}</span>
            {version.is_current && (
              <span className="version-current-badge">
                <CheckCircle size={14} />
                Current
              </span>
            )}
          </div>

          {version.change_summary && (
            <div className="version-summary">{version.change_summary}</div>
          )}
        </div>

        <div className="version-actions">
          {!version.is_current && (
            <button
              onClick={() => onRestore(version.id)}
              className="version-action-btn"
              title="Restore this version"
            >
              <RotateCcw size={16} />
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="version-action-btn"
            title={expanded ? 'Collapse' : 'Expand'}
          >
            <ChevronRight
              size={16}
              className={expanded ? 'version-chevron-expanded' : ''}
            />
          </button>
        </div>
      </div>

      {expanded && (
        <div className="version-details">
          <div className="version-detail-section">
            <h4>Title</h4>
            <p>{version.title}</p>
          </div>

          <div className="version-detail-section">
            <h4>Content</h4>
            <div className="version-content-preview">
              {version.body.substring(0, 300)}
              {version.body.length > 300 && '...'}
            </div>
          </div>

          {version.metadata && Object.keys(version.metadata).length > 0 && (
            <div className="version-detail-section">
              <h4>Metadata</h4>
              <pre className="version-metadata">
                {JSON.stringify(version.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
