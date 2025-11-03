import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, dateFnsLocalizer, View } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, addDays } from 'date-fns';
import { enUS } from 'date-fns/locale';
import toast from 'react-hot-toast';
import {
  Calendar as CalendarIcon,
  Plus,
  Filter,
  ChevronLeft,
  ChevronRight,
  Edit,
  Trash2,
} from 'lucide-react';
import { getContent, deleteContent } from '@/services/api';
import type { Content, ContentStatus } from '@/types';
import { ErrorState, EmptyState } from '@/components/ErrorState';
import { DashboardSkeleton } from '@/components/LoadingSkeleton';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './ContentCalendar.css';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  resource: Content;
  status: ContentStatus;
}

const ContentCalendar = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [content, setContent] = useState<Content[]>([]);
  const [view, setView] = useState<View>('month');
  const [date, setDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [statusFilter, setStatusFilter] = useState<ContentStatus | 'all'>('all');

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getContent();
      setContent(data);
    } catch (err) {
      console.error('Failed to fetch content:', err);
      setError('Failed to load content calendar');
      toast.error('Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  const events: CalendarEvent[] = useMemo(() => {
    return content
      .filter((item) => {
        if (statusFilter !== 'all' && item.status !== statusFilter) {
          return false;
        }
        return item.published_at || item.created_at;
      })
      .map((item) => {
        const eventDate = item.published_at
          ? new Date(item.published_at)
          : new Date(item.created_at);

        return {
          id: item.id,
          title: item.title,
          start: eventDate,
          end: addDays(eventDate, 0), // Same day event
          resource: item,
          status: item.status,
        };
      });
  }, [content, statusFilter]);

  const handleSelectSlot = useCallback(
    ({ start }: { start: Date; end: Date }) => {
      navigate('/content/new', { state: { scheduledDate: start } });
    },
    [navigate]
  );

  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    setSelectedEvent(event);
  }, []);

  const handleDeleteContent = async (id: string) => {
    if (!confirm('Are you sure you want to delete this content?')) {
      return;
    }

    try {
      await deleteContent(id);
      toast.success('Content deleted successfully');
      setSelectedEvent(null);
      await fetchContent();
    } catch (err) {
      console.error('Failed to delete content:', err);
      toast.error('Failed to delete content');
    }
  };

  const eventStyleGetter = (event: CalendarEvent) => {
    const statusColors: Record<ContentStatus, string> = {
      draft: '#9ca3af',
      review: '#f59e0b',
      approved: '#10b981',
      published: '#667eea',
      rejected: '#ef4444',
    };

    return {
      style: {
        backgroundColor: statusColors[event.status] || '#667eea',
        borderRadius: '6px',
        opacity: 0.9,
        color: 'white',
        border: 'none',
        display: 'block',
        fontSize: '0.875rem',
        padding: '4px 8px',
      },
    };
  };

  const handleNavigate = (newDate: Date) => {
    setDate(newDate);
  };

  const handleViewChange = (newView: View) => {
    setView(newView);
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to Load Calendar"
        message={error}
        onRetry={fetchContent}
      />
    );
  }

  return (
    <div className="content-calendar">
      <div className="calendar-header">
        <div>
          <h1>Content Calendar</h1>
          <p className="text-secondary">Plan and schedule your content publishing</p>
        </div>
        <button
          onClick={() => navigate('/content/new')}
          className="btn btn-primary"
        >
          <Plus size={20} />
          Schedule Content
        </button>
      </div>

      <div className="calendar-toolbar">
        <div className="calendar-nav">
          <button
            onClick={() => handleNavigate(addDays(date, -30))}
            className="btn btn-secondary btn-sm"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            onClick={() => setDate(new Date())}
            className="btn btn-secondary btn-sm"
          >
            Today
          </button>
          <button
            onClick={() => handleNavigate(addDays(date, 30))}
            className="btn btn-secondary btn-sm"
          >
            <ChevronRight size={16} />
          </button>
          <span className="calendar-date-display">
            {format(date, 'MMMM yyyy')}
          </span>
        </div>

        <div className="calendar-views">
          <button
            onClick={() => handleViewChange('month')}
            className={`btn btn-sm ${view === 'month' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Month
          </button>
          <button
            onClick={() => handleViewChange('week')}
            className={`btn btn-sm ${view === 'week' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Week
          </button>
          <button
            onClick={() => handleViewChange('day')}
            className={`btn btn-sm ${view === 'day' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Day
          </button>
          <button
            onClick={() => handleViewChange('agenda')}
            className={`btn btn-sm ${view === 'agenda' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Agenda
          </button>
        </div>

        <div className="calendar-filter">
          <Filter size={16} />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as ContentStatus | 'all')}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="review">In Review</option>
            <option value="approved">Approved</option>
            <option value="published">Published</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div className="calendar-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#9ca3af' }}></span>
          <span>Draft</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#f59e0b' }}></span>
          <span>Review</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#10b981' }}></span>
          <span>Approved</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#667eea' }}></span>
          <span>Published</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ef4444' }}></span>
          <span>Rejected</span>
        </div>
      </div>

      {events.length === 0 ? (
        <EmptyState
          icon={<CalendarIcon size={48} />}
          title="No content scheduled"
          message="Start scheduling content to see it on your calendar"
          action={{
            label: 'Schedule Content',
            onClick: () => navigate('/content/new'),
            icon: <Plus size={20} />,
          }}
        />
      ) : (
        <div className="calendar-container card">
          <Calendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ height: 700 }}
            view={view}
            onView={handleViewChange}
            date={date}
            onNavigate={handleNavigate}
            onSelectSlot={handleSelectSlot}
            onSelectEvent={handleSelectEvent}
            eventPropGetter={eventStyleGetter}
            selectable
            popup
            views={['month', 'week', 'day', 'agenda']}
          />
        </div>
      )}

      {/* Event Details Sidebar */}
      {selectedEvent && (
        <div className="event-sidebar-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="event-sidebar" onClick={(e) => e.stopPropagation()}>
            <div className="event-sidebar-header">
              <h3>Content Details</h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="btn btn-secondary btn-sm"
              >
                ×
              </button>
            </div>

            <div className="event-sidebar-content">
              <div className="event-detail-section">
                <h4>{selectedEvent.title}</h4>
                <div className="event-meta">
                  <span className={`badge badge-${
                    selectedEvent.status === 'published' ? 'primary' :
                    selectedEvent.status === 'approved' ? 'success' :
                    selectedEvent.status === 'review' ? 'warning' :
                    selectedEvent.status === 'rejected' ? 'error' : 'secondary'
                  }`}>
                    {selectedEvent.status}
                  </span>
                  <span className="badge badge-secondary">
                    {selectedEvent.resource.type}
                  </span>
                </div>
              </div>

              <div className="event-detail-section">
                <label>Scheduled Date</label>
                <p>{format(selectedEvent.start, 'MMMM dd, yyyy')}</p>
              </div>

              {selectedEvent.resource.body && (
                <div className="event-detail-section">
                  <label>Preview</label>
                  <p className="event-preview">
                    {selectedEvent.resource.body.substring(0, 150)}...
                  </p>
                </div>
              )}

              {selectedEvent.resource.platform && (
                <div className="event-detail-section">
                  <label>Platform</label>
                  <p>{selectedEvent.resource.platform}</p>
                </div>
              )}

              <div className="event-sidebar-actions">
                <button
                  onClick={() => navigate(`/content/${selectedEvent.id}/edit`)}
                  className="btn btn-primary btn-block"
                >
                  <Edit size={16} />
                  Edit Content
                </button>
                <button
                  onClick={() => handleDeleteContent(selectedEvent.id)}
                  className="btn btn-danger btn-block"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentCalendar;
