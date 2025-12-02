import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { supabase } from '../lib/supabase'
import { api } from '../lib/api'
import type { Note } from '../lib/api'

const Overlay: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [session, setSession] = useState<any>(null)
    const [note, setNote] = useState<Note | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
        })

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
        })

        return () => subscription.unsubscribe()
    }, [])

    useEffect(() => {
        if (isOpen && session) {
            fetchNote()
        }
    }, [isOpen, session])

    const fetchNote = async () => {
        setLoading(true)
        setError(null)
        try {
            const currentUrl = window.location.href
            const n = await api.getNoteByUrl(currentUrl)
            setNote(n)
        } catch (e: any) {
            if (e.message !== 'Note not found') {
                setError(e.message)
            } else {
                setNote(null)
            }
        } finally {
            setLoading(false)
        }
    }

    const handleCreateNote = async () => {
        setLoading(true)
        setError(null)
        try {
            const currentUrl = window.location.href
            const res = await api.createNote(currentUrl)
            // Start polling
            pollNote(res.note_id)
        } catch (e: any) {
            setError(e.message)
            setLoading(false)
        }
    }

    const pollNote = async (noteId: number) => {
        const interval = setInterval(async () => {
            try {
                const n = await api.getNote(noteId)
                setNote(n)
                if (n.status === 'COMPLETED' || n.status === 'FAILED') {
                    clearInterval(interval)
                    setLoading(false)
                }
            } catch (e) {
                console.error(e)
            }
        }, 2000)
    }

    if (!session) return null // Or show a login prompt button

    return (
        <div className="fixed bottom-4 right-4 z-50 font-sans">
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
                {isOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                )}
            </button>

            {/* Sidebar / Content Area */}
            {isOpen && (
                <div className="absolute bottom-16 right-0 w-96 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden flex flex-col max-h-[80vh]">
                    <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                        <h2 className="font-bold text-gray-800">TubeWiki</h2>
                        <span className="text-xs text-gray-500">
                            {note?.status && <span className={`px-2 py-1 rounded-full ${note.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{note.status}</span>}
                        </span>
                    </div>

                    <div className="p-4 overflow-y-auto flex-1">
                        {loading && !note && (
                            <div className="flex justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            </div>
                        )}

                        {error && (
                            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">
                                {error}
                            </div>
                        )}

                        {!note && !loading && !error && (
                            <div className="text-center py-8">
                                <p className="text-gray-600 mb-4">No wiki found for this video.</p>
                                <button
                                    onClick={handleCreateNote}
                                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Generate Wiki
                                </button>
                            </div>
                        )}

                        {note && (
                            <div className="prose prose-sm max-w-none">
                                {note.status === 'PROCESSING' && (
                                    <div className="text-center py-4">
                                        <p className="text-gray-500 animate-pulse">Generating content...</p>
                                    </div>
                                )}
                                {note.title && <h3 className="text-lg font-bold mb-2">{note.title}</h3>}
                                {note.content && (
                                    <div className="text-gray-700">
                                        <ReactMarkdown>{note.content}</ReactMarkdown>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

export default Overlay
