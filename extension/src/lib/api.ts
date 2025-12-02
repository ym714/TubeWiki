import type { Note } from '../types/note'

export type { Note }

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = {
    async createNote(videoUrl: string, options: Record<string, any> = {}) {
        const response = await fetch(`${API_URL}/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_url: videoUrl,
                options: options
            })
        })

        if (!response.ok) {
            throw new Error('Failed to create note')
        }

        return response.json()
    },

    async getNote(noteId: number): Promise<Note> {
        const response = await fetch(`${API_URL}/notes/${noteId}`, {
            headers: {
                'Content-Type': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error('Failed to fetch note')
        }

        return response.json()

    },

    async getNoteByUrl(videoUrl: string): Promise<Note> {
        const response = await fetch(`${API_URL}/notes/by-url/?video_url=${encodeURIComponent(videoUrl)}`, {
            headers: {
                'Content-Type': 'application/json'
            }
        })

        if (response.status === 404) {
            throw new Error('Note not found')
        }

        if (!response.ok) {
            throw new Error('Failed to fetch note')
        }

        return response.json()
    }
}
