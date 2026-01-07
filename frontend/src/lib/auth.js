import { supabase } from './supabase';

const authService = {
  async register(data) {
    // Sign up with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
    });

    if (authError) {
      throw new Error(authError.message);
    }

    if (!authData.user) {
      throw new Error('Registration failed');
    }

    // Create user record in public.users table
    const { error: insertError } = await supabase
      .from('users')
      .insert({
        id: authData.user.id,
        email: data.email,
        name: data.name,
        role: data.role,
        verification_status: 'unverified'
      });

    if (insertError) {
      throw new Error(insertError.message);
    }

    // Fetch the user profile with role
    const { data: profile, error: profileError } = await supabase
      .from('users')
      .select('*')
      .eq('id', authData.user.id)
      .single();

    if (profileError) {
      throw new Error(profileError.message);
    }

    return {
      success: true,
      user: {
        id: profile.id,
        email: profile.email,
        name: profile.name,
        role: profile.role,
        verificationStatus: profile.verification_status
      },
      session: authData.session
    };
  },

  async login(email, password) {
    // Sign in with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      throw new Error(authError.message);
    }

    if (!authData.user) {
      throw new Error('Invalid credentials');
    }

    // Fetch user profile with role from public.users table
    const { data: profile, error: profileError } = await supabase
      .from('users')
      .select('*')
      .eq('id', authData.user.id)
      .single();

    if (profileError || !profile) {
      throw new Error('User profile not found');
    }

    return {
      success: true,
      user: {
        id: profile.id,
        email: profile.email,
        name: profile.name,
        role: profile.role,
        verificationStatus: profile.verification_status
      },
      session: authData.session
    };
  },

  async logout() {
    await supabase.auth.signOut();
  },

  async getUser() {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      return null;
    }

    // Fetch role from public.users table
    const { data: profile, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', user.id)
      .single();

    if (error || !profile) {
      return null;
    }

    return {
      id: profile.id,
      email: profile.email,
      name: profile.name,
      role: profile.role,
      verificationStatus: profile.verification_status
    };
  },

  async getSession() {
    const { data: { session } } = await supabase.auth.getSession();
    return session;
  },

  isAuthenticated() {
    return supabase.auth.getSession().then(({ data: { session } }) => !!session);
  }
};

export default authService;
