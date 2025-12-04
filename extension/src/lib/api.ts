import type { Note } from '../types/note'
import { MessageType } from '../types/messages'
import type { ApiProxyRequest, ApiProxyResponse } from '../types/messages'

export type { Note }

const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
const API_URL = BASE_URL.endsWith('/api/v1') ? BASE_URL : `${BASE_URL}/api/v1`

/**
 * Send an API request through the background script to avoid CORS issues
 */
async function sendApiRequest(
    url: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
    body?: any
): Promise<any> {
    return new Promise((resolve, reject) => {
        const message: ApiProxyRequest = {
            type: MessageType.API_PROXY_REQUEST,
            url,
            method,
            headers: { 'Content-Type': 'application/json' },
            ...(body && { body: JSON.stringify(body) })
        }

        try {
            chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                // Check for extension context invalidation
                if (chrome.runtime.lastError) {
                    const error = chrome.runtime.lastError
                    if (error.message?.includes('Extension context invalidated')) {
                        reject(new Error(
                            '拡張機能が再読み込みされました。ページをリフレッシュしてください。\n' +
                            'Extension was reloaded. Please refresh the page.'
                        ))
                    } else {
                        reject(new Error(`Chrome runtime error: ${error.message}`))
                    }
                    return
                }

                if (!response) {
                    reject(new Error('No response from background script'))
                    return
                }

                if (response.ok) {
                    resolve(response.data)
                } else {
                    reject(new Error(response.error || `API request failed with status ${response.status}`))
                }
            })
        } catch (error) {
            // Catch synchronous errors (e.g., if chrome.runtime is not available)
            reject(new Error(
                '拡張機能との通信に失敗しました。ページをリフレッシュしてください。\n' +
                'Failed to communicate with extension. Please refresh the page.'
            ))
        }
    })
}

export const api = {
    async createNote(videoUrl: string, options: Record<string, any> = {}) {
        return sendApiRequest(`${API_URL}/notes`, 'POST', {
            video_url: videoUrl,
            options: options
        })
    },

    async getNote(noteId: number): Promise<Note> {
        return sendApiRequest(`${API_URL}/notes/${noteId}`, 'GET')
    },

    async getNoteByUrl(videoUrl: string): Promise<Note> {
        try {
            return await sendApiRequest(
                `${API_URL}/notes/by-url/?video_url=${encodeURIComponent(videoUrl)}`,
                'GET'
            )
        } catch (error) {
            // Check if it's a 404 error by checking the error message
            if (error instanceof Error && error.message.includes('404')) {
                throw new Error('Note not found')
            }
            throw error
        }
    }
}
