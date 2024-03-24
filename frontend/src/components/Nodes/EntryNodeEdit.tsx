import React, {useState} from "react";
import { Handle, Position } from "reactflow";
import {
    Autocomplete, AutocompleteChangeDetails, AutocompleteChangeReason, Box, Button,
    Card,
    CardActions,
    CardContent, Icon,
    TextField,
    Typography
} from '@mui/material';
import { AddCircle } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import {DataType, DataTypeOptions} from "../../enums/dataTypeEnum";
import {NodeProps} from "reactflow";

const  EntryNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [inputNames, setInputNames]  = React.useState<string[]>([])


    const onSelectInputName = (newName: string, index: number ) => {
        data.onSelectEntryInputName(index, newName, inputNames[index])
        setInputNames(inputNames.map((name, nameIndex) => {
            if (nameIndex !== index ) return name;
            return newName;
        }))
    }

    const onAddInput = () => {
        setInputNames([...inputNames,""])
        data.onAddPipelineInput()
    }

    const dataInSelection = data.dataIn.map((inputField: { name: string ; type: string[];}, index: number) =>
        <Box sx={{display: "flex", width: "100%"}}>
            <Box sx={{display: "flex", alignItems: "center", width: "40%", mr: 1}} key={index}>
                <TextField id="standard-basic" label="Input Name" variant="standard"
                onBlur={(event) => onSelectInputName(event.target.value, index)}/>
            </Box>
            <Autocomplete
                fullWidth
                multiple
                value={inputField.type}
                sx={{mb: 2, width: "60%"}}
                options={DataTypeOptions}
                isOptionEqualToValue={(option, value) => value === "" || option === value}
                renderOption={(props, option, {selected}) => (
                    <li {...props}>
                        {option}
                    </li>
                )}
                onChange={(event, value: string[]) => {
                    if (value) data.onSelectEntryInput(index, value);
                }}
                renderInput={(params) => (
                    <TextField {...params} label={"Data type"} placeholder=""/>
                )}
            />
        </Box>
    );



    return (
        <>
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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "20em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}>
                        {data.label}
                    </Typography>
                    {dataInSelection}
                </CardContent>
                <CardActions sx={{ justifyContent: "flex-end", m: 1 }}>
                    <Typography variant={"body1"} sx={{ mr: 1 }}>Add input file</Typography>
                    <Icon sx={{ display: 'flex', alignItems: 'center' }} color={"primary"} onClick={onAddInput}><AddCircle/></Icon>
                </CardActions>
            </Card>
            <Handle
                type={"source"}
                position={Position.Right}
            />
        </>
    );
};

export default EntryNodeEdit;