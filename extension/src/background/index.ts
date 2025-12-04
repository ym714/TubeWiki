import { getSupabase } from '../lib/supabase'
import { MessageType } from '../types/messages'
import type { ApiProxyRequest, ApiProxyResponse, RuntimeMessage } from '../types/messages'

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

// Listen for messages from Content Script or Popup
chrome.runtime.onMessage.addListener((message: RuntimeMessage, _sender, sendResponse) => {
    // Handle API proxy requests
    if (message.type === MessageType.API_PROXY_REQUEST) {
        const apiRequest = message as ApiProxyRequest

        // Get the current Supabase session and add auth token
        supabase.auth.getSession().then(({ data: { session } }) => {
            // Prepare headers with auth token if available
            const headers = { ...apiRequest.headers }
            if (session?.access_token) {
                headers['Authorization'] = `Bearer ${session.access_token}`
            }

            // Perform the fetch request from background script (has host permissions)
            fetch(apiRequest.url, {
                method: apiRequest.method,
                headers: headers,
                body: apiRequest.body
            })
                .then(async (response) => {
                    const data = await response.json()
                    const apiResponse: ApiProxyResponse = {
                        ok: response.ok,
                        status: response.status,
                        data
                    }
                    sendResponse(apiResponse)
                })
                .catch((error) => {
                    const apiResponse: ApiProxyResponse = {
                        ok: false,
                        status: 0,
                        error: error instanceof Error ? error.message : 'Unknown error'
                    }
                    sendResponse(apiResponse)
                })
        }).catch((error) => {
            // If session retrieval fails, send error response
            const apiResponse: ApiProxyResponse = {
                ok: false,
                status: 0,
                error: `Failed to get auth session: ${error instanceof Error ? error.message : 'Unknown error'}`
            }
            sendResponse(apiResponse)
        })

        return true // Indicates async response
    }

    // Handle auth status requests
    if (message.type === MessageType.GET_AUTH_STATUS) {
        supabase.auth.getSession().then(({ data: { session } }) => {
            sendResponse({ session })
        })
        return true // Indicates async response
    }
})
