import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url) {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED')
  const [lastMessage, setLastMessage] = useState(null)
  const [error, setError] = useState(null)
  
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = 3000

  const connect = useCallback(() => {
    try {
      if (socket) {
        socket.close()
      }

      setConnectionStatus('CONNECTING')
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionStatus('CONNECTED')
        setError(null)
        reconnectAttempts.current = 0
        setSocket(ws)
      }

      ws.onmessage = (event) => {
        try {
          setLastMessage(event.data)
        } catch (err) {
          console.error('Error processing WebSocket message:', err)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setSocket(null)
        
        if (event.code !== 1000) {
          setConnectionStatus('DISCONNECTED')
          
          if (reconnectAttempts.current < maxReconnectAttempts) {
            setConnectionStatus('RECONNECTING')
            reconnectAttempts.current += 1
            
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log(`Reconnection attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`)
              connect()
            }, reconnectDelay * reconnectAttempts.current)
          } else {
            setConnectionStatus('FAILED')
            setError('Maximum reconnection attempts exceeded')
          }
        } else {
          setConnectionStatus('DISCONNECTED')
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('WebSocket connection error')
        setConnectionStatus('ERROR')
      }

      return ws
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err)
      setError('Failed to create WebSocket connection')
      setConnectionStatus('ERROR')
      return null
    }
  }, [url, socket])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (socket) {
      socket.close(1000, 'Manual disconnect')
      setSocket(null)
    }
    
    setIsConnected(false)
    setConnectionStatus('DISCONNECTED')
    reconnectAttempts.current = 0
  }, [socket])

  const sendMessage = useCallback((message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        const messageStr = typeof message === 'string' ? message : JSON.stringify(message)
        socket.send(messageStr)
        return true
      } catch (err) {
        console.error('Error sending WebSocket message:', err)
        setError('Failed to send message')
        return false
      }
    } else {
      console.warn('WebSocket is not connected')
      return false
    }
  }, [socket])

  useEffect(() => {
    if (url) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [url])

  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socket) {
        socket.close()
      }
    }
  }, [])

  return {
    socket,
    isConnected,
    connectionStatus,
    lastMessage,
    error,
    sendMessage,
    connect,
    disconnect,
    reconnectAttempts: reconnectAttempts.current,
    maxReconnectAttempts
  }
}
