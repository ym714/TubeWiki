import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import type { Note } from '../types/note'
import { copyToClipboard } from './exporters/clipboard'
import { downloadAsMarkdown } from './exporters/download'

const ExportBar = () => {
    const [videoId, setVideoId] = useState<string | null>(null)
    const [note, setNote] = useState<Note | null>(null)
    const [loading, setLoading] = useState(false)
    const [notification, setNotification] = useState<string | null>(null)

    useEffect(() => {
        // URLからvideo IDを取得
        const params = new URLSearchParams(window.location.search)
        const id = params.get('v')
        setVideoId(id)

        // 既存のノートを確認
        if (id) {
            const url = `https://www.youtube.com/watch?v=${id}`
            api.getNoteByUrl(url)
                .then(setNote)
                .catch(() => setNote(null))
        }
    }, [])

    const showNotification = (message: string) => {
        setNotification(message)
        setTimeout(() => setNotification(null), 3000)
    }

    const ensureNote = async (): Promise<Note> => {
        if (note) return note

        setLoading(true)
        try {
            const url = `https://www.youtube.com/watch?v=${videoId}`
            const newNote = await api.createNote(url)

            // ポーリングで完了を待つ
            let attempts = 0
            while (attempts < 30) {
                await new Promise(resolve => setTimeout(resolve, 2000))
                try {
                    const completedNote = await api.getNote(newNote.id)
                    if (completedNote.status === 'COMPLETED') {
                        setNote(completedNote)
                        setLoading(false)
                        return completedNote
                    }
                } catch (error) {
                    // まだ処理中
                }
                attempts++
            }
            throw new Error('Timeout waiting for note generation')
        } catch (error) {
            setLoading(false)
            throw error
        }
    }

    const handleExport = async (type: 'clipboard' | 'download' | 'notion' | 'github' | 'obsidian') => {
        try {
            const currentNote = await ensureNote()

            switch (type) {
                case 'clipboard':
                    await copyToClipboard(currentNote)
                    showNotification('✅ Copied to clipboard!')
                    break
                case 'download':
                    await downloadAsMarkdown(currentNote)
                    showNotification('✅ Downloaded!')
                    break
                case 'notion':
                    if (!(await storage.isConfigured('notion'))) {
                        showNotification('⚠️ Please configure Notion in extension settings')
                        return
                    }
                    showNotification('⏳ Exporting to Notion...')
                    const notionUrl = await exportToNotion(currentNote)
                    showNotification('✅ Exported to Notion!')
                    window.open(notionUrl, '_blank')
                    break
                case 'github':
                    if (!(await storage.isConfigured('github'))) {
                        showNotification('⚠️ Please configure GitHub in extension settings')
                        return
                    }
                    showNotification('⏳ Exporting to GitHub...')
                    const githubUrl = await exportToGitHub(currentNote)
                    showNotification('✅ Exported to GitHub!')
                    window.open(githubUrl, '_blank')
                    break
                case 'obsidian':
                    // Obsidian doesn't strictly require config if vault name is not used, but let's check if user wants to set it
                    // Actually, let's allow it without config, but warn if vault name is missing?
                    // For now, simple check:
                    // if (!(await storage.isConfigured('obsidian'))) { ... }
                    // But maybe we just run it.
                    await exportToObsidian(currentNote)
                    showNotification('✅ Opened in Obsidian!')
                    break
            }
        } catch (error) {
            console.error(error)
            showNotification('❌ Error: ' + (error as Error).message)
        }
    }

    if (!videoId) return null

    return (
        <div className="tubewiki-export-bar">
            <div className="logo">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <rect width="32" height="32" rx="6" fill="#065fd4" />
                    <path d="M16 10L22 16L16 22L10 16L16 10Z" fill="white" />
                </svg>
                <span>YouTube Summary</span>
            </div>

            <div className="export-buttons">
                <button
                    onClick={() => handleExport('clipboard')}
                    title="Copy to Clipboard"
                    disabled={loading}
                >
                    📋
                </button>
                <button
                    onClick={() => handleExport('download')}
                    title="Download as Markdown"
                    disabled={loading}
                >
                    💾
                </button>
                <button
                    onClick={() => handleExport('notion')}
                    title="Export to Notion"
                    disabled={loading}
                >
                    📝
                </button>
                <button
                    onClick={() => handleExport('github')}
                    title="Export to GitHub"
                    disabled={loading}
                >
                    🐙
                </button>
                <button
                    onClick={() => handleExport('obsidian')}
                    title="Export to Obsidian"
                    disabled={loading}
                >
                    📓
                </button>
            </div>

            {loading && (
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <span>Generating summary...</span>
                </div>
            )}

            {notification && (
                <div className="notification">
                    {notification}
                </div>
            )}
        </div>
    )
}

export default ExportBar
