import React from "react";
import {Position, useUpdateNodeInternals} from "reactflow";
import {
    Autocomplete,
    Box,
    Card,
    CardActions,
    CardContent, Icon, IconButton,
    TextField,
    Typography
} from '@mui/material';
import {AddCircle, Close as CloseIcon} from '@mui/icons-material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';
import {dataTypeOptions} from "../../enums/dataTypeEnum";
import {FieldDescription} from "../../models/ExecutionUnit";
import CustomHandle from "../Handles/CustomHandle";
import {positionHandle} from "../../utils/functions";
import {toast} from "react-toastify";

const EntryNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [inputNames, setInputNames] = React.useState<string[]>([])
    const updateNodeInternals = useUpdateNodeInternals();


    const onSelectInputName = (newName: string, index: number) => {
        if (inputNames[index] === newName) return;
        if (inputNames.includes(newName)) {
            toast("Input name must be unique", {type: "info"});
            return;
        }

        data.onSelectEntryInputName(index, newName, inputNames[index])
        setInputNames(inputNames.map((name, nameIndex) => {
            if (nameIndex !== index) return name;
            return newName;
        }))
        updateNodeInternals(id)
    }

    const onDeleteInput = (index: number) => {
        const updatedNames = [...inputNames]
        updatedNames.splice(index, 1)
        setInputNames(updatedNames)
        data.onDeleteEntryInput(index);
        updateNodeInternals(id)
    }

    const onAddInput = () => {
        const defaultName = "Input Name";
        let newName = defaultName;
        let counter = 1;
        while (inputNames.includes(newName)) {
            newName = `${defaultName} ${counter}`;
            counter++;
        }
        setInputNames([...inputNames, newName]);
        data.onAddEntryInput(newName);
        updateNodeInternals(id)
    }

    const dataInSelection = data.dataIn.map((inputField: { name: string; type: string[]; }, index: number) =>
        <Box sx={{display: "flex", width: "100%"}} key={inputField.name}>
            <Box sx={{display: "flex", alignItems: "center", width: "40%", mr: 1}} key={index}>
                <TextField label="Input Name" variant="standard" defaultValue={inputField.name}
                           onFocus={(event) => event.target.select()}
                           onBlur={(event) => onSelectInputName(event.target.value, index)}/>
            </Box>
            <Autocomplete
                fullWidth
                multiple
                value={inputField.type}
                sx={{mb: 2, width: "60%"}}
                options={dataTypeOptions}
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
            <Box sx={{display: "flex", alignItems: "center", justifyContent: "center"}}>
                <IconButton
                    sx={{width: "fit-content", height: "fit-content", transform: "scale(0.7)"}}
                    aria-label={"close"}
                    onClick={() => {
                        onDeleteInput(index)
                    }}
                >
                    <CloseIcon/>
                </IconButton>
            </Box>
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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "15em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2}}>
                        {data.label}
                    </Typography>
                    {dataInSelection}
                </CardContent>
                <CardActions sx={{justifyContent: "flex-end", m: 1}}>
                    <Typography variant={"body1"} sx={{mr: 1}}>Add input file</Typography>
                    <Icon sx={{display: 'flex', alignItems: 'center'}} color={"primary"}
                          onClick={onAddInput}><AddCircle/></Icon>
                </CardActions>
            </Card>
            {data.dataIn.map((input: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={input.name}
                        label={input.name}
                        type={"source"}
                        style={{top: positionHandle(data.dataIn.length, index + 1)}}
                        position={Position.Right}
                    />
                );
            })}
        </>
    );
};

export default EntryNodeEdit;