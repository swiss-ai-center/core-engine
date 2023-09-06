import React from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Button, Card, CardActions, CardContent, Typography
} from '@mui/material';
import { DownloadForOfflineTwoTone } from '@mui/icons-material';
import {
    RunState,
    setResultIdList,
} from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { getResult } from '../../utils/api';
import { toast } from 'react-toastify';
import { grey } from '@mui/material/colors';


const ProgressNode = ({data}: any) => {
    const lightgrey = grey[400];
    const dispatch = useDispatch();
    const run = useSelector((state: any) => state.runState.value);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);

    const isExecuting = () => {
        return (
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

    React.useEffect(() => {
        dispatch(setResultIdList([]));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [data]);

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    border: !isExecuting() ? ("2px solid " + (run === RunState.FINISHED ? "#2f7c31" :
                        run === RunState.ERROR ? "#d32f2f" : lightgrey)) : "none",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
                className={isExecuting() ? "rotating-border" : ""}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>
                </CardContent>
                <CardActions>
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
