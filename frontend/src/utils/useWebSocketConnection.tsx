import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import useWebSocket from 'react-use-websocket';


export const useWebSocketConnection = () => {
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const {lastJsonMessage, sendJsonMessage} = useWebSocket(
        `${process.env.REACT_APP_ENGINE_WS_URL}/ws`,
        {
            share: true,
            onError: () => {
                toast.error('Connection to engine lost. Please refresh the page.', {
                    theme: colorMode === 'light' ? 'dark' : 'light'
                });
            }
        }
    );

    return {lastJsonMessage, sendJsonMessage} as const;
};
