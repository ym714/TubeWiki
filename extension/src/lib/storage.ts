import { SupportedStorage } from '@supabase/supabase-js'

export const chromeStorageAdapter: SupportedStorage = {
    getItem: async (key: string) => {
        const result = await chrome.storage.local.get(key)
        return (result[key] as string) || null
    },
    setItem: async (key: string, value: string) => {
        await chrome.storage.local.set({ [key]: value })
    },
    removeItem: async (key: string) => {
        await chrome.storage.local.remove(key)
    },
}
