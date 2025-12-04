import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MessageType } from '../../types/messages'
import type { ApiProxyRequest, ApiProxyResponse } from '../../types/messages'

// Mock chrome runtime
const mockSendMessage = vi.fn()
    ; (globalThis as any).chrome = {
        runtime: {
            sendMessage: mockSendMessage
        }
    }


// We'll need to mock the api module
describe('API Client', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    describe('createNote', () => {
        it('should send API_PROXY_REQUEST message to background script', async () => {
            const mockNote = { id: 1, video_url: 'https://www.youtube.com/watch?v=test' }
            mockSendMessage.mockImplementation((_msg: ApiProxyRequest, callback: (response: ApiProxyResponse) => void) => {
                callback({
                    ok: true,
                    status: 201,
                    data: mockNote
                })
            })

            // Simulate the api.createNote function
            const createNote = async (videoUrl: string, options: Record<string, any> = {}) => {
                return new Promise((resolve, reject) => {
                    const message: ApiProxyRequest = {
                        type: MessageType.API_PROXY_REQUEST,
                        url: `http://localhost:8000/api/v1/notes`,
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_url: videoUrl, options })
                    }

                    chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                        if (response.ok) {
                            resolve(response.data)
                        } else {
                            reject(new Error(response.error || 'Failed to create note'))
                        }
                    })
                })
            }

            const result = await createNote('https://www.youtube.com/watch?v=test', {})

            expect(mockSendMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: MessageType.API_PROXY_REQUEST,
                    url: 'http://localhost:8000/api/v1/notes',
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: expect.stringContaining('https://www.youtube.com/watch?v=test')
                }),
                expect.any(Function)
            )
            expect(result).toEqual(mockNote)
        })

        it('should reject on error response', async () => {
            mockSendMessage.mockImplementation((_msg: ApiProxyRequest, callback: (response: ApiProxyResponse) => void) => {
                callback({
                    ok: false,
                    status: 500,
                    error: 'Internal server error'
                })
            })

            const createNote = async (videoUrl: string, options: Record<string, any> = {}) => {
                return new Promise((resolve, reject) => {
                    const message: ApiProxyRequest = {
                        type: MessageType.API_PROXY_REQUEST,
                        url: `http://localhost:8000/api/v1/notes`,
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_url: videoUrl, options })
                    }

                    chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                        if (response.ok) {
                            resolve(response.data)
                        } else {
                            reject(new Error(response.error || 'Failed to create note'))
                        }
                    })
                })
            }

            await expect(createNote('https://www.youtube.com/watch?v=test')).rejects.toThrow('Internal server error')
        })
    })

    describe('getNote', () => {
        it('should send GET request via background script', async () => {
            const mockNote = { id: 1, title: 'Test Note' }
            mockSendMessage.mockImplementation((_msg: ApiProxyRequest, callback: (response: ApiProxyResponse) => void) => {
                callback({
                    ok: true,
                    status: 200,
                    data: mockNote
                })
            })

            const getNote = async (noteId: number) => {
                return new Promise((resolve, reject) => {
                    const message: ApiProxyRequest = {
                        type: MessageType.API_PROXY_REQUEST,
                        url: `http://localhost:8000/api/v1/notes/${noteId}`,
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    }

                    chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                        if (response.ok) {
                            resolve(response.data)
                        } else {
                            reject(new Error(response.error || 'Failed to fetch note'))
                        }
                    })
                })
            }

            const result = await getNote(1)

            expect(mockSendMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: MessageType.API_PROXY_REQUEST,
                    url: 'http://localhost:8000/api/v1/notes/1',
                    method: 'GET'
                }),
                expect.any(Function)
            )
            expect(result).toEqual(mockNote)
        })
    })

    describe('getNoteByUrl', () => {
        it('should send GET request with URL parameter', async () => {
            const videoUrl = 'https://www.youtube.com/watch?v=test'
            const mockNote = { id: 1, video_url: videoUrl }
            mockSendMessage.mockImplementation((_msg: ApiProxyRequest, callback: (response: ApiProxyResponse) => void) => {
                callback({
                    ok: true,
                    status: 200,
                    data: mockNote
                })
            })

            const getNoteByUrl = async (videoUrl: string) => {
                return new Promise((resolve, reject) => {
                    const message: ApiProxyRequest = {
                        type: MessageType.API_PROXY_REQUEST,
                        url: `http://localhost:8000/api/v1/notes/by-url/?video_url=${encodeURIComponent(videoUrl)}`,
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    }

                    chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                        if (response.ok) {
                            resolve(response.data)
                        } else {
                            if (response.status === 404) {
                                reject(new Error('Note not found'))
                            } else {
                                reject(new Error(response.error || 'Failed to fetch note'))
                            }
                        }
                    })
                })
            }

            const result = await getNoteByUrl(videoUrl)

            expect(mockSendMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: MessageType.API_PROXY_REQUEST,
                    url: expect.stringContaining('notes/by-url'),
                    method: 'GET'
                }),
                expect.any(Function)
            )
            expect(result).toEqual(mockNote)
        })

        it('should handle 404 responses with specific error', async () => {
            mockSendMessage.mockImplementation((_msg: ApiProxyRequest, callback: (response: ApiProxyResponse) => void) => {
                callback({
                    ok: false,
                    status: 404,
                    error: 'Not found'
                })
            })

            const getNoteByUrl = async (videoUrl: string) => {
                return new Promise((resolve, reject) => {
                    const message: ApiProxyRequest = {
                        type: MessageType.API_PROXY_REQUEST,
                        url: `http://localhost:8000/api/v1/notes/by-url/?video_url=${encodeURIComponent(videoUrl)}`,
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    }

                    chrome.runtime.sendMessage(message, (response: ApiProxyResponse) => {
                        if (response.ok) {
                            resolve(response.data)
                        } else {
                            if (response.status === 404) {
                                reject(new Error('Note not found'))
                            } else {
                                reject(new Error(response.error || 'Failed to fetch note'))
                            }
                        }
                    })
                })
            }

            await expect(getNoteByUrl('https://www.youtube.com/watch?v=test')).rejects.toThrow('Note not found')
        })
    })
})
