

const init = async () => {
    console.log('[TubeWiki] Notion content script loaded')

    // Check if we have pending content to paste
    // We use chrome.storage.local directly to avoid importing dependencies that might break in content script
    const content = await new Promise<string | null>((resolve) => {
        try {
            chrome.storage.local.get('pending_notion_paste', (result) => {
                if (chrome.runtime.lastError) {
                    console.error('[TubeWiki] Storage error:', chrome.runtime.lastError)
                    resolve(null)
                } else {
                    resolve((result?.pending_notion_paste as string) || null)
                }
            })
        } catch (e) {
            console.error('[TubeWiki] Failed to access storage:', e)
            resolve(null)
        }
    })

    if (!content) {
        console.log('[TubeWiki] No pending content found')
        return
    }

    console.log('[TubeWiki] Found pending content, attempting to paste...')

    // Wait for the editor to be ready
    // Notion structure is complex. We look for the main content editable area.
    // Try multiple selectors
    const getEditor = () => {
        return document.querySelector('.notion-page-content') ||
            document.querySelector('[contenteditable="true"]')
    }

    let attempts = 0
    const maxAttempts = 20

    const tryPaste = async () => {
        const editor = getEditor()

        if (!editor && attempts < maxAttempts) {
            attempts++
            console.log(`[TubeWiki] Editor not found, retrying (${attempts}/${maxAttempts})...`)
            setTimeout(tryPaste, 500)
            return
        }

        if (!editor) {
            console.error('[TubeWiki] Could not find Notion editor after multiple attempts')
            alert('TubeWiki: Failed to find Notion editor. Please paste manually.')
            return
        }

        console.log('[TubeWiki] Editor found, focusing...')

        // Find the specific contenteditable element
        const contentEditable = (editor.querySelector('[contenteditable="true"]') as HTMLElement) || (editor as HTMLElement)

        if (contentEditable) {
            contentEditable.focus()
            // Ensure focus is really there
            await new Promise(r => setTimeout(r, 200))

            try {
                // Method 1: Try to set innerText directly
                console.log('[TubeWiki] Attempting direct text insertion...')

                // Clear existing content
                contentEditable.innerText = ''

                // Insert content
                contentEditable.innerText = content

                // Trigger input event to notify Notion
                const inputEvent = new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: content
                })
                contentEditable.dispatchEvent(inputEvent)

                // Also trigger change event
                const changeEvent = new Event('change', { bubbles: true })
                contentEditable.dispatchEvent(changeEvent)

                console.log('[TubeWiki] ✅ Content inserted successfully!')
                showToast('✅ Content pasted automatically!')
                finishPaste()

            } catch (e) {
                console.error('[TubeWiki] Direct insertion failed:', e)

                // Fallback: Copy to clipboard and show instruction
                try {
                    await navigator.clipboard.writeText(content)
                    showToast('📋 Content copied! Press Cmd+V to paste.')
                    finishPaste(false)
                } catch (clipError) {
                    console.error('[TubeWiki] Clipboard fallback also failed:', clipError)
                    showToast('❌ Please reload and try again.')
                }
            }
        }
    }

    const finishPaste = (clearStorage = true) => {
        if (clearStorage) {
            chrome.storage.local.remove('pending_notion_paste')
        }
    }

    const showToast = (message: string) => {
        const toast = document.createElement('div')
        toast.style.position = 'fixed'
        toast.style.bottom = '20px'
        toast.style.right = '20px'
        toast.style.backgroundColor = '#065fd4'
        toast.style.color = 'white'
        toast.style.padding = '12px 24px'
        toast.style.borderRadius = '8px'
        toast.style.zIndex = '9999'
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
        toast.style.fontFamily = 'sans-serif'
        toast.textContent = message
        document.body.appendChild(toast)
        setTimeout(() => toast.remove(), 5000)
    }

    // Start trying to paste
    tryPaste()
}

init()
