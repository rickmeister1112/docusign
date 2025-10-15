/**
 * Token Manager - Handles JWT token expiry warnings and auto-refresh
 * 
 * Features:
 * - Decode JWT to check expiry time
 * - Show warning before token expires
 * - Auto-refresh token if possible
 * - Graceful logout with countdown
 */

interface TokenPayload {
  exp: number; // Expiry timestamp
  sub: string; // User ID
  iat: number; // Issued at
}

interface TokenExpiryConfig {
  warningMinutes: number; // Show warning X minutes before expiry
  refreshMinutes: number; // Try to refresh X minutes before expiry
  logoutCountdownSeconds: number; // Countdown before forced logout
}

class TokenManager {
  private warningTimer: NodeJS.Timeout | null = null;
  private refreshTimer: NodeJS.Timeout | null = null;
  private logoutTimer: NodeJS.Timeout | null = null;
  private config: TokenExpiryConfig;
  private onTokenExpiry: (() => void) | null = null;
  private onTokenRefresh: (() => Promise<boolean>) | null = null;

  constructor(config: Partial<TokenExpiryConfig> = {}) {
    this.config = {
      warningMinutes: 5, // Warn 5 minutes before expiry
      refreshMinutes: 2, // Try refresh 2 minutes before expiry
      logoutCountdownSeconds: 30, // 30 second countdown
      ...config,
    };
  }

  /**
   * Set callback for when token expires
   */
  setOnTokenExpiry(callback: () => void): void {
    this.onTokenExpiry = callback;
  }

  /**
   * Set callback for token refresh attempt
   * Should return true if refresh successful, false otherwise
   */
  setOnTokenRefresh(callback: () => Promise<boolean>): void {
    this.onTokenRefresh = callback;
  }

  /**
   * Decode JWT token payload (without verification)
   */
  private decodeToken(token: string): TokenPayload | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  }

  /**
   * Get token expiry time in milliseconds
   */
  private getTokenExpiry(token: string): number | null {
    const payload = this.decodeToken(token);
    if (!payload || !payload.exp) {
      return null;
    }

    // Convert Unix timestamp to milliseconds
    return payload.exp * 1000;
  }

  /**
   * Get time until token expires in milliseconds
   */
  private getTimeUntilExpiry(token: string): number | null {
    const expiry = this.getTokenExpiry(token);
    if (!expiry) {
      return null;
    }

    return expiry - Date.now();
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(token: string): boolean {
    const timeUntilExpiry = this.getTimeUntilExpiry(token);
    return timeUntilExpiry === null || timeUntilExpiry <= 0;
  }

  /**
   * Start monitoring token expiry
   */
  startMonitoring(token: string): void {
    this.stopMonitoring();

    if (!token || this.isTokenExpired(token)) {
      return;
    }

    const timeUntilExpiry = this.getTimeUntilExpiry(token);
    if (!timeUntilExpiry) {
      return;
    }

    const warningTime = this.config.warningMinutes * 60 * 1000; // Convert to ms
    const refreshTime = this.config.refreshMinutes * 60 * 1000; // Convert to ms

    // Set warning timer
    if (timeUntilExpiry > warningTime) {
      const warningDelay = timeUntilExpiry - warningTime;
      this.warningTimer = setTimeout(() => {
        this.showExpiryWarning();
      }, warningDelay);
    }

    // Set refresh timer
    if (timeUntilExpiry > refreshTime) {
      const refreshDelay = timeUntilExpiry - refreshTime;
      this.refreshTimer = setTimeout(async () => {
        await this.attemptTokenRefresh();
      }, refreshDelay);
    }

    // Set logout timer (when token actually expires)
    this.logoutTimer = setTimeout(() => {
      this.handleTokenExpiry();
    }, timeUntilExpiry);
  }

  /**
   * Stop all monitoring timers
   */
  stopMonitoring(): void {
    if (this.warningTimer) {
      clearTimeout(this.warningTimer);
      this.warningTimer = null;
    }
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
    if (this.logoutTimer) {
      clearTimeout(this.logoutTimer);
      this.logoutTimer = null;
    }
  }

  /**
   * Show expiry warning to user
   */
  private showExpiryWarning(): void {
    const minutes = this.config.warningMinutes;
    
    // Create warning notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff6b6b;
      color: white;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      max-width: 300px;
      animation: slideIn 0.3s ease-out;
    `;

    notification.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 4px;">⚠️ Session Expiring Soon</div>
      <div>Your session will expire in ${minutes} minutes. Please save your work.</div>
      <button onclick="this.parentElement.remove()" style="
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        margin-top: 8px;
        cursor: pointer;
        font-size: 12px;
      ">Dismiss</button>
    `;

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 10000);
  }

  /**
   * Attempt to refresh token
   */
  private async attemptTokenRefresh(): Promise<void> {
    if (!this.onTokenRefresh) {
      return;
    }

    try {
      const success = await this.onTokenRefresh();
      if (success) {
        console.log('Token refreshed successfully');
        // Show success notification
        this.showRefreshSuccess();
      } else {
        console.log('Token refresh failed');
        this.showRefreshFailed();
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      this.showRefreshFailed();
    }
  }

  /**
   * Show refresh success notification
   */
  private showRefreshSuccess(): void {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #51cf66;
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = '✅ Session refreshed successfully';

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
  }

  /**
   * Show refresh failed notification
   */
  private showRefreshFailed(): void {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff6b6b;
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = '❌ Session refresh failed. Please log in again.';

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
  }

  /**
   * Handle token expiry with countdown
   */
  private handleTokenExpiry(): void {
    if (!this.onTokenExpiry) {
      return;
    }

    // Show countdown modal
    this.showLogoutCountdown();
  }

  /**
   * Show logout countdown modal
   */
  private showLogoutCountdown(): void {
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
      background: white;
      padding: 32px;
      border-radius: 12px;
      text-align: center;
      max-width: 400px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    `;

    let countdown = this.config.logoutCountdownSeconds;
    
    const updateCountdown = () => {
      content.innerHTML = `
        <div style="font-size: 24px; margin-bottom: 16px;">⏰</div>
        <h2 style="margin: 0 0 16px 0; color: #333;">Session Expired</h2>
        <p style="margin: 0 0 24px 0; color: #666;">
          Your session has expired. You will be logged out in ${countdown} seconds.
        </p>
        <button onclick="this.closest('.modal').remove(); window.location.href='/login'" style="
          background: #007bff;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
        ">Log In Again</button>
      `;
      
      countdown--;
      
      if (countdown < 0) {
        this.onTokenExpiry?.();
        modal.remove();
      } else {
        setTimeout(updateCountdown, 1000);
      }
    };

    content.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    updateCountdown();
  }
}

// Export singleton instance
export const tokenManager = new TokenManager();
