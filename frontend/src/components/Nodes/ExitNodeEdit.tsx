import { Box, Card, CardActions, CardContent, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import React from "react";
import { useSelector } from 'react-redux';
import { Handle, Position } from "reactflow";
import DataField from './DataField';


const ExitNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);

    const listDataOut = () => {
        return data.dataOut.map((inputField: { name: string; type: string[]; }, index: number) =>
            <DataField key={`${data.label}-${index}`} inputField={inputField} index={index} data={data.dataOut}/>
        );
    }

    return (
        <>
            <Handle
                type={"target"}
                position={Position.Left}
                className={"custom-handle"}
                about={colorMode}
            />
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: colorMode === "light" ? lightgrey : darkgrey,
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
                key={id}
            >
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "10em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2}}
                    >
                        {data.label}
                    </Typography>

                    {data.dataOut.length !== 0 ?
                        <Box sx={{width: "100%", mb: -1}}>
                            {listDataOut()}
                        </Box>
                        : false}
                </CardContent>
                <CardActions></CardActions>
            </Card>
        </>
    );
};

export default ExitNodeEdit;
