import { useState, useEffect } from "react";
import type { Feedback } from "../types/feedback";

interface FeedbackListProps {
  feedbacks: Feedback[];
  isLoading?: boolean;
  onDelete?: (id: number) => Promise<void>;
  onUpvote?: (id: number) => Promise<void>;
  currentUserEmail?: string;
}

/**
 * Feedback list component.
 * Displays all feedback entries in a clean, organized layout with upvote functionality.
 */
const FeedbackList: React.FC<FeedbackListProps> = ({
  feedbacks,
  isLoading = false,
  onDelete,
  onUpvote,
  currentUserEmail,
}) => {
  const [sortedFeedbacks, setSortedFeedbacks] = useState<Feedback[]>([]);

  useEffect(() => {
    const sorted = [...feedbacks].sort((a, b) => b.upvotes - a.upvotes);
    setSortedFeedbacks(sorted);
  }, [feedbacks]);

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleUpvote = async (id: number) => {
    if (onUpvote) {
      try {
        await onUpvote(id);
      } catch (error) {
        console.error("Error upvoting feedback:", error);
      }
    }
  };

  const handleDelete = async (id: number) => {
    if (onDelete) {
      try {
        await onDelete(id);
      } catch (error) {
        console.error("Error deleting feedback:", error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="feedback-list">
        <h2>Feedback Entries</h2>
        <div className="loading">Loading feedback...</div>
      </div>
    );
  }

  if (sortedFeedbacks.length === 0) {
    return (
      <div className="feedback-list">
        <h2>Feedback Entries</h2>
        <div className="empty-state">
          <p>No feedback submitted yet.</p>
          <p>Be the first to share your thoughts!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-list">
      <h2>
        Feedback Entries ({sortedFeedbacks.length})
      </h2>
      <div className="feedback-items">
        {sortedFeedbacks.map((feedback) => (
          <div key={feedback.id} className="feedback-item">
            <div className="feedback-content">
              <p className="feedback-text">{feedback.text}</p>
              <div className="feedback-meta">
                <span className="feedback-author">
                  By: {feedback.user_email}
                </span>
                <span className="feedback-date">
                  Submitted: {formatDate(feedback.created_at)}
                </span>
                {feedback.updated_at &&
                  feedback.updated_at !== feedback.created_at && (
                    <span className="feedback-updated">
                      Updated: {formatDate(feedback.updated_at)}
                    </span>
                  )}
              </div>
            </div>
            <div className="feedback-actions">
              {onUpvote && (
                <button
                  onClick={() => handleUpvote(feedback.id)}
                  className={`upvote-button ${feedback.has_upvoted ? 'upvoted' : ''}`}
                  title={feedback.has_upvoted ? "Remove your upvote" : "Upvote this feedback"}
                >
                  {feedback.has_upvoted ? '👍' : '👍'} {feedback.upvotes}
                </button>
              )}
              {onDelete && currentUserEmail === feedback.user_email && (
                <button
                  onClick={() => handleDelete(feedback.id)}
                  className="delete-button"
                  title="Delete this feedback"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeedbackList;
