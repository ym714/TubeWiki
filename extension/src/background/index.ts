import { supabase } from '../lib/supabase'



// Listen for installation
chrome.runtime.onInstalled.addListener(() => {

})

// Listen for auth changes (if needed for other background tasks)
supabase.auth.onAuthStateChange((event) => {


    if (event === 'SIGNED_OUT') {
        // Clear any local state if needed
        chrome.storage.local.clear()
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
