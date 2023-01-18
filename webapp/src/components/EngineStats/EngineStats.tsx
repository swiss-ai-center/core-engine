import React, { useEffect, useState } from 'react';
import { Box, Modal, Typography } from '@mui/material';
import { getStats } from '../../utils/api';
import { useNotification } from '../../utils/useNotification';

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 300,
    bgcolor: 'background.paper',
    border: '2px solid',
    borderColor: 'primary.main',
    boxShadow: 24,
    borderRadius: '5px',
    p: 4,
};

export const EngineStats: React.FC<{
    trigger: boolean, onClose: any
}> = ({trigger, onClose}) => {

    const [engineStatus, setEngineStatus] = useState<any>({})
    const { displayNotification } = useNotification();

    const loadStats = async () => {
        getStats()
            .then((resp) => {
                setEngineStatus(resp);
            })
            .catch((err) => {
                displayNotification({message: `Error loading engine stats: ${err}`, type: "error"});
            })
    }

    useEffect(() => {
        loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [trigger])

    return (
        <Modal open={trigger} onClose={onClose}>
            <Box sx={style}>
                <Typography id="modal-modal-title" variant="h6" component="h2">
                    Engine stats
                </Typography>
                <Box id="modal-modal-description" sx={{ mt: 2 }}>
                    <dl>
                        <dt>Statistics of the engine</dt>
                        { Object.keys(engineStatus).length > 0
                            ? Object.keys(engineStatus["tasks"]).map((k) => {
                                return (<dd key={k}>{k.charAt(0).toUpperCase()}{k.slice(1)} : {engineStatus.tasks[k]}</dd>)
                            })
                            : "No statistics on tasks found"}

                        <dt>Statistics per services</dt>
                        {Object.keys(engineStatus).length > 0
                            ? Object.keys(engineStatus.services).map((k) => {
                                return (<dd key={k}>{k.charAt(0).toUpperCase()}{k.slice(1)} : {engineStatus.services[k]}</dd>)
                            })
                            : "No statistics on services found"}

                        <dt>Statistics per pipelines</dt>
                        {Object.keys(engineStatus).length > 0
                            ? Object.keys(engineStatus.pipelines).map((k) => {
                                return (<dd key={k}>{k.charAt(0).toUpperCase()}{k.slice(1)} : {engineStatus.pipelines[k]}</dd>)
                            })
                            : "No statistics on pipelines found"}
                    </dl>
                </Box>
            </Box>
        </Modal>
    )
}
