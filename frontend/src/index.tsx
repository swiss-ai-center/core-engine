import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import 'animate.css';
import App from './App';
import { Provider } from 'react-redux';
import store from './utils/store';
import { FileArrayProvider } from './utils/providers/fileArray';
import { ToastContainer, cssTransition } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);

const fadeIn = cssTransition({
    enter: "animate__animated animate__backInLeft",
    exit: "animate__animated animate__backOutLeft"
});

root.render(
    <React.StrictMode>
        <Provider store={store}>
            <FileArrayProvider>
                <App/>
                <ToastContainer
                    position={"bottom-left"}
                    theme={"colored"}
                    transition={fadeIn}
                    autoClose={3000}
                />
            </FileArrayProvider>
        </Provider>
    </React.StrictMode>
);
