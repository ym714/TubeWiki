export type NoteStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'

export interface Note {
    id: number
    user_id: string
    video_url: string
    title: string | null
    content: string | null
    status: NoteStatus
    created_at: string
    updated_at: string
    error_message: string | null
    notion_url?: string | null
}
