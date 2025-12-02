import { createRoot } from 'react-dom/client'
import ExportBar from './ExportBar'
import ErrorBoundary from '../components/ErrorBoundary'
import style from './style.css?inline'

// YouTubeの動画ページでのみ実行
const isYouTubeWatch = () => {
    return window.location.hostname === 'www.youtube.com' &&
        window.location.pathname === '/watch'
}

// Export Barを注入
const injectExportBar = () => {
    // 既に存在する場合は何もしない
    if (document.getElementById('tubewiki-export-bar-root')) {
        return
    }

    // 動画ページでない場合は何もしない
    if (!isYouTubeWatch()) {
        return
    }

    // コンテナを作成
    const container = document.createElement('div')
    container.id = 'tubewiki-export-bar-root'
    document.body.appendChild(container)

    // Shadow Rootを作成（スタイルの隔離）
    const shadowRoot = container.attachShadow({ mode: 'open' })

    // スタイルを注入
    const styleElement = document.createElement('style')
    styleElement.textContent = style
    shadowRoot.appendChild(styleElement)

    // Reactアプリをマウント（ErrorBoundaryでラップ）
    const root = createRoot(shadowRoot)
    root.render(
        <ErrorBoundary>
            <ExportBar />
        </ErrorBoundary>
    )
}

// ページ読み込み時に実行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectExportBar)
} else {
    injectExportBar()
}

// YouTube SPAの遷移を監視
let lastUrl = location.href
new MutationObserver(() => {
    const url = location.href
    if (url !== lastUrl) {
        lastUrl = url
        if (isYouTubeWatch()) {
            injectExportBar()
        } else {
            // 動画ページ以外では削除
            const container = document.getElementById('tubewiki-export-bar-root')
            if (container) {
                container.remove()
            }
        }
    }
}).observe(document, { subtree: true, childList: true })
