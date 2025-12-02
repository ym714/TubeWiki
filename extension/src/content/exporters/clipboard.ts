import type { Note } from '../../types/note'

export const copyToClipboard = async (note: Note): Promise<void> => {
    const markdown = `# ${note.title ?? 'Untitled'}\n\n${note.content ?? ''}`

    try {
        await navigator.clipboard.writeText(markdown)
    } catch (error) {
        // フォールバック: textareaを使用
        const textarea = document.createElement('textarea')
        textarea.value = markdown
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
    }
}
