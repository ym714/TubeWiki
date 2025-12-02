import { createRoot } from 'react-dom/client'
import Overlay from './Overlay'
import style from './style.css?inline'



// Function to inject the overlay
const injectOverlay = () => {
    // Check if already injected
    if (document.getElementById('flashnote-ai-root')) return

    // 1. Find target element (YouTube specific)
    // secondary-inner is the sidebar, but we might want it elsewhere.
    // For now, let's append to body or a specific container.
    const target = document.body

    if (target) {
        // 2. Create container
        const container = document.createElement('div')
        container.id = 'flashnote-ai-root'
        target.appendChild(container)

        // 3. Create Shadow Root
        const shadowRoot = container.attachShadow({ mode: 'open' })

        // 4. Inject styles
        const styleElement = document.createElement('style')
        styleElement.textContent = style
        shadowRoot.appendChild(styleElement)

        // 5. Mount React
        createRoot(shadowRoot).render(<Overlay />)
    }
}

// Initial injection
injectOverlay()

// Handle navigation (YouTube is SPA)
// Observer or interval might be needed if the target element is dynamic
const observer = new MutationObserver(() => {
    injectOverlay()
})

observer.observe(document.body, { childList: true, subtree: true })
