import { useState, useEffect } from "react";
import type { FeedbackCreate } from "../types/feedback";

interface FeedbackFormProps {
  onSubmit: (feedback: FeedbackCreate) => Promise<void>;
  isLoading?: boolean;
}

/**
 * Feedback submission form component.
 * Allows users to submit new feedback entries.
 */
const FeedbackForm: React.FC<FeedbackFormProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [charCount, setCharCount] = useState(0);

  useEffect(() => {
    setCharCount(text.length);
  }, [text]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
    setCharCount(newText.length);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate input
    if (!text.trim()) {
      setError("Please enter some feedback text");
      return;
    }

    if (text.length > 1000) {
      setError("Feedback text must be 1000 characters or less");
      return;
    }

    try {
      setError("");
      await onSubmit({ text: text.trim() });
      setText(""); // Clear form on successful submission
      setCharCount(0);
    } catch {
      setError("Failed to submit feedback. Please try again.");
    }
  };

  return (
    <div className="feedback-form">
      <h2>Submit Feedback</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="feedback-text">Your Feedback:</label>
          <textarea
            id="feedback-text"
            value={text}
            onChange={handleTextChange}
            placeholder="Share your thoughts, suggestions, or feedback..."
            rows={4}
            maxLength={1000}
            disabled={isLoading}
            className="feedback-textarea"
          />
          <div className="char-count">{charCount}/1000 characters</div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          type="submit"
          disabled={isLoading || !text.trim()}
          className="submit-button"
        >
          {isLoading ? "Submitting..." : "Submit Feedback"}
        </button>
      </form>
    </div>
  );
};

export default FeedbackForm;
