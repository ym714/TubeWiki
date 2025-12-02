import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface Note {
    id: number
    user_id: string
    video_url: string
    status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
    title?: string
    content?: string
    error_message?: string
    created_at: string
}

export const api = {
    async createNote(videoUrl: string) {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) throw new Error('Not authenticated')

        const response = await fetch(`${API_URL}/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session.access_token}`
            },
            body: JSON.stringify({
                video_url: videoUrl,
                user_id: session.user.id
            })
        })

        if (!response.ok) {
            throw new Error('Failed to create note')
        }

        return response.json()
    },

    async getNote(noteId: number): Promise<Note> {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) throw new Error('Not authenticated')

        const response = await fetch(`${API_URL}/notes/${noteId}`, {
            headers: {
                'Authorization': `Bearer ${session.access_token}`
            }
        })

        if (!response.ok) {
            throw new Error('Failed to fetch note')
        }

        return response.json()

    },

    async getNoteByUrl(videoUrl: string): Promise<Note> {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) throw new Error('Not authenticated')

        const response = await fetch(`${API_URL}/notes/by-url/?video_url=${encodeURIComponent(videoUrl)}`, {
            headers: {
                'Authorization': `Bearer ${session.access_token}`
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
