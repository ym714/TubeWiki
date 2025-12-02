import { useState, useEffect } from 'react'
import { storage, AppSettings } from '../lib/storage'

const Settings = () => {
    const [settings, setSettings] = useState<AppSettings>({})
    const [status, setStatus] = useState<string>('')

    useEffect(() => {
        storage.get().then(setSettings)
    }, [])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setSettings(prev => ({ ...prev, [name]: value }))
    }

    const handleSave = async () => {
        await storage.set(settings)
        setStatus('Settings saved!')
        setTimeout(() => setStatus(''), 2000)
    }

    return (
        <div className="settings-container">
            <h2>Integrations</h2>

            <div className="integration-section">
                <h3>Notion</h3>
                <div className="form-group">
                    <label>Integration Token</label>
                    <input
                        type="password"
                        name="notionToken"
                        value={settings.notionToken || ''}
                        onChange={handleChange}
                        placeholder="secret_..."
                    />
                </div>
                <div className="form-group">
                    <label>Page ID (Parent)</label>
                    <input
                        type="text"
                        name="notionPageId"
                        value={settings.notionPageId || ''}
                        onChange={handleChange}
                        placeholder="32-char ID"
                    />
                </div>
            </div>

            <div className="integration-section">
                <h3>GitHub</h3>
                <div className="form-group">
                    <label>Personal Access Token</label>
                    <input
                        type="password"
                        name="githubToken"
                        value={settings.githubToken || ''}
                        onChange={handleChange}
                        placeholder="ghp_..."
                    />
                </div>
                <div className="form-group">
                    <label>Repository (owner/repo)</label>
                    <input
                        type="text"
                        name="githubRepo"
                        value={settings.githubRepo || ''}
                        onChange={handleChange}
                        placeholder="username/repo"
                    />
                </div>
            </div>

            <div className="integration-section">
                <h3>Obsidian</h3>
                <div className="form-group">
                    <label>Vault Name</label>
                    <input
                        type="text"
                        name="obsidianVaultName"
                        value={settings.obsidianVaultName || ''}
                        onChange={handleChange}
                        placeholder="My Vault"
                    />
                </div>
            </div>

            <button onClick={handleSave} className="save-button">
                Save Settings
            </button>

            {status && <div className="status-message">{status}</div>}

            <style>{`
        .settings-container {
          padding: 16px;
          min-width: 300px;
        }
        .integration-section {
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 1px solid #eee;
        }
        h3 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #333;
        }
        .form-group {
          margin-bottom: 12px;
        }
        label {
          display: block;
          margin-bottom: 4px;
          font-size: 12px;
          color: #666;
        }
        input {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          box-sizing: border-box;
        }
        .save-button {
          width: 100%;
          padding: 10px;
          background: #065fd4;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 600;
        }
        .save-button:hover {
          background: #0556bf;
        }
        .status-message {
          margin-top: 12px;
          text-align: center;
          color: #28a745;
          font-size: 14px;
        }
      `}</style>
        </div>
    )
}

export default Settings
