import { Note } from '../../types/note'
import { storage } from '../../lib/storage'
import { sanitizeFilename } from '../../utils/format'

export const exportToObsidian = async (note: Note): Promise<void> => {
    const settings = await storage.get()

    // Vault name is optional but recommended
    const vaultName = settings.obsidianVaultName || ''

    const title = note.title || 'Untitled Note'
    const content = note.content || ''
    const videoUrl = note.video_url

    // Format content
    const fileContent = `# ${title}\n\nURL: ${videoUrl}\n\n${content}`

    // Encode parameters
    const encodedTitle = encodeURIComponent(sanitizeFilename(title))
    const encodedContent = encodeURIComponent(fileContent)
    const encodedVault = vaultName ? `&vault=${encodeURIComponent(vaultName)}` : ''

    // Construct URI
    // obsidian://new?name=my%20note&content=...&vault=...
    const uri = `obsidian://new?name=${encodedTitle}&content=${encodedContent}${encodedVault}`

    // Open URI
    window.open(uri, '_self')
}
