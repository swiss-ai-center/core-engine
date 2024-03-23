import React, { useEffect, useState } from 'react';
import { alpha, Box, CircularProgress, Grid, IconButton, Modal, styled, Typography } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { DataGrid, gridClasses } from '@mui/x-data-grid';
import { getStats } from '../../utils/api';
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

const ODD_OPACITY = 0.2;

const StripedDataGrid = styled(DataGrid)(({theme}) => ({
    [`& .${gridClasses.row}.even`]: {
        backgroundColor: theme.palette.mode === 'light' ? theme.palette.grey[200] : theme.palette.grey[800],
        '&:hover, &.Mui-hovered': {
            backgroundColor: alpha(theme.palette.primary.main, ODD_OPACITY),
            '@media (hover: none)': {
                backgroundColor: 'transparent',
            },
        },
        '&.Mui-selected': {
            backgroundColor: alpha(
                theme.palette.primary.main,
                ODD_OPACITY + theme.palette.action.selectedOpacity,
            ),
            '&:hover, &.Mui-hovered': {
                backgroundColor: alpha(
                    theme.palette.primary.main,
                    ODD_OPACITY +
                    theme.palette.action.selectedOpacity +
                    theme.palette.action.hoverOpacity,
                ),
                // Reset on touch devices, it doesn't add specificity
                '@media (hover: none)': {
                    backgroundColor: alpha(
                        theme.palette.primary.main,
                        ODD_OPACITY + theme.palette.action.selectedOpacity,
                    ),
                },
            },
        },
    },
    [`& .${gridClasses.row}.odd`]: {
        backgroundColor: theme.palette.background.paper,
        '&:hover, &.Mui-hovered': {
            backgroundColor: alpha(theme.palette.primary.main, ODD_OPACITY),
            '@media (hover: none)': {
                backgroundColor: 'transparent',
            }
        },
        '&.Mui-selected': {
            backgroundColor: alpha(
                theme.palette.primary.main,
                ODD_OPACITY + theme.palette.action.selectedOpacity,
            ),
            '&:hover, &.Mui-hovered': {
                backgroundColor: alpha(
                    theme.palette.primary.main,
                    ODD_OPACITY +
                    theme.palette.action.selectedOpacity +
                    theme.palette.action.hoverOpacity,
                ),
                // Reset on touch devices, it doesn't add specificity
                '@media (hover: none)': {
                    backgroundColor: alpha(
                        theme.palette.primary.main,
                        ODD_OPACITY + theme.palette.action.selectedOpacity,
                    ),
                }
            }
        }
    }
}));

export const EngineStats: React.FC<{
    trigger: boolean, onClose: any
}> = ({trigger, onClose}) => {
    const columns = [
        {field: 'status', headerName: 'Status', width: 150},
        {field: 'count', headerName: 'Count', width: 120},
    ]
    const [isReady, setIsReady] = useState(false);
    const [stats, setStats] = useState<any>({});

    const loadStats = async () => {
        const stats = await getStats();
        if (stats.hasOwnProperty("total")) {
            setStats(stats);
        } else {
            toast(`Error loading engine stats: ${stats.error}`, {type: "error"});
        }
        setIsReady(true);
    }

    useEffect(() => {
        if (trigger) {
            setIsReady(false);
            loadStats();
        }
    }, [trigger])

    return (
        <Modal open={trigger} onClose={onClose}>
            <Box sx={style}>
                <Typography id={"modal-modal-title"} variant={"h4"} component={"h2"}>
                    Engine stats
                </Typography>
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
                <Box sx={{mt: 2}}>
                    {!isReady ?
                        <CircularProgress/>
                        :
                        <>
                            {stats.summary && stats.summary.length > 0 &&
                                <Box sx={{height: 250, width: '100%'}}>
                                    <Typography id={"modal-modal-title"} variant={"h5"} color={"primary"}
                                                component={"h2"} marginY={2}>
                                        Summary (Total tasks: {stats.total})
                                    </Typography>
                                    <StripedDataGrid
                                        sx={{textTransform: 'uppercase', borderColor: 'primary.main'}} hideFooter={true}
                                        rows={stats.summary.map((row: any, index: number) => {
                                            return {...row, id: index}
                                        })}
                                        columns={columns}
                                        getRowClassName={(params) =>
                                            params.indexRelativeToCurrentPage % 2 === 0 ? 'even' : 'odd'
                                        }
                                    />
                                </Box>
                            }
                            {stats.services && stats.services.length > 0 &&
                                <Box marginTop={8} marginBottom={4}>
                                    <Typography id={"modal-modal-title"} variant={"h5"} color={"primary"}
                                                component={"h2"} marginTop={2}>
                                        Services
                                    </Typography>
                                    <Grid container spacing={2} rowSpacing={6}>
                                        {stats.services.map((service: any, index: number) => {
                                            return (
                                                <Grid item xs={12} md={6} lg={4} key={index}>
                                                    <Box sx={{height: 250, width: 'auto'}}>
                                                        <Typography id={"modal-modal-title"} variant={"h6"}
                                                                    component={"h4"}>
                                                            {service.service_name} (Total tasks: {service.total})
                                                        </Typography>
                                                        <StripedDataGrid
                                                            sx={{
                                                                textTransform: 'uppercase',
                                                                borderColor: 'primary.main'
                                                            }} hideFooter={true}
                                                            rows={service.status.map((row: any, index: number) => {
                                                                return {...row, id: index};
                                                            })}
                                                            columns={columns}
                                                            getRowClassName={(params) =>
                                                                params.indexRelativeToCurrentPage % 2 === 0 ?
                                                                    'even' : 'odd'
                                                            }
                                                        />
                                                    </Box>
                                                </Grid>
                                            )
                                        })}
                                    </Grid>
                                </Box>
                            }
                            {stats.pipelines && stats.pipelines.length > 0 &&
                                <Box marginTop={8} marginBottom={4}>
                                    <Typography id={"modal-modal-title"} variant={"h5"} color={"primary"}
                                                component={"h2"} marginTop={2}>
                                        Pipelines
                                    </Typography>
                                    <Grid container spacing={2} rowSpacing={6}>
                                        {stats.pipelines.map((pipeline: any, index: number) => {
                                            return (
                                                <Grid item xs={12} md={6} lg={4} key={index}>
                                                    <Box sx={{height: 250, width: 'auto'}}>
                                                        <Typography id={"modal-modal-title"} variant={"h6"}
                                                                    component={"h4"}>
                                                            {pipeline.pipeline_name}
                                                        </Typography>
                                                        <StripedDataGrid
                                                            sx={{
                                                                textTransform: 'uppercase',
                                                                borderColor: 'primary.main'
                                                            }} hideFooter={true}
                                                            rows={pipeline.status.map((row: any, index: number) => {
                                                                return {...row, id: index};
                                                            })}
                                                            columns={columns}
                                                            getRowClassName={(params) =>
                                                                params.indexRelativeToCurrentPage % 2 === 0 ?
                                                                    'even' : 'odd'
                                                            }
                                                        />
                                                    </Box>
                                                </Grid>
                                            )
                                        })}
                                    </Grid>
                                </Box>
                            }
                        </>
                    }
                </Box>
            </Box>
        </Modal>
    )
}
