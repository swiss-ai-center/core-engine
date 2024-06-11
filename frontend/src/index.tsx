import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import 'animate.css';
import { Provider } from 'react-redux';
import { cssTransition, ToastContainer } from 'react-toastify';
import App from './App';
import { FileArrayProvider } from './utils/providers/fileArray';
import store from './utils/store';
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
