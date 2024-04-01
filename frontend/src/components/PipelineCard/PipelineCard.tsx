import Grid from "@mui/material/Unstable_Grid2";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import {Psychology} from "@mui/icons-material";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";
import React, {ReactNode} from "react";
import {Tag} from "../../models/Tag";
import CardBase from "../CardBase/CardBase";

const PipelineCard : React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, searchParams: URLSearchParams
}> = ({index, item, tags, handleTags, searchParams}) => {

    const cardActions = () =>
        <>
            <Link
                to={"/showcase/pipeline/" + item.slug}
                state={{back: searchParams.toString()}}
            >
                <Button size={"small"} variant={"contained"} disableElevation>
                    View
                </Button>
            </Link>
        </>

    const cardName = () =>
        <Typography gutterBottom variant={"h5"} component={"h2"}>
            {item.name}
        </Typography>

    const summary = () =>
        <Typography>
            {item.summary}
        </Typography>

    return (
            <CardBase index={index} item={item} tags={tags} handleTags={handleTags} cardActions={cardActions()}
                      cardName={cardName()} summary={summary()}></CardBase>
    );
}

export default PipelineCard;