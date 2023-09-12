import React from "react";
import { Handle, Position } from "react-flow-renderer";
import { Button, Card, CardActions, CardContent, Link as URLLink, Tooltip, Typography } from '@mui/material';
import { DownloadForOfflineTwoTone } from '@mui/icons-material';
import { RunState } from '../../utils/reducers/runStateSlice';
import { useSelector } from 'react-redux';
import { getResult } from '../../utils/api';
import { toast } from 'react-toastify';
import { grey } from '@mui/material/colors';


const ProgressNode = ({data}: any) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const successColor = (colorMode === "light" ? "#2f7c31" : "#66bb69");
    const errorColor = (colorMode === "light" ? "#d32f2f" : "#f44336");
    const run = useSelector((state: any) => state.runState.value);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);

    const isExecuting = () => {
        return (
            run === RunState.PENDING ||
            run === RunState.PROCESSING ||
            run === RunState.SAVING ||
            run === RunState.FETCHING ||
            run === RunState.SCHEDULED);
    }

    const downloadIntermediateResult = async () => {
        // TODO: implement
        /* for (const id of resultIdList) {
            const file: any = await getResult(id);
            if (file.file) {
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(file.file);
                link.setAttribute('download', 'result.' + id.split('.')[1]);
                document.body.appendChild(link);
                link.click();
            } else {
                toast(`Error downloading file ${id}: ${file.error}`, {type: "error"});
            }
        } */
    }

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    border: !isExecuting() ? ("2px solid " + (run === RunState.FINISHED ? successColor :
                        run === RunState.ERROR ? "#d32f2f" : (colorMode === "light" ? lightgrey : darkgrey))) : "none",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
                className={isExecuting() ? "rotating-border" : ""}
            >
                <CardContent sx={{flexGrow: 1}}>
                    {data.type === "pipeline" ? (
                    <URLLink href={`/showcase/service/${data.service_id}`} sx={{textDecoration: "none"}}>
                        <Tooltip title={"Service's page"} placement={"top"}>
                            <Typography variant={"subtitle1"} color={"primary"}
                                        sx={{justifyContent: "center", display: "flex"}}
                            >
                                {data.label}
                            </Typography>
                        </Tooltip>
                    </URLLink>
                    ) : (
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>
                    )}
                </CardContent>
                <CardActions
                    // if type is service, hide download button
                    sx={{display: data.type === "service" ? "none" : "flex"}}
                >
                    <Tooltip title={"Download intermediate result"} placement={"bottom"}>
                        <span>
                            <Button
                                disabled={!(run === RunState.FINISHED)}
                                sx={{
                                    display: "flex",
                                    width: "100%",
                                    minHeight: 32,
                                }}
                                variant={"outlined"}
                                color={"success"}
                                size={"small"}
                                endIcon={<DownloadForOfflineTwoTone/>}
                                onClick={downloadIntermediateResult}
                            >
                                Download
                            </Button>
                        </span>
                    </Tooltip>
                </CardActions>
            </Card>
            <Handle
                type={"target"}
                position={Position.Left}
            />
            <Handle
                type={"source"}
                position={Position.Right}
            />
        </>
    );
};

export default ProgressNode;
