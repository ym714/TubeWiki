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
const injectExportBar = async () => {
    try {
        if (!chrome.runtime?.id) return
    } catch {
        return
    }

    // 既に存在する場合は何もしない
    if (document.getElementById('tubewiki-export-bar-root')) {
        return
    }

    // 動画ページでない場合は何もしない
    if (!isYouTubeWatch()) {
        return
    }

    // サイドバー要素を探す（最大10秒待機）
    const findSidebar = (): Promise<Element | null> => {
        return new Promise((resolve) => {
            const sidebar = document.querySelector('#secondary')
            if (sidebar) {
                resolve(sidebar)
                return
            }

            const observer = new MutationObserver((_, obs) => {
                const element = document.querySelector('#secondary')
                if (element) {
                    obs.disconnect()
                    resolve(element)
                }
            })

            observer.observe(document.body, {
                childList: true,
                subtree: true
            })

            // タイムアウト
            setTimeout(() => {
                observer.disconnect()
                resolve(null)
            }, 10000)
        })
    }

    const sidebar = await findSidebar()
    if (!sidebar) {
        console.log('TubeWiki: Sidebar not found')
        return
    }

    // コンテナを作成
    const container = document.createElement('div')
    container.id = 'tubewiki-export-bar-root'

    // サイドバーの先頭に挿入
    sidebar.prepend(container)

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
    document.addEventListener('DOMContentLoaded', () => injectExportBar())
} else {
    injectExportBar()
}

// YouTube SPAの遷移を監視
try {
    if (chrome.runtime?.id) {
        let lastUrl = location.href
        new MutationObserver(() => {
            try {
                if (!chrome.runtime?.id) return

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
            } catch (e) {
                // Ignore context invalidation
            }
        }).observe(document, { subtree: true, childList: true })
    }
} catch (e) {
    // Ignore context invalidation
}
