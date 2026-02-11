import React, {useState, useRef, useEffect} from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

function formatTimestamp(date = new Date()) {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

function Markdown({ children }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeSanitize]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          )
        }
      }}
    >
      {children}
    </ReactMarkdown>
  )
}

export default function App(){
  const [messages, setMessages] = useState([
    {
      from: 'server',
      text: 'Welcome. Please give a road stretch on the 401 between two roads (i.e. eastbound lane between Markham Road and McCowan Road) and I can tell you what will be the impact after blocking a lane temporarily',
      timestamp: formatTimestamp()
    }
  ])
  const apiUrl = 'https://fastapi-test-626046981738.us-central1.run.app/'
  const [input, setInput] = useState('')
  const sending = useRef(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesRef = useRef(null)

  useEffect(()=>{
    // auto-scroll to bottom when messages change
    const el = messagesRef.current
    if(el) el.scrollTop = el.scrollHeight
  }, [messages, isLoading])

  async function sendMessage(){
    if(!input.trim() || sending.current) return
    const userMsg = input.trim()
    setMessages(m => [...m, {from: 'user', text: userMsg, timestamp: formatTimestamp()}])
    setInput('')
    sending.current = true
    setIsLoading(true)
    try{
      const jobRes = await fetch(apiUrl+'run-simulation', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({desc: userMsg})
      })

      const jobData = await jobRes.json()
      const jobId = jobData.execution_id

      console.log("jobId:", jobId)

      // Wait 7 minutes before starting to poll for results
      const initialDelayMs = 7 * 60 * 1000
      const sleep = (ms) => new Promise(res => setTimeout(res, ms))
      await sleep(initialDelayMs)

      // Exponential backoff: try up to 3 attempts
      const maxAttempts = 3
      const baseDelay = 5000 // 5s base for backoff between attempts
      let resultData = null
      for(let attempt = 1; attempt <= maxAttempts; attempt++){
        try{
          const res = await fetch(apiUrl+'get-result/'+jobId)
          if(res.ok){
            const data = await res.json()
            resultData = data
            break
          } else {
            // treat non-OK as not-ready and throw to trigger retry
            const text = await res.text().catch(()=>"")
            throw new Error(`Status ${res.status}: ${text}`)
          }
        }catch(err){
          console.warn(`Attempt ${attempt} failed:`, err)
          if(attempt < maxAttempts){
            const wait = baseDelay * Math.pow(2, attempt-1)
            await sleep(wait)
          }
        }
      }

      if(resultData){
        setMessages(m => [...m, {from: 'server', text: resultData.analysis, timestamp: formatTimestamp()}])
      } else {
        setMessages(m => [...m, {from: 'server', text: 'Simulation result not available after retries.', timestamp: formatTimestamp()}])
      }
    }catch(e){
      setMessages(m => [...m, {from: 'server', text: 'Error contacting server.', timestamp: formatTimestamp()}])
    }finally{
      sending.current = false
      setIsLoading(false)
    }
  }

  function onKey(e){
    if(e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-root">
      <header className="chat-header">
        <h2>Traffic Simulation Chat</h2>
      </header>

      <div className="messages" ref={messagesRef}>
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.from}`}>
            <div className="bubble">
              <Markdown>{m.text}</Markdown>
              <div className="timestamp">{m.timestamp}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="msg server typing">
            <div className="bubble">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}
      </div>

      <div className="composer">
        <textarea value={input} onChange={e=>setInput(e.target.value)} onKeyDown={onKey} placeholder="Send a message" disabled={isLoading} />
        <div className="composer-actions">
          <button className="send" onClick={sendMessage} disabled={isLoading}>{isLoading ? 'Sending...' : 'Send'}</button>
        </div>
      </div>
    </div>
  )
}
