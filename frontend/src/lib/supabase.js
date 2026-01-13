import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('[SUPABASE] Missing environment variables:', {
    hasUrl: !!supabaseUrl,
    hasKey: !!supabaseAnonKey
  });
  throw new Error('Missing Supabase environment variables. Check your .env file.');
}

// Create Supabase client with minimal auth auto-management
// We use backend API for auth, so we disable Supabase's automatic session handling
// This prevents AbortError issues during initialization
let supabase;
try {
  supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: false,   // Disabled - backend handles token refresh
      persistSession: false,      // Disabled - we store tokens manually in localStorage
      detectSessionInUrl: false,  // Disabled - no OAuth/URL-based flows
      // Note: onAuthStateChange listener will still work, it just won't auto-restore sessions
    }
  });
} catch (error) {
  console.error('[SUPABASE] Failed to initialize client:', error);
  throw error;
}

export { supabase };
