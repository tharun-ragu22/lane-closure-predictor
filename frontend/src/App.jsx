import React, {useState, useRef, useEffect} from 'react'

export default function App(){
  const [messages, setMessages] = useState([
    {from: 'server', text: 'Welcome — this is a dummy chat. Try saying "hello".'}
  ])
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
    setMessages(m => [...m, {from: 'user', text: userMsg}])
    setInput('')
    sending.current = true
    setIsLoading(true)
    try{
      const res = await fetch('https://fastapi-test-626046981738.us-central1.run.app/get-result/sumo-simulation-job-spnrh', {
        method: 'GET',
        headers: {'Content-Type':'application/json'},
        // body: JSON.stringify({message: userMsg})
      })
      const data = await res.json()
      setMessages(m => [...m, {from: 'server', text: data.analysis}])
    }catch(e){
      setMessages(m => [...m, {from: 'server', text: 'Error contacting server.'}])
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
            <div className="bubble">{m.text}</div>
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
