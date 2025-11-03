import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Save,
  Send,
  Eye,
  Sparkles,
  AlertCircle,
  CheckCircle,
  TrendingUp,
  ArrowLeft,
} from 'lucide-react';
import {
  getContentById,
  createContent,
  updateContent,
  generateContent,
} from '@/services/api';
import type { ContentType, ContentStatus, Platform } from '@/types';
import { ErrorState } from '@/components/ErrorState';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import './ContentEditor.css';

const ContentEditor = () => {
  const { id } = useParams<{ id: string}>();
  const navigate = useNavigate();
  const isEditMode = id !== undefined && id !== 'new';

  const [loading, setLoading] = useState(isEditMode);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const autosaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    type: 'blog' as ContentType,
    platform: 'linkedin' as Platform,
    body: '',
    metadata: {
      target_audience: '',
      keywords: '',
      cta: '',
    },
  });

  const [scores, setScores] = useState({
    brand_voice_score: null as number | null,
    seo_score: null as number | null,
  });

  useEffect(() => {
    if (isEditMode) {
      fetchContent();
    }
  }, [id]);

  const fetchContent = async () => {
    try {
      const content = await getContentById(id!);
      setFormData({
        title: content.title,
        type: content.type,
        platform: (content.platform || 'linkedin') as Platform,
        body: content.body,
        metadata: {
          target_audience: content.metadata?.target_audience || '',
          keywords: content.metadata?.keywords || '',
          cta: content.metadata?.cta || '',
        },
      });
      setScores({
        brand_voice_score: content.brand_voice_score || null,
        seo_score: content.seo_score || null,
      });
      setError(null);
    } catch (error) {
      console.error('Failed to fetch content:', error);
      setError('Failed to load content. Please try again.');
      toast.error('Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  // Autosave function
  const autoSave = useCallback(async () => {
    if (!isEditMode || !formData.title || !formData.body) {
      return;
    }

    try {
      const contentData = {
        ...formData,
        status: 'draft' as ContentStatus,
        brand_voice_score: scores.brand_voice_score ?? undefined,
        seo_score: scores.seo_score ?? undefined,
      };

      await updateContent(id!, contentData);
      setLastSaved(new Date());
    } catch (error) {
      console.error('Autosave failed:', error);
      // Silent fail for autosave
    }
  }, [isEditMode, formData, scores, id]);

  // Autosave effect
  useEffect(() => {
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }

    autosaveTimerRef.current = setTimeout(() => {
      autoSave();
    }, 3000); // Autosave after 3 seconds of inactivity

    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
    };
  }, [formData, autoSave]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    if (name.startsWith('metadata.')) {
      const metadataKey = name.split('.')[1];
      setFormData((prev) => ({
        ...prev,
        metadata: {
          ...prev.metadata,
          [metadataKey]: value,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleGenerateContent = async () => {
    if (!formData.title) {
      toast.error('Please enter a title or topic first');
      return;
    }

    setGenerating(true);
    const loadingToast = toast.loading('Generating content with AI...');

    try {
      const generated = await generateContent({
        topic: formData.title,
        content_type: formData.type,
        platform: formData.platform,
        target_audience: formData.metadata.target_audience,
      });

      setFormData((prev) => ({
        ...prev,
        body: generated.content,
      }));

      setScores({
        brand_voice_score: generated.brand_voice_score,
        seo_score: generated.seo_score,
      });

      toast.success('Content generated successfully!', { id: loadingToast });
    } catch (error) {
      console.error('Failed to generate content:', error);
      toast.error('Failed to generate content. Please try again.', { id: loadingToast });
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (status: ContentStatus) => {
    if (!formData.title || !formData.body) {
      toast.error('Title and content are required');
      return;
    }

    setSaving(true);
    const statusText = status === 'draft' ? 'draft' : status === 'review' ? 'review' : 'published';
    const loadingToast = toast.loading(`Saving as ${statusText}...`);

    try {
      const contentData = {
        ...formData,
        status,
        brand_voice_score: scores.brand_voice_score ?? undefined,
        seo_score: scores.seo_score ?? undefined,
      };

      if (isEditMode) {
        await updateContent(id!, contentData);
        toast.success(`Content saved as ${statusText}!`, { id: loadingToast });
      } else {
        await createContent(contentData);
        toast.success(`Content created as ${statusText}!`, { id: loadingToast });
      }

      navigate('/content');
    } catch (error) {
      console.error('Failed to save content:', error);
      toast.error('Failed to save content. Please try again.', { id: loadingToast });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to Load Content"
        message={error}
        onRetry={fetchContent}
      />
    );
  }

  return (
    <div className="content-editor">
      <div className="editor-header">
        <button
          onClick={() => navigate('/content')}
          className="btn btn-secondary btn-sm"
        >
          <ArrowLeft size={16} />
          Back to Library
        </button>
        <div>
          <h1>{isEditMode ? 'Edit Content' : 'Create New Content'}</h1>
          {lastSaved && (
            <p className="text-sm text-secondary">
              Last saved: {lastSaved.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      <div className="editor-layout">
        {/* Main Editor */}
        <div className="editor-main">
          <div className="card">
            <div className="form-group">
              <label htmlFor="type">Content Type</label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="form-control"
              >
                <option value="blog">Blog Post</option>
                <option value="social">Social Media Post</option>
                <option value="email">Email</option>
                <option value="whitepaper">Whitepaper</option>
                <option value="case_study">Case Study</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="platform">Platform</label>
              <select
                id="platform"
                name="platform"
                value={formData.platform}
                onChange={handleInputChange}
                className="form-control"
              >
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter</option>
                <option value="blog">Blog</option>
                <option value="email">Email</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="title">Title / Topic</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Enter the title or main topic..."
                className="form-control"
              />
            </div>

            <div className="form-group">
              <div className="label-with-action">
                <label htmlFor="body">Content</label>
                <button
                  onClick={handleGenerateContent}
                  disabled={generating || !formData.title}
                  className="btn btn-primary btn-sm"
                >
                  <Sparkles size={16} />
                  {generating ? 'Generating...' : 'AI Generate'}
                </button>
              </div>
              <textarea
                id="body"
                name="body"
                value={formData.body}
                onChange={handleInputChange}
                placeholder="Write your content here or use AI to generate..."
                className="form-control content-textarea"
                rows={15}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="metadata.target_audience">Target Audience</label>
                <input
                  type="text"
                  id="metadata.target_audience"
                  name="metadata.target_audience"
                  value={formData.metadata.target_audience}
                  onChange={handleInputChange}
                  placeholder="e.g., Marketing Managers, CTOs"
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label htmlFor="metadata.keywords">Keywords (SEO)</label>
                <input
                  type="text"
                  id="metadata.keywords"
                  name="metadata.keywords"
                  value={formData.metadata.keywords}
                  onChange={handleInputChange}
                  placeholder="AI, automation, productivity"
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="metadata.cta">Call to Action</label>
              <input
                type="text"
                id="metadata.cta"
                name="metadata.cta"
                value={formData.metadata.cta}
                onChange={handleInputChange}
                placeholder="e.g., Book a demo, Download whitepaper"
                className="form-control"
              />
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="editor-sidebar">
          {/* Actions Card */}
          <div className="card">
            <h3 className="card-title">Actions</h3>
            <div className="action-buttons">
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="btn btn-secondary btn-block"
              >
                <Eye size={16} />
                {showPreview ? 'Hide Preview' : 'Show Preview'}
              </button>

              <button
                onClick={() => handleSave('draft')}
                disabled={saving}
                className="btn btn-secondary btn-block"
              >
                <Save size={16} />
                Save as Draft
              </button>

              <button
                onClick={() => handleSave('review')}
                disabled={saving}
                className="btn btn-warning btn-block"
              >
                <Send size={16} />
                Submit for Review
              </button>

              <button
                onClick={() => handleSave('approved')}
                disabled={saving}
                className="btn btn-success btn-block"
              >
                <CheckCircle size={16} />
                Approve & Publish
              </button>
            </div>
          </div>

          {/* Scores Card */}
          <div className="card">
            <h3 className="card-title">Quality Scores</h3>

            {scores.brand_voice_score !== null || scores.seo_score !== null ? (
              <div className="scores-container">
                {scores.brand_voice_score !== null && (
                  <div className="score-item">
                    <div className="score-header">
                      <TrendingUp size={16} />
                      <span>Brand Voice</span>
                    </div>
                    <div className="score-value">
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{
                            width: `${scores.brand_voice_score}%`,
                            backgroundColor:
                              scores.brand_voice_score >= 80
                                ? 'var(--success)'
                                : scores.brand_voice_score >= 60
                                ? 'var(--warning)'
                                : 'var(--error)',
                          }}
                        />
                      </div>
                      <span className="score-number">
                        {scores.brand_voice_score}%
                      </span>
                    </div>
                  </div>
                )}

                {scores.seo_score !== null && (
                  <div className="score-item">
                    <div className="score-header">
                      <TrendingUp size={16} />
                      <span>SEO Score</span>
                    </div>
                    <div className="score-value">
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{
                            width: `${scores.seo_score}%`,
                            backgroundColor:
                              scores.seo_score >= 80
                                ? 'var(--success)'
                                : scores.seo_score >= 60
                                ? 'var(--warning)'
                                : 'var(--error)',
                          }}
                        />
                      </div>
                      <span className="score-number">{scores.seo_score}%</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-scores">
                <AlertCircle size={24} />
                <p>Generate content with AI to see quality scores</p>
              </div>
            )}
          </div>

          {/* Tips Card */}
          <div className="card tips-card">
            <h3 className="card-title">AI Tips</h3>
            <ul className="tips-list">
              <li>Use specific, descriptive titles for better AI generation</li>
              <li>Include target audience for personalized content</li>
              <li>Add relevant keywords to improve SEO scores</li>
              <li>Brand voice scores measure alignment with AI Elevate values</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="preview-overlay" onClick={() => setShowPreview(false)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <h2>Preview</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="btn btn-secondary btn-sm"
              >
                Close
              </button>
            </div>
            <div className="preview-content">
              <h1 className="preview-title">{formData.title || 'Untitled'}</h1>
              <div className="preview-meta">
                <span className="badge badge-primary">{formData.type}</span>
                <span className="badge badge-secondary">{formData.platform}</span>
              </div>
              <div
                className="preview-body"
                dangerouslySetInnerHTML={{
                  __html: formData.body.replace(/\n/g, '<br>'),
                }}
              />
              {formData.metadata.cta && (
                <div className="preview-cta">
                  <button className="btn btn-primary">{formData.metadata.cta}</button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentEditor;
