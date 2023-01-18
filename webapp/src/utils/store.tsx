import { configureStore } from '@reduxjs/toolkit';
import runStateReducer from './reducers/runStateSlice';
import { NotificationReducer } from './reducers/notificationSlice';
import colorModeReducer from './reducers/colorModeSlice';

export default configureStore({
    reducer: {
        runState: runStateReducer,
        notification: NotificationReducer,
        colorMode: colorModeReducer
    },
})
