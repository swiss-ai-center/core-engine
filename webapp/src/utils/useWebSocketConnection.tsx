import useWebSocket from 'react-use-websocket';
import { toast } from 'react-toastify';
import { useSelector } from 'react-redux';


export const useWebSocketConnection = () => {
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const {lastJsonMessage, sendJsonMessage} = useWebSocket(
        `${process.env.REACT_APP_ENGINE_WS_URL}/ws`,
        {
            share: true,
            onClose: () => toast(
                'Connection to engine lost. Please refresh the page.',
                {type: 'warning', theme: colorMode === 'light' ? 'dark' : 'light', toastId: 'connectionLost'}
            ),
        }
    );

    return {lastJsonMessage, sendJsonMessage} as const;
};
