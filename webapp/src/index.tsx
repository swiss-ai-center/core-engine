import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import 'animate.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
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
                    position="bottom-left"
                    theme={"colored"}
                    transition={fadeIn}
                    autoClose={3000}
                />
            </FileArrayProvider>
        </Provider>
    </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
