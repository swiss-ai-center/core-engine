import { configureStore } from '@reduxjs/toolkit';
import runStateReducer from './reducers/runStateSlice';
import { NotificationReducer } from './reducers/notificationSlice';

export default configureStore({
    reducer: {
        runState: runStateReducer,
        notification: NotificationReducer
    },
})
