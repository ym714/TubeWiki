import { createClient } from '@supabase/supabase-js'
import { chromeStorageAdapter } from './storage'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
    const errorMsg = `Missing Supabase credentials: URL=${!!supabaseUrl}, Key=${!!supabaseAnonKey}`
    console.error(errorMsg)
    throw new Error(errorMsg)
}

let supabaseInstance: ReturnType<typeof createClient> | null = null

export const getSupabase = () => {
    if (supabaseInstance) return supabaseInstance

    if (!supabaseUrl || !supabaseAnonKey) {
        const errorMsg = `Missing Supabase credentials: URL=${!!supabaseUrl}, Key=${!!supabaseAnonKey}`
        console.error(errorMsg)
        throw new Error(errorMsg)
    }

    try {
        supabaseInstance = createClient(supabaseUrl, supabaseAnonKey, {
            auth: {
                storage: chromeStorageAdapter,
                autoRefreshToken: true,
                persistSession: true,
                detectSessionInUrl: false,
            },
        })
    } catch (error) {
        console.error('Failed to initialize Supabase client:', error)
        throw error
    }

    return supabaseInstance
}
