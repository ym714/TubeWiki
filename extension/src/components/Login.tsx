import { useState } from 'react'
import { supabase } from '../lib/supabase'

export function Login({ onLogin }: { onLogin: () => void }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        })

        if (error) {
            setError(error.message)
        } else {
            onLogin()
        }
        setLoading(false)
    }

    return (
        <div className="flex flex-col items-center justify-center h-full p-4 space-y-4">
            <h1 className="text-2xl font-bold text-primary">FlashNote AI</h1>
            <form onSubmit={handleLogin} className="w-full space-y-3">
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full p-2 border rounded"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full p-2 border rounded"
                />
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full p-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
        </div>
    )
}
