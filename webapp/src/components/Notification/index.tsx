import { Snackbar, Alert, SnackbarCloseReason } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import { useNotification } from "../../utils/useNotification";

export const Notification = (): JSX.Element => {
    const notification = useSelector((state: any) => state.notification);
    const { clearNotification } = useNotification();

    const handleClose = (_: unknown, reason?: SnackbarCloseReason) =>
        reason !== "clickaway" && clearNotification();

    return (
        <Snackbar
            open={notification.open}
            autoHideDuration={notification.timeout}
            onClose={handleClose}
        >
            <Alert
                variant="filled"
                onClose={handleClose}
                severity={notification.type}
            >
                {notification.message}
            </Alert>
        </Snackbar>
    );
};
