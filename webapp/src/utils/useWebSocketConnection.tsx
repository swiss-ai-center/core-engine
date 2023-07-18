import useWebSocket from 'react-use-websocket';

export const useWebSocketConnection = () => {
    const {lastJsonMessage, sendJsonMessage} = useWebSocket(
        `${process.env.REACT_APP_ENGINE_WS_URL}/ws`,
        {
            share: true,
        }
    );

    return {lastJsonMessage, sendJsonMessage} as const;
};
