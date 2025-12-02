import { SupportedStorage } from '@supabase/supabase-js'

const isExtensionContextValid = () => {
    try {
        return typeof chrome !== 'undefined' &&
            !!chrome.runtime &&
            !!chrome.runtime.id
    } catch (e) {
        return false
    }
}

export const chromeStorageAdapter: SupportedStorage = {
    getItem: async (key: string) => {
        return new Promise((resolve) => {
            if (!isExtensionContextValid()) {
                resolve(null)
                return
            }
            try {
                chrome.storage.local.get(key, (result) => {
                    if (chrome.runtime.lastError) {
                        resolve(null)
                        return
                    }
                    resolve((result?.[key] as string) || null)
                })
            } catch (error) {
                resolve(null)
            }
        })
    },
    setItem: async (key: string, value: string) => {
        return new Promise((resolve) => {
            if (!isExtensionContextValid()) {
                resolve()
                return
            }
            try {
                chrome.storage.local.set({ [key]: value }, () => {
                    if (chrome.runtime.lastError) {
                        // Ignore error
                    }
                    resolve()
                })
            } catch (error) {
                resolve()
            }
        })
    },
    removeItem: async (key: string) => {
        return new Promise((resolve) => {
            if (!isExtensionContextValid()) {
                resolve()
                return
            }
            try {
                chrome.storage.local.remove(key, () => {
                    if (chrome.runtime.lastError) {
                        // Ignore error
                    }
                    resolve()
                })
            } catch (error) {
                resolve()
            }
        })
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
        if (!isExtensionContextValid()) {
            return {}
        }
        return new Promise((resolve) => {
            try {
                chrome.storage.sync.get(
                    ['notionToken', 'notionPageId', 'githubToken', 'githubRepo', 'obsidianVaultName'],
                    (items) => {
                        if (chrome.runtime.lastError) {
                            resolve({})
                            return
                        }
                        resolve(items as AppSettings)
                    }
                )
            } catch (error) {
                resolve({})
            }
        })
    },

    set: async (settings: AppSettings): Promise<void> => {
        if (!isExtensionContextValid()) {
            return
        }
        return new Promise((resolve) => {
            try {
                chrome.storage.sync.set(settings, () => {
                    if (chrome.runtime.lastError) {
                        // Ignore errors
                    }
                    resolve()
                })
            } catch (error) {
                resolve()
            }
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
