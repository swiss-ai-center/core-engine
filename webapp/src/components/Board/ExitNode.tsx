import React from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Button, Card, CardActions, CardContent, Tooltip, Typography
} from '@mui/material';
import { DownloadForOfflineTwoTone } from '@mui/icons-material';
import {
    RunState,
} from '../../utils/reducers/runStateSlice';
import { useSelector } from 'react-redux';
import { getResult } from '../../utils/api';
import { toast } from 'react-toastify';
import { grey } from '@mui/material/colors';


const ExitNode = ({data}: any) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const run = useSelector((state: any) => state.runState.value);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);

    const downloadResult = async () => {
        for (const id of resultIdList) {
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
        }
    }

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: run === RunState.FINISHED ? "success.main" :
                        run === RunState.ERROR ? "error.main" : (colorMode === "light" ? lightgrey : darkgrey),
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
                                disabled={!(run === RunState.FINISHED)}
                                sx={{
                                    display: "flex",
                                    width: "100%",
                                    minHeight: 32,
                                }}
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
            <Handle
                type={"target"}
                position={Position.Left}
            />
        </>
    );
};

export default ExitNode;
