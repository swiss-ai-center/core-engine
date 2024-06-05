import React from "react";
import { Position, useUpdateNodeInternals } from "reactflow";
import {
    Autocomplete,
    Card,
    CardActions,
    CardContent,
    Fab, Grid,
    IconButton,
    TextField, Tooltip,
    Typography
} from '@mui/material';
import { Add, Close as CloseIcon } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import { dataTypeOptions } from "../../enums/dataTypeEnum";
import { FieldDescription } from "../../models/ExecutionUnit";
import CustomHandle from "../Handles/CustomHandle";
import { positionHandle } from "../../utils/functions";
import { toast } from "react-toastify";


const EntryNodeEdit: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [inputNames, setInputNames] = React.useState<string[]>([])
    const updateNodeInternals = useUpdateNodeInternals();

    const replaceHyphensWithUnderscores = (newName: string) => {
        return newName.replace(/-/g, "_");
    }

    const onSelectInputName = (newName: string, prevName: string, index: number) => {
        if (inputNames[index] === newName) return;
        if (inputNames.includes(newName)) {
            toast("Input name must be unique", {type: "warning"});
            // reset the input name to the previous value
            setInputNames(inputNames.map((name, nameIndex) => {
                if (nameIndex !== index) return name;
                return prevName;
            }))
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
        const defaultName = "input_name";
        let newName = defaultName;
        let counter = 1;
        while (inputNames.includes(newName)) {
            newName = `${defaultName}_${counter}`;
            counter++;
        }
        setInputNames([...inputNames, newName]);
        data.onAddEntryInput(newName);
        updateNodeInternals(id)
    }

    const dataInSelection = data.dataIn.map((inputField: { name: string; type: string[]; }, index: number) =>
        <Grid sx={{display: "flex", flexGrow: 1}} key={inputField.name} mb={index === data.dataIn.length - 1 ? 0 : 1}
              spacing={2} container>
            <Grid xs={5} key={`${inputField.name}-name`} item>
                <TextField label={"Input name"} variant={"outlined"} defaultValue={inputField.name} size={"small"}
                           onFocus={(event) => event.target.select()}
                           onBlur={(event) => {
                               const val = replaceHyphensWithUnderscores(event.target.value);
                               onSelectInputName(val, inputField.name, index);
                               // set value of text field to the new name
                               event.target.value = val;
                           }}
                />
            </Grid>
            <Grid xs={6} item>
                <Autocomplete
                    fullWidth
                    multiple
                    size={"small"}
                    value={inputField.type}
                    options={dataTypeOptions}
                    isOptionEqualToValue={(option, value) => value === "" || option === value}
                    renderOption={(props, option, _) => (
                        <li {...props}>
                            {option}
                        </li>
                    )}
                    onChange={(_, value: string[]) => {
                        if (value) data.onSelectEntryInput(index, value);
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label={"Data type"} placeholder=""/>
                    )}
                />
            </Grid>
            <Grid xs={1} key={index} sx={{display: "flex", alignItems: "center", justifyContent: "center"}} item>
                <IconButton
                    sx={{width: "fit-content", height: "fit-content", transform: "scale(0.7)"}}
                    aria-label={"close"}
                    onClick={() => {
                        onDeleteInput(index)
                    }}
                >
                    <CloseIcon/>
                </IconButton>
            </Grid>
        </Grid>
    );


    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    minWidth: data.minWidth,
                    borderColor: colorMode === "light" ? lightgrey : darkgrey,
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2}}>
                        {data.label}
                    </Typography>
                    {dataInSelection}
                </CardContent>
                <CardActions sx={{justifyContent: "flex-end", m: 0}}>
                    <Tooltip title={"Add input"}>
                        <Fab color={"info"} aria-label={"add"} size={"small"} onClick={onAddInput}
                             sx={{boxShadow: 0}}>
                            <Add/>
                        </Fab>
                    </Tooltip>
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
