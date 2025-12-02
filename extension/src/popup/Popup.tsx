import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Login } from '../components/Login'
import { api } from '../lib/api'
import type { Note } from '../lib/api'
import '../index.css'

function Popup() {
  const [session, setSession] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [currentUrl, setCurrentUrl] = useState<string>('')
  const [note, setNote] = useState<Note | null>(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const init = async () => {
      try {
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

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event: string, session: any) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])



  const handleCreateNote = async () => {
    if (!currentUrl) return
    setProcessing(true)
    setError(null)
    try {
      const res = await api.createNote(currentUrl)
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
        // Don't stop polling on transient error?
      }
    }, 2000)
  }

  if (loading) return <div className="p-4">Loading...</div>

  if (!session) {
    return <Login onLogin={() => { }} />
  }

  return (
    <div className="w-full h-screen bg-gray-50 p-4 overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-xl font-bold text-gray-900">TubeWiki</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={async () => {
              try {
                const res = await api.createCheckoutSession()
                if (res.checkout_url) {
                  window.open(res.checkout_url, '_blank')
                }
              } catch (e) {
                console.error(e)
                alert('Failed to start checkout')
              }
            }}
            className="text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-1 rounded hover:opacity-90 font-medium"
          >
            Upgrade
          </button>
          <button
            onClick={() => supabase.auth.signOut()}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Sign Out
          </button>
        </div>
      </div>

      {!note && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Current Video</h3>
            <p className="text-sm text-gray-900 truncate">{currentUrl}</p>
          </div>

          <button
            onClick={handleCreateNote}
            disabled={processing || !currentUrl.includes('youtube.com')}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {processing ? 'Generating...' : 'Generate Study Guide'}
          </button>

          {error && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg">
              {error}
            </div>
          )}
        </div>
      )}

      {note && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className={`px-2 py-1 text-xs rounded-full ${note.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
              note.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                'bg-blue-100 text-blue-800'
              }`}>
              {note.status}
            </span>
            {note.status === 'COMPLETED' && (
              <button
                onClick={() => setNote(null)}
                className="text-xs text-blue-600 hover:underline"
              >
                New Note
              </button>
            )}
          </div>

          {note.status === 'PROCESSING' && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-sm text-gray-500">Analyzing video content...</p>
            </div>
          )}

          {note.status === 'COMPLETED' && (
            <div className="bg-white rounded-lg shadow-sm border p-4 prose prose-sm max-w-none">
              <h2 className="text-lg font-bold mb-2">{note.title}</h2>
              <div className="text-sm text-gray-700 whitespace-pre-wrap">
                {note.content?.substring(0, 300)}...
              </div>
              {/* If we had Notion URL, we'd link it here */}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Popup
