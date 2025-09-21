import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectTimeoutId = useRef(null);
  const reconnectAttempts = useRef(0);
  
  const { 
    shouldReconnect = true, 
    maxReconnectAttempts = 5, 
    reconnectInterval = 3000,
    onMessage,
    onError,
    onOpen,
    onClose 
  } = options;

  const connect = useCallback(() => {
    try {
      if (ws.current?.readyState === WebSocket.OPEN) {
        return;
      }

      setConnectionStatus('Connecting');
      setError(null);

      ws.current = new WebSocket(url);

      ws.current.onopen = (event) => {
        setConnectionStatus('Connected');
        reconnectAttempts.current = 0;
        if (onOpen) onOpen(event);
      };

      ws.current.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data);
          setData(parsedData);
          if (onMessage) onMessage(parsedData, event);
        } catch (err) {
          console.warn('Failed to parse WebSocket message:', err);
          setData(event.data);
          if (onMessage) onMessage(event.data, event);
        }
      };

      ws.current.onclose = (event) => {
        setConnectionStatus('Disconnected');
        if (onClose) onClose(event);

        // Attempt to reconnect if enabled and not at max attempts
        if (shouldReconnect && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          setConnectionStatus(`Reconnecting (${reconnectAttempts.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutId.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.current.onerror = (event) => {
        setError('WebSocket connection error');
        setConnectionStatus('Error');
        if (onError) onError(event);
      };

    } catch (err) {
      setError(`Failed to connect: ${err.message}`);
      setConnectionStatus('Error');
    }
  }, [url, shouldReconnect, maxReconnectAttempts, reconnectInterval, onMessage, onError, onOpen, onClose]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutId.current) {
      clearTimeout(reconnectTimeoutId.current);
    }
    
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        const messageToSend = typeof message === 'string' ? message : JSON.stringify(message);
        ws.current.send(messageToSend);
        return true;
      } catch (err) {
        setError(`Failed to send message: ${err.message}`);
        return false;
      }
    } else {
      setError('WebSocket is not connected');
      return false;
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    data,
    connectionStatus,
    error,
    sendMessage,
    connect,
    disconnect,
    isConnected: connectionStatus === 'Connected'
  };
};

export default useWebSocket;