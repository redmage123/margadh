import { useState, useEffect, useRef } from 'react';
import {
  MessageCircle,
  Send,
  Edit,
  Trash2,
  CheckCircle,
  MoreVertical,
} from 'lucide-react';
import type { Comment } from '@/types/collaboration';
import {
  getComments,
  addComment,
  updateComment,
  deleteComment,
  resolveComment,
  unresolveComment,
} from '@/services/collaboration';
import { CURRENT_USER, MOCK_USERS } from '@/services/approvals';
import { formatRelativeTime, highlightMentions } from '@/types/collaboration';
import toast from 'react-hot-toast';
import './Comments.css';

interface CommentsProps {
  contentId: string;
}

export const Comments = ({ contentId }: CommentsProps) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [showMentions, setShowMentions] = useState(false);
  const [mentionSearch, setMentionSearch] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fetchComments();
  }, [contentId]);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const data = await getComments(contentId);
      setComments(data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
      toast.error('Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      const comment = await addComment(contentId, newComment, replyTo || undefined);
      setComments([...comments, comment]);
      setNewComment('');
      setReplyTo(null);
      toast.success('Comment added');
    } catch (error) {
      console.error('Failed to add comment:', error);
      toast.error('Failed to add comment');
    }
  };

  const handleUpdateComment = async (commentId: string) => {
    if (!editText.trim()) return;

    try {
      const updated = await updateComment(commentId, editText);
      setComments(comments.map(c => (c.id === commentId ? updated : c)));
      setEditingId(null);
      setEditText('');
      toast.success('Comment updated');
    } catch (error) {
      console.error('Failed to update comment:', error);
      toast.error('Failed to update comment');
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Delete this comment?')) return;

    try {
      await deleteComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
      toast.success('Comment deleted');
    } catch (error) {
      console.error('Failed to delete comment:', error);
      toast.error('Failed to delete comment');
    }
  };

  const handleResolveComment = async (commentId: string, resolved: boolean) => {
    try {
      const updated = resolved
        ? await unresolveComment(commentId)
        : await resolveComment(commentId);
      setComments(comments.map(c => (c.id === commentId ? updated : c)));
      toast.success(resolved ? 'Comment reopened' : 'Comment resolved');
    } catch (error) {
      console.error('Failed to resolve comment:', error);
      toast.error('Failed to update comment');
    }
  };

  const handleTextChange = (text: string, isEdit: boolean = false) => {
    if (isEdit) {
      setEditText(text);
    } else {
      setNewComment(text);
    }

    // Check for @ mention trigger
    const lastAtIndex = text.lastIndexOf('@');
    if (lastAtIndex !== -1) {
      const textAfterAt = text.substring(lastAtIndex + 1);
      if (!textAfterAt.includes(' ')) {
        setMentionSearch(textAfterAt.toLowerCase());
        setShowMentions(true);
        return;
      }
    }

    setShowMentions(false);
  };

  const insertMention = (userName: string, isEdit: boolean = false) => {
    const text = isEdit ? editText : newComment;
    const lastAtIndex = text.lastIndexOf('@');

    if (lastAtIndex !== -1) {
      const before = text.substring(0, lastAtIndex);
      const after = text.substring(lastAtIndex).replace(/@\w*/, `@${userName.replace(/\s+/g, '')} `);
      const newText = before + after;

      if (isEdit) {
        setEditText(newText);
      } else {
        setNewComment(newText);
      }
    }

    setShowMentions(false);
    textareaRef.current?.focus();
  };

  const filteredUsers = MOCK_USERS.filter(u =>
    u.name.toLowerCase().includes(mentionSearch) ||
    u.role.toLowerCase().includes(mentionSearch)
  );

  // Organize comments by thread
  const topLevelComments = comments.filter(c => !c.parent_id);
  const getReplies = (parentId: string) => comments.filter(c => c.parent_id === parentId);

  return (
    <div className="comments-section">
      <div className="comments-header">
        <h3 className="comments-title">
          <MessageCircle size={20} />
          Comments ({comments.length})
        </h3>
      </div>

      {/* Comment Input */}
      <div className="comment-input-container">
        <div className="comment-avatar">
          {CURRENT_USER.name.split(' ').map((n: string) => n[0]).join('')}
        </div>
        <div className="comment-input-wrapper">
          <textarea
            ref={textareaRef}
            value={newComment}
            onChange={(e) => handleTextChange(e.target.value)}
            placeholder={replyTo ? "Write a reply... (Use @ to mention)" : "Add a comment... (Use @ to mention)"}
            className="comment-textarea"
            rows={3}
          />

          {/* @Mention Autocomplete */}
          {showMentions && filteredUsers.length > 0 && (
            <div className="mention-autocomplete">
              {filteredUsers.map(user => (
                <div
                  key={user.id}
                  className="mention-option"
                  onClick={() => insertMention(user.name)}
                >
                  <div className="mention-avatar">
                    {user.name.split(' ').map((n: string) => n[0]).join('')}
                  </div>
                  <div className="mention-info">
                    <div className="mention-name">{user.name}</div>
                    <div className="mention-role">{user.role.replace('_', ' ')}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="comment-actions">
            {replyTo && (
              <button
                onClick={() => setReplyTo(null)}
                className="btn btn-secondary btn-sm"
              >
                Cancel Reply
              </button>
            )}
            <button
              onClick={handleAddComment}
              disabled={!newComment.trim()}
              className="btn btn-primary btn-sm"
            >
              <Send size={16} />
              {replyTo ? 'Reply' : 'Comment'}
            </button>
          </div>
        </div>
      </div>

      {/* Comments List */}
      <div className="comments-list">
        {loading ? (
          <div className="comments-loading">Loading comments...</div>
        ) : topLevelComments.length === 0 ? (
          <div className="comments-empty">
            <MessageCircle size={48} />
            <p>No comments yet. Be the first to comment!</p>
          </div>
        ) : (
          topLevelComments.map(comment => (
            <CommentItem
              key={comment.id}
              comment={comment}
              replies={getReplies(comment.id)}
              onReply={setReplyTo}
              onEdit={(id, text) => {
                setEditingId(id);
                setEditText(text);
              }}
              onUpdate={handleUpdateComment}
              onDelete={handleDeleteComment}
              onResolve={handleResolveComment}
              editingId={editingId}
              editText={editText}
              onEditTextChange={(text) => handleTextChange(text, true)}
              onCancelEdit={() => {
                setEditingId(null);
                setEditText('');
              }}
              showMentions={showMentions && editingId === comment.id}
              filteredUsers={filteredUsers}
              onInsertMention={(name) => insertMention(name, true)}
            />
          ))
        )}
      </div>
    </div>
  );
};

// Comment Item Component
interface CommentItemProps {
  comment: Comment;
  replies: Comment[];
  onReply: (id: string) => void;
  onEdit: (id: string, text: string) => void;
  onUpdate: (id: string) => void;
  onDelete: (id: string) => void;
  onResolve: (id: string, resolved: boolean) => void;
  editingId: string | null;
  editText: string;
  onEditTextChange: (text: string) => void;
  onCancelEdit: () => void;
  showMentions: boolean;
  filteredUsers: any[];
  onInsertMention: (name: string) => void;
}

const CommentItem = ({
  comment,
  replies,
  onReply,
  onEdit,
  onUpdate,
  onDelete,
  onResolve,
  editingId,
  editText,
  onEditTextChange,
  onCancelEdit,
  showMentions,
  filteredUsers,
  onInsertMention,
}: CommentItemProps) => {
  const [showMenu, setShowMenu] = useState(false);
  const isEditing = editingId === comment.id;
  const isOwner = comment.user_id === CURRENT_USER.id;

  return (
    <div className={`comment-item ${comment.resolved ? 'comment-resolved' : ''}`}>
      <div className="comment-avatar">
        {comment.user_name.split(' ').map((n: string) => n[0]).join('')}
      </div>

      <div className="comment-content">
        <div className="comment-header">
          <span className="comment-author">{comment.user_name}</span>
          <span className="comment-time">{formatRelativeTime(comment.created_at)}</span>
          {comment.edited && <span className="comment-edited">(edited)</span>}
          {comment.resolved && (
            <span className="comment-resolved-badge">
              <CheckCircle size={14} />
              Resolved
            </span>
          )}

          {isOwner && (
            <div className="comment-menu">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="comment-menu-btn"
              >
                <MoreVertical size={16} />
              </button>

              {showMenu && (
                <div className="comment-menu-dropdown">
                  <button onClick={() => onEdit(comment.id, comment.text)}>
                    <Edit size={14} />
                    Edit
                  </button>
                  <button onClick={() => onDelete(comment.id)}>
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {isEditing ? (
          <div className="comment-edit">
            <textarea
              value={editText}
              onChange={(e) => onEditTextChange(e.target.value)}
              className="comment-textarea"
              rows={3}
              autoFocus
            />

            {showMentions && filteredUsers.length > 0 && (
              <div className="mention-autocomplete">
                {filteredUsers.map(user => (
                  <div
                    key={user.id}
                    className="mention-option"
                    onClick={() => onInsertMention(user.name)}
                  >
                    <div className="mention-avatar">
                      {user.name.split(' ').map((n: string) => n[0]).join('')}
                    </div>
                    <div className="mention-info">
                      <div className="mention-name">{user.name}</div>
                      <div className="mention-role">{user.role.replace('_', ' ')}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="comment-edit-actions">
              <button onClick={onCancelEdit} className="btn btn-secondary btn-sm">
                Cancel
              </button>
              <button onClick={() => onUpdate(comment.id)} className="btn btn-primary btn-sm">
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            <div
              className="comment-text"
              dangerouslySetInnerHTML={{
                __html: highlightMentions(comment.text, MOCK_USERS),
              }}
            />

            <div className="comment-actions">
              <button onClick={() => onReply(comment.id)} className="comment-action-btn">
                Reply
              </button>
              <button
                onClick={() => onResolve(comment.id, comment.resolved)}
                className="comment-action-btn"
              >
                {comment.resolved ? 'Reopen' : 'Resolve'}
              </button>
            </div>
          </>
        )}

        {/* Replies */}
        {replies.length > 0 && (
          <div className="comment-replies">
            {replies.map(reply => (
              <CommentItem
                key={reply.id}
                comment={reply}
                replies={[]}
                onReply={onReply}
                onEdit={onEdit}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onResolve={onResolve}
                editingId={editingId}
                editText={editText}
                onEditTextChange={onEditTextChange}
                onCancelEdit={onCancelEdit}
                showMentions={showMentions}
                filteredUsers={filteredUsers}
                onInsertMention={onInsertMention}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
