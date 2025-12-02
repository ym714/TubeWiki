import { Note } from '../../types/note'
import { storage } from '../../lib/storage'
import { sanitizeFilename } from '../../utils/format'

export const exportToGitHub = async (note: Note): Promise<string> => {
    const settings = await storage.get()

    if (!settings.githubToken || !settings.githubRepo) {
        throw new Error('GitHub integration not configured')
    }

    const title = note.title || 'Untitled Note'
    const content = note.content || ''
    const videoUrl = note.video_url

    // Format content with header
    const fileContent = `# ${title}\n\nURL: ${videoUrl}\n\n${content}`

    // Generate filename: YYYY-MM-DD-Title.md
    const date = new Date().toISOString().split('T')[0]
    const safeTitle = sanitizeFilename(title).replace(/\s+/g, '-')
    const filename = `${date}-${safeTitle}.md`

    // Base64 encode content (handle UTF-8)
    const contentEncoded = btoa(unescape(encodeURIComponent(fileContent)))

    const response = await fetch(`https://api.github.com/repos/${settings.githubRepo}/contents/${filename}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${settings.githubToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify({
            message: `Add note: ${title}`,
            content: contentEncoded
        })
    })

    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`GitHub API Error: ${errorData.message || response.statusText}`)
    }

    const data = await response.json()
    return data.html_url // Return the URL of the created file
}
