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

export interface AppSettings {
    notionToken?: string
    notionPageId?: string
    githubToken?: string
    githubRepo?: string
    obsidianVaultName?: string
}

export const storage = {
    get: async (): Promise<AppSettings> => {
        return new Promise((resolve) => {
            chrome.storage.sync.get(
                ['notionToken', 'notionPageId', 'githubToken', 'githubRepo', 'obsidianVaultName'],
                (items) => {
                    resolve(items as AppSettings)
                }
            )
        })
    },

    set: async (settings: AppSettings): Promise<void> => {
        return new Promise((resolve) => {
            chrome.storage.sync.set(settings, () => {
                resolve()
            })
        })
    },

    // Check if a specific service is configured
    isConfigured: async (service: 'notion' | 'github' | 'obsidian'): Promise<boolean> => {
        const settings = await storage.get()
        switch (service) {
            case 'notion':
                return !!(settings.notionToken && settings.notionPageId)
            case 'github':
                return !!(settings.githubToken && settings.githubRepo)
            case 'obsidian':
                return !!settings.obsidianVaultName
            default:
                return false
        }
    }
}
