import { Note } from '../../types/note'
import { storage } from '../../lib/storage'

export const exportToNotion = async (note: Note): Promise<string> => {
    const settings = await storage.get()

    if (!settings.notionToken || !settings.notionPageId) {
        throw new Error('Notion integration not configured')
    }

    const title = note.title || 'Untitled Note'
    const content = note.content || ''
    const videoUrl = note.video_url

    // Notion Block Object Construction
    // Note: Splitting content into chunks because Notion blocks have a 2000 char limit
    const contentChunks = content.match(/.{1,2000}/g) || []

    const children = [
        {
            object: 'block',
            type: 'embed',
            embed: {
                url: videoUrl
            }
        },
        {
            object: 'block',
            type: 'heading_2',
            heading_2: {
                rich_text: [{ type: 'text', text: { content: 'Summary' } }]
            }
        },
        ...contentChunks.map(chunk => ({
            object: 'block',
            type: 'paragraph',
            paragraph: {
                rich_text: [{ type: 'text', text: { content: chunk } }]
            }
        }))
    ]

    const response = await fetch('https://api.notion.com/v1/pages', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${settings.notionToken}`,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        },
        body: JSON.stringify({
            parent: { page_id: settings.notionPageId },
            properties: {
                title: {
                    title: [{ type: 'text', text: { content: title } }]
                }
            },
            children: children
        })
    })

    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`Notion API Error: ${errorData.message || response.statusText}`)
    }

    const data = await response.json()
    return data.url // Return the URL of the created page
}
