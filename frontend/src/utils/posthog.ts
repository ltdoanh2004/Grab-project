import posthog from 'posthog-js';

// Initialize PostHog with your project API key
const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY || '';
const posthogHost = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com';

if (typeof window !== 'undefined') {
  posthog.init(posthogKey, {
    api_host: posthogHost,
    capture_pageview: true,     // Automatically capture pageviews
    capture_pageleave: true,    // Automatically capture when users leave
    loaded: (posthogInstance) => {
      if (process.env.NODE_ENV !== 'production') {
        // Add console debug in development
        posthogInstance.debug();
      }
    }
  });
}

export default posthog; 