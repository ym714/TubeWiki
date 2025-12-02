import { createClient } from '@supabase/supabase-js'
import { chromeStorageAdapter } from './storage'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
    const errorMsg = `Missing Supabase credentials: URL=${!!supabaseUrl}, Key=${!!supabaseAnonKey}`
    console.error(errorMsg)
    throw new Error(errorMsg)
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        storage: chromeStorageAdapter,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: false,
    },
})
