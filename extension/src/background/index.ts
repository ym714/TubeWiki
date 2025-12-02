import { getSupabase } from '../lib/supabase'

// Listen for auth changes to update badge or context menu
const supabase = getSupabase()

supabase.auth.onAuthStateChange((event) => {
    if (event === 'SIGNED_IN') {
        chrome.action.setBadgeText({ text: '' })
    } else if (event === 'SIGNED_OUT') {
        chrome.action.setBadgeText({ text: '!' })
        chrome.action.setBadgeBackgroundColor({ color: '#F00' })
    }
})

// Check initial session
supabase.auth.getSession().then(({ data: { session } }) => {
    if (!session) {
        chrome.action.setBadgeText({ text: '!' })
        chrome.action.setBadgeBackgroundColor({ color: '#F00' })
    }
})

// Example: Listen for messages from Content Script or Popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === 'GET_AUTH_STATUS') {
        supabase.auth.getSession().then(({ data: { session } }) => {
            sendResponse({ session })
        })
        return true // Indicates async response
    }
})
