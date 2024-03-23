import React from "react";
import { NodeProps, Position } from "reactflow";
import {
    Button, Card, CardActions, CardContent, Tooltip, Typography
} from '@mui/material';
import { DownloadForOfflineTwoTone } from '@mui/icons-material';
import {
    RunState,
} from '../../utils/reducers/runStateSlice';
import { useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import { download, positionHandle } from '../../utils/functions';
import { ExitNodeData } from '../../models/NodeData';
import CustomHandle from './CustomHandle';


const ExitNode = ({data}: NodeProps<ExitNodeData>) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const generalStatus = useSelector((state: any) => state.runState.generalStatus);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);

    const downloadResult = async () => {
        await download(resultIdList);
    }

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: generalStatus === RunState.FINISHED ? "success.main" :
                        generalStatus === RunState.ERROR ? "error.main" :
                            (colorMode === "light" ? lightgrey : darkgrey),
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>
                </CardContent>
                <CardActions>
                    <Tooltip title={"Download final result"} placement={"left"}>
                        <span style={{display: "flex", width: "100%"}}>
                            <Button
                                disabled={!(generalStatus === RunState.FINISHED)}
                                sx={{
                                    display: "flex",
                                    width: "100%",
                                    minHeight: 32,
                                }}
                                disableElevation
                                variant={"contained"}
                                color={"success"}
                                size={"small"}
                                endIcon={<DownloadForOfflineTwoTone/>}
                                onClick={downloadResult}
                            >
                                Download
                            </Button>
                        </span>
                    </Tooltip>
                </CardActions>
            </Card>
            <div className="handles target">
                {data.targetHandles.map((handle, index) => {
                    return (
                        <CustomHandle
                            key={handle.id}
                            id={handle.id}
                            label={handle.label}
                            type={"target"}
                            style={{top: positionHandle(data.targetHandles.length, index + 1)}}
                            position={Position.Left}
                        />
                    );
                })}
            </div>
        </>
    );
};

export default ExitNode;
