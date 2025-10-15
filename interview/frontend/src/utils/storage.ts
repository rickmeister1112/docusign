/**
 * Safe localStorage wrapper with fallback to memory storage.
 * Handles cases where localStorage is unavailable (private browsing, old browsers).
 */

class StorageService {
  private isAvailable: boolean;
  private memoryStorage: Map<string, string>;

  constructor() {
    this.memoryStorage = new Map();
    this.isAvailable = this.checkAvailability();
  }

  /**
   * Check if localStorage is available and functional.
   */
  private checkAvailability(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (e) {
      console.warn('localStorage not available, using memory storage:', e);
      return false;
    }
  }

  /**
   * Get item from storage (localStorage or memory fallback).
   */
  getItem(key: string): string | null {
    if (this.isAvailable) {
      try {
        return localStorage.getItem(key);
      } catch (e) {
        console.error('Error reading from localStorage:', e);
      }
    }
    return this.memoryStorage.get(key) || null;
  }

  /**
   * Set item in storage (localStorage or memory fallback).
   */
  setItem(key: string, value: string): void {
    if (this.isAvailable) {
      try {
        localStorage.setItem(key, value);
        return;
      } catch (e) {
        console.error('Error writing to localStorage:', e);
      }
    }
    this.memoryStorage.set(key, value);
  }

  /**
   * Remove item from storage.
   */
  removeItem(key: string): void {
    if (this.isAvailable) {
      try {
        localStorage.removeItem(key);
        return;
      } catch (e) {
        console.error('Error removing from localStorage:', e);
      }
    }
    this.memoryStorage.delete(key);
  }

  /**
   * Clear all storage.
   */
  clear(): void {
    if (this.isAvailable) {
      try {
        localStorage.clear();
        return;
      } catch (e) {
        console.error('Error clearing localStorage:', e);
      }
    }
    this.memoryStorage.clear();
  }

  /**
   * Check if storage is using localStorage or memory fallback.
   */
  isUsingLocalStorage(): boolean {
    return this.isAvailable;
  }
}

// Export singleton instance
export const storage = new StorageService();

