import { CloseRounded } from "@mui/icons-material";
import { Card, CardActions, CardContent, Fab, Tooltip, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import { FieldDescription } from "models/ExecutionUnit";
import React, { useCallback } from "react";
import { useSelector } from 'react-redux';
import { Position, useReactFlow } from "reactflow";
import { positionHandle } from "utils/functions";
import CustomHandle from "components/Handles/CustomHandle";
import DataField from 'components/Nodes/DataField';


const StepNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const {deleteElements} = useReactFlow();

    const onDelete = useCallback(() => {
        deleteElements({nodes: [{id}]});
    }, [id, deleteElements]);


    const listDataIn = () => {
        return data.dataIn.map((inputField: { name: string; type: string[]; }, index: number) =>
            <DataField inputField={inputField} data={data.dataIn} index={index} key={`${data.label}-${index}`}/>
        );
    }

    return (
        <>
            {data.dataIn.map((input: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={input.name === "Input Name" ? `${input.name}${index}` : input.name}
                        label={input.name}
                        type={"target"}
                        style={{top: positionHandle(data.dataIn.length, index + 1)}}
                        position={Position.Left}
                    />
                );
            })}
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: colorMode === "light" ? lightgrey : darkgrey,
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
            >
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "17em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2}}
                    >
                        {data.label}
                    </Typography>
                    {listDataIn()}
                </CardContent>
                <CardActions sx={{justifyContent: "flex-end", m: 0}}>
                    <Tooltip title={"Delete node"}>
                        <Fab color={"error"} aria-label={"delete"} size={"small"} onClick={onDelete}
                             sx={{boxShadow: 0}}>
                            <CloseRounded/>
                        </Fab>
                    </Tooltip>
                </CardActions>
            </Card>
            {data.dataOut.map((output: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={output.name}
                        label={output.name}
                        type={"source"}
                        style={{top: positionHandle(data.dataOut.length, index + 1)}}
                        position={Position.Right}
                    />
                );
            })}
        </>
    );
};

export default StepNodeEdit;
