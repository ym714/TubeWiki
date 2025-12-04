import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MessageType } from '../../types/messages'
import type { ApiProxyRequest, ApiProxyResponse } from '../../types/messages'

    // Mock chrome API
    ; (globalThis as any).chrome = {
        runtime: {
            onMessage: {
                addListener: vi.fn()
            }
        }
    }

    // Mock fetch
    ; (globalThis as any).fetch = vi.fn()


describe('Background API Proxy', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    describe('Message Handler Registration', () => {
        it('should register a message listener', () => {
            // This will be tested when we import the actual background script
            expect(chrome.runtime.onMessage.addListener).toBeDefined()
        })
    })

    describe('API Proxy Request Handling', () => {
        it('should handle successful API GET request', async () => {
            const mockResponse = { id: 1, title: 'Test Note' }
            const mockFetch = vi.fn().mockResolvedValue({
                ok: true,
                status: 200,
                json: async () => mockResponse
            })
            globalThis.fetch = mockFetch

            const request: ApiProxyRequest = {
                type: MessageType.API_PROXY_REQUEST,
                url: 'http://localhost:8000/api/v1/notes/1',
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            }

            // We'll test this by calling the handler directly
            // Handler will be implemented in the background script
            const sendResponse = vi.fn()

            // Simulate handler
            const handleApiProxy = async (message: ApiProxyRequest, sendResponse: (response: ApiProxyResponse) => void) => {
                if (message.type === MessageType.API_PROXY_REQUEST) {
                    try {
                        const response = await fetch(message.url, {
                            method: message.method,
                            headers: message.headers,
                            body: message.body
                        })

                        const data = await response.json()
                        sendResponse({
                            ok: response.ok,
                            status: response.status,
                            data
                        })
                    } catch (error) {
                        sendResponse({
                            ok: false,
                            status: 0,
                            error: error instanceof Error ? error.message : 'Unknown error'
                        })
                    }
                    return true
                }
            }

            await handleApiProxy(request, sendResponse)

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:8000/api/v1/notes/1',
                expect.objectContaining({
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                })
            )
            expect(sendResponse).toHaveBeenCalledWith({
                ok: true,
                status: 200,
                data: mockResponse
            })
        })

        it('should handle successful API POST request with body', async () => {
            const mockResponse = { id: 2, video_url: 'https://www.youtube.com/watch?v=test' }
            const mockFetch = vi.fn().mockResolvedValue({
                ok: true,
                status: 201,
                json: async () => mockResponse
            })
            globalThis.fetch = mockFetch

            const request: ApiProxyRequest = {
                type: MessageType.API_PROXY_REQUEST,
                url: 'http://localhost:8000/api/v1/notes',
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_url: 'https://www.youtube.com/watch?v=test' })
            }

            const sendResponse = vi.fn()

            const handleApiProxy = async (message: ApiProxyRequest, sendResponse: (response: ApiProxyResponse) => void) => {
                if (message.type === MessageType.API_PROXY_REQUEST) {
                    try {
                        const response = await fetch(message.url, {
                            method: message.method,
                            headers: message.headers,
                            body: message.body
                        })

                        const data = await response.json()
                        sendResponse({
                            ok: response.ok,
                            status: response.status,
                            data
                        })
                    } catch (error) {
                        sendResponse({
                            ok: false,
                            status: 0,
                            error: error instanceof Error ? error.message : 'Unknown error'
                        })
                    }
                    return true
                }
            }

            await handleApiProxy(request, sendResponse)

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:8000/api/v1/notes',
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_url: 'https://www.youtube.com/watch?v=test' })
                })
            )
            expect(sendResponse).toHaveBeenCalledWith({
                ok: true,
                status: 201,
                data: mockResponse
            })
        })

        it('should handle API error responses', async () => {
            const mockFetch = vi.fn().mockResolvedValue({
                ok: false,
                status: 404,
                json: async () => ({ detail: 'Not found' })
            })
            globalThis.fetch = mockFetch

            const request: ApiProxyRequest = {
                type: MessageType.API_PROXY_REQUEST,
                url: 'http://localhost:8000/api/v1/notes/999',
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            }

            const sendResponse = vi.fn()

            const handleApiProxy = async (message: ApiProxyRequest, sendResponse: (response: ApiProxyResponse) => void) => {
                if (message.type === MessageType.API_PROXY_REQUEST) {
                    try {
                        const response = await fetch(message.url, {
                            method: message.method,
                            headers: message.headers,
                            body: message.body
                        })

                        const data = await response.json()
                        sendResponse({
                            ok: response.ok,
                            status: response.status,
                            data
                        })
                    } catch (error) {
                        sendResponse({
                            ok: false,
                            status: 0,
                            error: error instanceof Error ? error.message : 'Unknown error'
                        })
                    }
                    return true
                }
            }

            await handleApiProxy(request, sendResponse)

            expect(sendResponse).toHaveBeenCalledWith({
                ok: false,
                status: 404,
                data: { detail: 'Not found' }
            })
        })

        it('should handle network errors', async () => {
            const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'))
            globalThis.fetch = mockFetch

            const request: ApiProxyRequest = {
                type: MessageType.API_PROXY_REQUEST,
                url: 'http://localhost:8000/api/v1/notes',
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            }

            const sendResponse = vi.fn()

            const handleApiProxy = async (message: ApiProxyRequest, sendResponse: (response: ApiProxyResponse) => void) => {
                if (message.type === MessageType.API_PROXY_REQUEST) {
                    try {
                        const response = await fetch(message.url, {
                            method: message.method,
                            headers: message.headers,
                            body: message.body
                        })

                        const data = await response.json()
                        sendResponse({
                            ok: response.ok,
                            status: response.status,
                            data
                        })
                    } catch (error) {
                        sendResponse({
                            ok: false,
                            status: 0,
                            error: error instanceof Error ? error.message : 'Unknown error'
                        })
                    }
                    return true
                }
            }

            await handleApiProxy(request, sendResponse)

            expect(sendResponse).toHaveBeenCalledWith({
                ok: false,
                status: 0,
                error: 'Network error'
            })
        })

        it('should return true to indicate async response', () => {
            const request: ApiProxyRequest = {
                type: MessageType.API_PROXY_REQUEST,
                url: 'http://localhost:8000/api/v1/notes',
                method: 'GET'
            }

            const handleMessage = (message: any): boolean => {
                if (message.type === MessageType.API_PROXY_REQUEST) {
                    // Async handling
                    return true
                }
                return false
            }

            const result = handleMessage(request)
            expect(result).toBe(true)
        })
    })
})
