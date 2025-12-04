
const testUrlNormalization = (url: string) => {
    const normalized = (url || 'http://localhost:8000/api/v1').replace(/\/$/, '')
    console.log(`Original: '${url}' -> Normalized: '${normalized}'`)
    return normalized
}

console.log('Testing URL normalization:')
testUrlNormalization('http://localhost:8000/api/v1/')
testUrlNormalization('http://localhost:8000/api/v1')
testUrlNormalization('https://api.example.com/')
