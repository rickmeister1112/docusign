/**
 * Auth event emitter for handling authentication state changes.
 * Allows components to react to auth events without tight coupling.
 */

type AuthEventType = 'logout' | 'unauthorized' | 'token_expired';
type AuthEventHandler = () => void;

class AuthEventEmitter {
  private handlers: Map<AuthEventType, Set<AuthEventHandler>>;

  constructor() {
    this.handlers = new Map();
  }

  /**
   * Subscribe to auth events.
   * Returns an unsubscribe function.
   */
  on(event: AuthEventType, handler: AuthEventHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.get(event)?.delete(handler);
    };
  }

  /**
   * Emit an auth event to all subscribers.
   */
  emit(event: AuthEventType): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler());
    }
  }

  /**
   * Remove all handlers for an event.
   */
  off(event: AuthEventType): void {
    this.handlers.delete(event);
  }

  /**
   * Clear all event handlers.
   */
  clear(): void {
    this.handlers.clear();
  }
}

// Export singleton instance
export const authEvents = new AuthEventEmitter();

