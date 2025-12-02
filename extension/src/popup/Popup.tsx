
import { useState, useEffect } from 'react'
import { getSupabase } from '../lib/supabase'

import { storage } from '../lib/storage'
import { api } from '../lib/api'
import type { Note } from '../lib/api'
import Settings from './Settings'
import { Login } from '../components/Login'
import '../index.css'

const Popup = () => {
  const [session, setSession] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [currentUrl, setCurrentUrl] = useState<string>('')
  const [note, setNote] = useState<Note | null>(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'home' | 'settings'>('home')

  useEffect(() => {
    const init = async () => {
      try {
        const supabase = getSupabase()
        // 1. Check Auth
        const { data: { session } } = await supabase.auth.getSession()
        setSession(session)

        if (session) {
          // 2. Get URL
          const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
          if (tabs[0]?.url) {
            const url = tabs[0].url
            setCurrentUrl(url)

            // 3. Check Existing Note
            if (url.includes('youtube.com')) {
              try {
                const existingNote = await api.getNoteByUrl(url)
                setNote(existingNote)
                if (existingNote.status === 'PENDING' || existingNote.status === 'PROCESSING') {
                  setProcessing(true)
                  pollNote(existingNote.id)
                }
              } catch (e) {
                // Ignore 404
              }
            }
          }
        }
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }

    init()

    const supabase = getSupabase()
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleCreateNote = async () => {
    if (!currentUrl) return
    setProcessing(true)
    setError(null)
    try {
      const settings = await storage.get()
      const options = {
        notion_token: settings.notionToken,
        notion_page_id: settings.notionPageId
      }
      const res = await api.createNote(currentUrl, options)
      pollNote(res.note_id)
    } catch (e: any) {
      setError(e.message)
      setProcessing(false)
    }
  }

  const pollNote = async (noteId: number) => {
    const interval = setInterval(async () => {
      try {
        const n = await api.getNote(noteId)
        setNote(n)
        if (n.status === 'COMPLETED' || n.status === 'FAILED') {
          clearInterval(interval)
          setProcessing(false)
        }
      } catch (e) {
        console.error(e)
      }
    }, 2000)
  }

  const handleLogout = async () => {
    const supabase = getSupabase()
    await supabase.auth.signOut()
  }

  if (loading) return <div className="p-4">Loading...</div>

  if (!session) {
    return <Login onLogin={() => { }} />
  }

  return (
    <div className="w-full h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex justify-between items-center shadow-sm z-10">
        <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span className="text-blue-600">▶</span> TubeWiki
        </h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab(activeTab === 'home' ? 'settings' : 'home')}
            className={`p-2 rounded-full hover:bg-gray-100 transition-colors ${activeTab === 'settings' ? 'bg-gray-100 text-blue-600' : 'text-gray-600'}`}
            title="Settings"
          >
            ⚙️
          </button>
          <button
            onClick={handleLogout}
            className="p-2 rounded-full hover:bg-gray-100 text-gray-600 transition-colors"
            title="Sign Out"
          >
            🚪
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'settings' ? (
          <Settings />
        ) : (
          <div className="space-y-4">
            {!note && (
              <div className="space-y-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Current Video</h3>
                  <p className="text-sm text-gray-900 truncate">{currentUrl}</p>
                </div>

                <button
                  onClick={handleCreateNote}
                  disabled={processing || !currentUrl.includes('youtube.com')}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                >
                  {processing ? 'Generating...' : 'Generate Study Guide'}
                </button>

                {error && (
                  <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                    {error}
                  </div>
                )}
              </div>
            )}

            {note && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs rounded-full font-medium ${note.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                    note.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                    {note.status}
                  </span>
                  {note.status === 'COMPLETED' && (
                    <button
                      onClick={() => setNote(null)}
                      className="text-xs text-blue-600 hover:underline font-medium"
                    >
                      New Note
                    </button>
                  )}
                </div>

                {note.status === 'PROCESSING' && (
                  <div className="text-center py-12 bg-white rounded-lg border border-dashed">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-sm text-gray-500">Analyzing video content...</p>
                    <p className="text-xs text-gray-400 mt-2">This may take a minute</p>
                  </div>
                )}

                {note.status === 'COMPLETED' && (
                  <div className="bg-white rounded-lg shadow-sm border p-4 prose prose-sm max-w-none">
                    <h2 className="text-lg font-bold mb-2 text-gray-900">{note.title}</h2>
                    <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {note.content?.substring(0, 300)}...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Popup

