import React from "react";
import { Handle, Position} from "reactflow";
import { Box, Card, CardActions, CardContent, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';


const ExitNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);

    const listDataOut = () => {
        return data.dataOut.map((inputField: { name: string ; type: string[]; }, index: number) =>
            <Box sx={{display: "flex", width: "100%", alignItems: "center"}} key={inputField.name}>
                <Box sx={{display: "flex", flexDirection: "column", justifyContent: "center", width: "100%"}} key={index}>
                    <Typography variant={"body1"}>{inputField.name} </Typography>
                    <Box sx={{display:"flex"}}>
                        {inputField.type.map((type: string) => <Typography variant={"body2"} key={`${inputField.name}${type}`}>{type} &nbsp;</Typography>)}
                    </Box>
                </Box>
            </Box>
        );
    }

    return (
        <>
            <Handle
                type={"target"}
                position={Position.Left}
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
            >
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "10em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2 }}
                    >
                        {data.label}
                    </Typography>

                    {data.dataOut.length !== 0 ?
                        <Box sx={{width: "100%"}}>
                            <Box sx={{display: "flex", width: "100%", justifyContent: "center"}}>
                                <Typography variant={"body1"}> Pipeline Output </Typography>
                            </Box>
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
