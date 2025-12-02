import { describe, it, expect } from 'vitest'
import { formatTime, sanitizeFilename } from './format'

describe('formatTime', () => {
    it('formats seconds to MM:SS', () => {
        expect(formatTime(0)).toBe('0:00')
        expect(formatTime(59)).toBe('0:59')
        expect(formatTime(60)).toBe('1:00')
        expect(formatTime(3599)).toBe('59:59')
    })

    it('formats seconds to H:MM:SS', () => {
        expect(formatTime(3600)).toBe('1:00:00')
        expect(formatTime(3661)).toBe('1:01:01')
        expect(formatTime(7322)).toBe('2:02:02')
    })
})

describe('sanitizeFilename', () => {
    it('removes invalid characters', () => {
        expect(sanitizeFilename('test.txt')).toBe('test.txt')
        expect(sanitizeFilename('test/file.txt')).toBe('testfile.txt')
        expect(sanitizeFilename('test:file.txt')).toBe('testfile.txt')
        expect(sanitizeFilename('test*file.txt')).toBe('testfile.txt')
    })

    it('trims whitespace', () => {
        expect(sanitizeFilename(' test.txt ')).toBe('test.txt')
    })
})
