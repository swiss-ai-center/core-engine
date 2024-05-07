import Grid from "@mui/material/Unstable_Grid2";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import {Psychology} from "@mui/icons-material";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";
import React, {ReactNode} from "react";
import {Tag} from "../../models/Tag";
import ServiceCardBase from "./ServiceCardBase";

const CreatePipelineServiceCard : React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, functions: any
}> = ({index, item, tags, handleTags, ai, handleAIToggle, functions}) => {


    return (
        <ServiceCardBase index={index} item={item} tags={tags} handleTags={handleTags} ai={ai}
                         handleAIToggle={handleAIToggle}>
            <Button size={"small"} variant={"contained"} disableElevation={true}
                onClick={() => {
                    functions.addService(item.name, item.id, item.tags, item.slug, item.data_in_fields, item.data_out_fields)
                }}>Add</Button>
        </ServiceCardBase>
    );
}

export default CreatePipelineServiceCard;