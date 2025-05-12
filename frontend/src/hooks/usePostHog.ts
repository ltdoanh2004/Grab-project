import posthog from '../utils/posthog';

interface EventProperties {
  [key: string]: any;
}

/**
 * Custom hook to track events with PostHog
 */
export function usePostHog() {
  /**
   * Track an event
   * @param eventName - The name of the event to track
   * @param properties - Additional properties to send with the event
   */
  const trackEvent = (eventName: string, properties?: EventProperties) => {
    posthog.capture(eventName, properties);
  };

  /**
   * Identify a user
   * @param userId - User's ID or distinct ID
   * @param properties - User properties to set
   */
  const identify = (userId: string, properties?: EventProperties) => {
    posthog.identify(userId, properties);
  };

  /**
   * Reset the current user and start a new anonymous session
   */
  const reset = () => {
    posthog.reset();
  };

  /**
   * Register persistent properties to be sent with every event
   * @param properties - Properties to register
   */
  const registerProperties = (properties: EventProperties) => {
    posthog.register(properties);
  };

  return {
    trackEvent,
    identify,
    reset,
    registerProperties,
    posthog,
  };
} 