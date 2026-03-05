import {Add, Close as CloseIcon} from '@mui/icons-material';
import {Card, CardActions, CardContent, Fab, Grid, IconButton, TextField, Tooltip, Typography} from '@mui/material';
import {grey} from '@mui/material/colors';
import {FieldDescription} from "models/ExecutionUnit";
import React from "react";
import {useSelector} from 'react-redux';
import {toast} from "react-toastify";
import {Position, useUpdateNodeInternals} from "reactflow";
import {positionHandle} from "utils/functions";
import CustomHandle from "components/Handles/CustomHandle";
import DataField from "components/Nodes/DataField";

const ExitNodeEdit: React.FC<{ id: string; data: any }> = ({id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const updateNodeInternals = useUpdateNodeInternals();

    // Same idea as EntryNodeEdit
    const [outputNames, setOutputNames] = React.useState<string[]>([]);

    const replaceHyphensWithUnderscores = (newName: string) => {
        return newName.replace(/-/g, "_");
    };

    const replaceSpacesWithUnderscores = (newName: string) => {
        return newName.replace(/ /g, "_");
    };

    // Initialize names once when the component mounts (EntryNodeEdit style)
    React.useEffect(() => {
        if (outputNames.length === 0) {
            const names = (data.dataOut ?? []).map((f: any) => f.name);
            setOutputNames(names);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const onSelectOutputName = (newName: string, prevName: string, index: number) => {
        if (newName.trim().length === 0) {
            toast("Output name cannot be empty", {type: "warning"});
            setOutputNames(outputNames.map((name, nameIndex) => {
                if (nameIndex !== index) return name;
                return prevName;
            }));
            return;
        }

        if (outputNames[index] === newName) return;

        if (outputNames.includes(newName)) {
            toast("Output name must be unique", {type: "warning"});
            // reset the output name to the previous value (same as EntryNodeEdit)
            setOutputNames(outputNames.map((name, nameIndex) => {
                if (nameIndex !== index) return name;
                return prevName;
            }));
            return;
        }

        // IMPORTANT: same pattern: send prev name as what is currently stored
        data.onSelectExitOutputName(index, newName, outputNames[index]);

        setOutputNames(outputNames.map((name, nameIndex) => {
            if (nameIndex !== index) return name;
            return newName;
        }));

        updateNodeInternals(id);
    };

    const onDeleteOutput = (index: number) => {
        const updatedNames = [...outputNames];
        updatedNames.splice(index, 1);
        setOutputNames(updatedNames);

        data.onDeleteExitOutput(index);
        updateNodeInternals(id);
    };

    const onAddOutput = () => {
        const defaultName = "output_name";
        let newName = defaultName;
        let counter = 1;

        while (outputNames.includes(newName)) {
            newName = `${defaultName}_${counter}`;
            counter++;
        }

        setOutputNames([...outputNames, newName]);
        data.onAddExitOutput(newName);
        updateNodeInternals(id);
    };

    const dataOutSelection = (data.dataOut ?? []).map(
        (outputField: { name: string; type: string[] }, index: number) => (
            <Grid
                sx={{display: "flex", flexGrow: 1}}
                key={outputField.name}
                mb={index === (data.dataOut?.length ?? 0) - 1 ? 0 : 1}
                spacing={2}
                container
            >
                <Grid xs={5} key={`${outputField.name}-name`} item>
                    <TextField
                        label={"Output name"}
                        variant={"outlined"}
                        defaultValue={outputField.name}
                        size={"small"}
                        onFocus={(event) => event.target.select()}
                        onBlur={(event) => {
                            const previousName = outputNames[index] ?? outputField.name;
                            let val = event.target.value.trim();
                            val = replaceHyphensWithUnderscores(val);
                            val = replaceSpacesWithUnderscores(val);

                            if (val.length === 0) {
                                toast("Output name cannot be empty", {type: "warning"});
                                event.target.value = previousName;
                                return;
                            }

                            onSelectOutputName(val, previousName, index);

                            // set value of text field to the (sanitized) new name
                            event.target.value = val;
                        }}
                    />
                </Grid>

                <Grid xs={6} item>
                    {/* show output types like before */}
                    <DataField inputField={outputField} index={index} data={data.dataOut}/>
                </Grid>

                <Grid
                    xs={1}
                    key={index}
                    sx={{display: "flex", alignItems: "center", justifyContent: "center"}}
                    item
                >
                    <IconButton
                        sx={{width: "fit-content", height: "fit-content", transform: "scale(0.7)"}}
                        aria-label={"close"}
                        onClick={() => onDeleteOutput(index)}
                    >
                        <CloseIcon/>
                    </IconButton>
                </Grid>
            </Grid>
        )
    );

    return (
        <>
            <Card
                sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    borderColor: colorMode === "light" ? lightgrey : darkgrey,
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
                key={id}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography
                        variant={"subtitle1"}
                        color={"primary"}
                        sx={{justifyContent: "center", display: "flex", mb: 2}}
                    >
                        {data.label}
                    </Typography>

                    {dataOutSelection}
                </CardContent>

                <CardActions sx={{justifyContent: "flex-end", m: 0}}>
                    <Tooltip title={"Add output"}>
                        <Fab
                            color={"info"}
                            aria-label={"add"}
                            size={"small"}
                            onClick={onAddOutput}
                            sx={{boxShadow: 0}}
                        >
                            <Add/>
                        </Fab>
                    </Tooltip>
                </CardActions>
            </Card>

            {/* One target handle per output (this is the multi-output part) */}
            {(data.dataOut ?? []).map((output: FieldDescription, index: number) => (
                <CustomHandle
                    key={index}
                    id={output.name}
                    label={output.name}
                    type={"target"}
                    style={{top: positionHandle((data.dataOut ?? []).length, index + 1)}}
                    position={Position.Left}
                />
            ))}
        </>
    );
};

export default ExitNodeEdit;
