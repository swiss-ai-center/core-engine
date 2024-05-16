import {Button} from "@mui/material";
import React from "react";
import {Tag} from "../../models/Tag";
import ServiceCardBase from "./ServiceCardBase";

const CreatePipelineServiceCard: React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, functions: any
}> = ({index, item, tags, handleTags, ai, handleAIToggle, functions}) => {


    return (
        <ServiceCardBase index={index} item={item} tags={tags} handleTags={handleTags} ai={ai}
                         handleAIToggle={handleAIToggle}>
            <Button size={"small"} variant={"contained"} disableElevation={true}
                    onClick={() => {
                        functions.addService(item.name, item.tags, item.slug, item.data_in_fields, item.data_out_fields)
                    }}>Add</Button>
        </ServiceCardBase>
    );
}

export default CreatePipelineServiceCard;