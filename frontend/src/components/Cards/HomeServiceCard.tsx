import {Button} from "@mui/material";
import {Link} from "react-router-dom";
import React from "react";
import {Tag} from "../../models/Tag";
import ServiceCardBase from "./ServiceCardBase";

const HomeServiceCard: React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, functions: any
}> = ({index, item, tags, handleTags, ai, handleAIToggle, functions}) => {


    return (
        <ServiceCardBase index={index} item={item} tags={tags} handleTags={handleTags} ai={ai}
                         handleAIToggle={handleAIToggle}>
            <Link
                to={"/showcase/service/" + item.slug}>
                <Button size={"small"} variant={"contained"} disableElevation={true}>View</Button>
            </Link>

        </ServiceCardBase>
    );
}

export default HomeServiceCard;