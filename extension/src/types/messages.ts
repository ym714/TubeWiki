/**
 * Message types for communication between content scripts, popup, and background script
 */
export enum MessageType {
    API_PROXY_REQUEST = 'API_PROXY_REQUEST',
    GET_AUTH_STATUS = 'GET_AUTH_STATUS'
}

/**
 * API Proxy Request sent to background script
 */
export interface ApiProxyRequest {
    type: MessageType.API_PROXY_REQUEST
    url: string
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
    headers?: Record<string, string>
    body?: string
}

/**
 * API Proxy Response from background script
 */
export interface ApiProxyResponse {
    ok: boolean
    status: number
    data?: any
    error?: string
}

/**
 * Message for getting auth status
 */
export interface GetAuthStatusMessage {
    type: MessageType.GET_AUTH_STATUS
}

/**
 * Union type of all possible messages
 */
export type RuntimeMessage = ApiProxyRequest | GetAuthStatusMessage
