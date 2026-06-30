import ReactJson from '@microlink/react-json-view';
import { Close as CloseIcon, ContentCopy } from '@mui/icons-material';
import { Box, Button, IconButton, Modal, Typography } from '@mui/material';
import React from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    bgcolor: 'background.paper',
    border: '2px solid',
    borderColor: 'primary.main',
    boxShadow: 24,
    borderRadius: '5px',
    p: 4,
    width: '80%',
    height: '80%',
    overflow: 'auto' as 'auto',
};

export const JsonModal: React.FC<{
    trigger: boolean, onClose: any, json: string
}> = ({trigger, onClose, json}) => {

    const colorMode = useSelector((state: any) => state.colorMode.value);

    const copyJson = async () => {
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(json);
            } else {
                const textArea = document.createElement("textarea");
                textArea.value = json;
                textArea.style.position = "fixed";
                textArea.style.left = "-9999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand("copy");
                document.body.removeChild(textArea);
            }
            toast("Pipeline JSON copied to clipboard", {type: "info"});
        } catch (error: any) {
            toast(`Could not copy JSON: ${error.message}`, {type: "error"});
        }
    };

    return (
        <Modal open={trigger} onClose={onClose}>
            <Box sx={style}>
                <Typography id={"modal-modal-title"} variant={"h4"} component={"h2"}>
                    Pipeline JSON
                </Typography>
                <Button
                    sx={{mt: 2}}
                    variant={"outlined"}
                    startIcon={<ContentCopy/>}
                    onClick={copyJson}
                >
                    Copy JSON
                </Button>
                <IconButton
                    aria-label={"close"}
                    onClick={onClose}
                    sx={{
                        position: 'absolute',
                        right: 8,
                        top: 8,
                        color: (theme) => theme.palette.grey[500],
                    }}
                >
                    <CloseIcon/>
                </IconButton>
                <Box sx={{mt: 3}}>
                    <Box sx={{
                        border: 1,
                        borderColor: colorMode === 'light' ? "#bdbdbd" : "#5a5a5a",
                        borderRadius: 1,
                        backgroundColor: colorMode === 'light' ? "#fff" : "#000",
                    }}>
                        <ReactJson src={JSON.parse(json)}
                                   style={{padding: '1em', borderRadius: '4px'}}
                                   theme={colorMode === 'light' ? 'rjv-default' : 'summerfruit'}
                                   enableClipboard={true}
                                   iconStyle={'triangle'}
                                   sortKeys={false}
                                   collapsed={4}
                                   displayDataTypes={false}
                                   displayObjectSize={false}
                                   name={false}
                        />
                    </Box>
                </Box>
            </Box>
        </Modal>
    )
}
