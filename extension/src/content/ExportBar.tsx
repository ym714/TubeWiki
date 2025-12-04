import { useState, useEffect } from 'react'
import { api, Note } from '../lib/api'
import { storage, chromeStorageAdapter } from '../lib/storage'
import { IconNotion, IconSettings, IconChevronDown } from './Icons'
import './style.css'

const ExportBar = () => {
    const [videoId, setVideoId] = useState<string | null>(null)
    const [note, setNote] = useState<Note | null>(null)
    const [loading, setLoading] = useState(false)
    const [loadingText, setLoadingText] = useState('')
    const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info' | 'warning', message: string } | null>(null)

    useEffect(() => {
        const checkVideo = () => {
            const params = new URLSearchParams(window.location.search)
            const v = params.get('v')
            if (v !== videoId) {
                setVideoId(v)
                setNote(null)
            }
        }

        checkVideo()
        const interval = setInterval(checkVideo, 1000)
        return () => clearInterval(interval)
    }, [videoId])

    useEffect(() => {
        // Try to fetch existing note if available
        const fetchNote = async () => {
            if (!videoId) return
            try {
                const url = `https://www.youtube.com/watch?v=${videoId}`
                const existingNote = await api.getNoteByUrl(url)
                setNote(existingNote)
            } catch (error) {
                // Note doesn't exist yet, this is fine
                console.log('[TubeWiki] No existing note found')
            }
        }
        fetchNote()
    }, [videoId])

    const showNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
        setNotification({ type, message })
        setTimeout(() => setNotification(null), 4000)
    }

    const ensureNote = async (): Promise<Note> => {
        console.log('[TubeWiki] ensureNote called', { note, videoId })
        if (note) return note

        setLoading(true)
        setLoadingText('Generating summary...')
        try {
            const url = `https://www.youtube.com/watch?v=${videoId}`
            console.log('[TubeWiki] Creating note for URL:', url)

            // Pass Notion options if configured
            const settings = await storage.get()
            const options: Record<string, any> = {}
            if (settings.notionToken && settings.notionPageId) {
                options.notion_token = settings.notionToken
                options.notion_page_id = settings.notionPageId
            }

            const newNote = await api.createNote(url, options)
            console.log('[TubeWiki] Note created:', newNote)

            // ポーリングで完了を待つ
            let attempts = 0
            while (attempts < 30) {
                await new Promise(resolve => setTimeout(resolve, 2000))
                try {
                    const completedNote = await api.getNote(newNote.id)
                    console.log('[TubeWiki] Polling note status:', completedNote.status)
                    if (completedNote.status === 'COMPLETED') {
                        setNote(completedNote)
                        setLoading(false)
                        return completedNote
                    }
                    if (completedNote.status === 'FAILED') {
                        throw new Error(completedNote.error_message || 'Generation failed')
                    }
                } catch (error) {
                    if ((error as Error).message === 'Generation failed') throw error
                    // まだ処理中
                }
                attempts++
            }
            throw new Error('Timeout waiting for note generation')
        } catch (error) {
            console.error('[TubeWiki] ensureNote failed:', error)
            setLoading(false)
            throw error
        }
    }

    const handleExport = async () => {
        console.log('[TubeWiki] handleExport called')

        try {
            const currentNote = await ensureNote()
            console.log('[TubeWiki] Note ensured:', currentNote)

            // Auto-Paste Flow: Save to storage & Open
            console.log('[TubeWiki] Saving to storage for Notion paste...')

            if (!currentNote.content) {
                console.error('[TubeWiki] Note content is empty!', currentNote)
                throw new Error('Generated note has no content')
            }

            console.log('[TubeWiki] Content length:', currentNote.content.length)

            await chromeStorageAdapter.setItem('pending_notion_paste', currentNote.content)

            // Verify storage
            const saved = await chromeStorageAdapter.getItem('pending_notion_paste')
            console.log('[TubeWiki] Verified storage save. Length:', saved?.length)

            if (saved !== currentNote.content) {
                console.error('[TubeWiki] Storage save failed verification!')
                throw new Error('Failed to save to storage')
            }

            console.log('[TubeWiki] Saved to storage. Opening Notion...')

            // Copy to clipboard BEFORE opening Notion (to avoid permission issues)
            try {
                await navigator.clipboard.writeText(currentNote.content)
                console.log('[TubeWiki] Content copied to clipboard')
                showNotification('✅ Opening Notion... Press Cmd+V to paste!', 'success')
            } catch (clipboardError) {
                console.warn('[TubeWiki] Clipboard copy failed:', clipboardError)
                showNotification('Opening Notion...', 'success')
            }

            window.open('https://notion.so/new', '_blank')

        } catch (error) {
            console.error('[TubeWiki] handleExport failed:', error)
            const msg = (error as Error).message
            if (msg.includes('401')) {
                showNotification('Authentication failed. Check settings.', 'error')
            } else {
                showNotification(msg, 'error')
            }
        }
    }

    const openSettings = () => {
        if (chrome.runtime.openOptionsPage) {
            chrome.runtime.openOptionsPage()
        } else {
            window.open(chrome.runtime.getURL('src/popup/index.html'), '_blank')
        }
    }

    if (!videoId) return null

    return (
        <div className="tubewiki-export-bar">
            <div className="logo">
                <img
                    src={chrome.runtime.getURL('logo.png')}
                    alt="TubeWiki"
                    width="32"
                    height="32"
                    style={{ borderRadius: '6px', objectFit: 'contain' }}
                />
                <span>YouTube Summary</span>
            </div>

            <div className="export-buttons">
                <button
                    onClick={handleExport}
                    title="Export to Notion"
                    disabled={loading}
                >
                    <IconNotion />
                </button>

                <div style={{ width: '1px', height: '24px', background: '#e0e0e0', margin: '0 4px' }} />

                <button
                    onClick={openSettings}
                    title="Settings"
                >
                    <IconSettings />
                </button>
                <button
                    title="Collapse"
                >
                    <IconChevronDown />
                </button>
            </div>

            {loading && (
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <span>{loadingText}</span>
                </div>
            )}

            {notification && (
                <div className={`notification ${notification.type}`}>
                    {notification.type === 'success' && '✅ '}
                    {notification.type === 'error' && '❌ '}
                    {notification.type === 'warning' && '⚠️ '}
                    {notification.type === 'info' && 'ℹ️ '}
                    {notification.message}
                </div>
            )}
        </div>
    )
}

export default ExportBar
