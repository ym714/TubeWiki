const waitForElement = (selector: string, timeout = 10000): Promise<Element | null> => {
    return new Promise((resolve) => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector))
        }

        const observer = new MutationObserver(() => {
            if (document.querySelector(selector)) {
                resolve(document.querySelector(selector))
                observer.disconnect()
            }
        })

        observer.observe(document.body, {
            childList: true,
            subtree: true
        })

        setTimeout(() => {
            observer.disconnect()
            resolve(null)
        }, timeout)
    })
}

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
    // Notion uses contenteditable divs. The main one usually has class 'notion-page-content'
    // or we can look for the default block.
    const editorSelector = '.notion-page-content'
    const editor = await waitForElement(editorSelector)

    if (!editor) {
        console.error('[TubeWiki] Could not find Notion editor')
        return
    }

    // Give it a moment to fully settle
    await new Promise(r => setTimeout(r, 1000))

    try {
        // Focus the editor
        // We try to find the first text block
        const firstBlock = document.querySelector('[contenteditable="true"]') as HTMLElement
        if (firstBlock) {
            firstBlock.focus()

            // Use execCommand 'insertText' to simulate typing/pasting
            // This is deprecated but still widely supported and works for this use case
            // ensuring Notion's internal state updates correctly.
            document.execCommand('insertText', false, content)

            // Clear the storage so we don't paste again on reload
            chrome.storage.local.remove('pending_notion_paste')

            // Show success message
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
            toast.textContent = '✅ Pasted from TubeWiki'
            document.body.appendChild(toast)

            setTimeout(() => {
                toast.remove()
            }, 3000)
        } else {
            console.error('[TubeWiki] Could not find contenteditable element')
        }
    } catch (e) {
        console.error('[TubeWiki] Failed to paste content', e)
    }
}

init()
