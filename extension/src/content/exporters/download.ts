import type { Note } from '../../types/note'

export const downloadAsMarkdown = async (note: Note): Promise<void> => {
    const markdown = `# ${note.title ?? 'Untitled'}\n\n${note.content ?? ''}`
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)

    const filename = `${(note.title ?? 'untitled').replace(/[^a-z0-9]/gi, '-').toLowerCase()}.md`

    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)

    // メモリリーク防止
    setTimeout(() => URL.revokeObjectURL(url), 100)
}
