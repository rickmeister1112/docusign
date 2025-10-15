import { useState, useEffect } from "react";
import { AuthProvider } from "./contexts/AuthProvider.tsx";
import { useAuth } from "./hooks/useAuth";
import AuthPage from "./components/AuthPage";
import FeedbackForm from "./components/FeedbackForm";
import FeedbackList from "./components/FeedbackList";
import { feedbackApi } from "./services/api";
import type { Feedback, FeedbackCreate } from "./types/feedback";
import "./App.css";

/**
 * Main application component with authentication.
 * Shows auth page if not authenticated, otherwise shows feedback app.
 */
function AppContent() {
  const { user, isLoading, logout } = useAuth();
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [isLoadingFeedbacks, setIsLoadingFeedbacks] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [refreshCounter, setRefreshCounter] = useState(0);

  const loadFeedbacks = async () => {
    try {
      setIsLoadingFeedbacks(true);
      setError("");
      const data = await feedbackApi.getAll();
      setFeedbacks(data);
    } catch (err) {
      setError("Failed to load feedback entries. Please refresh the page.");
      console.error("Error loading feedbacks:", err);
    } finally {
      setIsLoadingFeedbacks(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadFeedbacks();
    }
  }, [user, refreshCounter]);

  const handleSubmitFeedback = async (feedback: FeedbackCreate) => {
    try {
      setIsSubmitting(true);
      setError("");
      const newFeedback = await feedbackApi.create(feedback);
      setFeedbacks((prev) => [newFeedback, ...prev]);
      setRefreshCounter((prev) => prev + 1);
    } catch (err) {
      console.error("Error submitting feedback:", err);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpvoteFeedback = async (id: number) => {
    try {
      setError("");
      const response = await feedbackApi.upvote(id);
      setFeedbacks((prev) =>
        prev.map((feedback) =>
          feedback.id === id
            ? { 
                ...feedback, 
                upvotes: response.upvotes,
                has_upvoted: response.has_upvoted 
              }
            : feedback
        )
      );
    } catch (err) {
      setError("Failed to upvote feedback. Please try again.");
      console.error("Error upvoting feedback:", err);
    }
  };

  const handleDeleteFeedback = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this feedback?")) {
      return;
    }

    try {
      setError("");
      await feedbackApi.delete(id);
      setFeedbacks((prev) => prev.filter((feedback) => feedback.id !== id));
    } catch (err) {
      setError("Failed to delete feedback. Please try again.");
      console.error("Error deleting feedback:", err);
    }
  };

  const handleLogout = () => {
    setFeedbacks([]);
    setError("");
    setIsLoadingFeedbacks(true);
    setIsSubmitting(false);
    setRefreshCounter(0);
    logout();
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show auth page if not authenticated
  if (!user) {
    return <AuthPage />;
  }

  // Show main app if authenticated
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>Feedback System</h1>
            <p>
              A simple CRUD application for managing feedback submissions with
              upvote functionality
            </p>
          </div>
          <div className="user-info">
            <span>Welcome, {user.email}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="global-error">
            {error}
            <button onClick={() => setError("")} className="error-close">
              ×
            </button>
          </div>
        )}

        <div className="app-content">
          <FeedbackForm
            onSubmit={handleSubmitFeedback}
            isLoading={isSubmitting}
          />

          <FeedbackList
            feedbacks={feedbacks}
            isLoading={isLoadingFeedbacks}
            onDelete={handleDeleteFeedback}
            onUpvote={handleUpvoteFeedback}
            currentUserEmail={user.email}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>Built with React + TypeScript + Vite + FastAPI + SQLite</p>
      </footer>
    </div>
  );
}

/**
 * Root application component with authentication provider.
 */
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
