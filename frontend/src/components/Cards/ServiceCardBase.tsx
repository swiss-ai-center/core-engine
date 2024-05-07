import Grid from "@mui/material/Unstable_Grid2";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import {Psychology} from "@mui/icons-material";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";
import React, {ReactNode} from "react";
import {Tag} from "../../models/Tag";
import CardBase from "./CardBase";

const ServiceCardBase : React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, children: ReactNode
}> = ({index, item, tags, handleTags, ai, handleAIToggle, children}) => {


    const cardName = () =>
        <Grid container>
            {item.has_ai ? (
                <>
                    <Grid xs={11} sm={10} padding={0}>
                        <Typography variant={"h5"} component={"h2"} gutterBottom>
                            {item.name}
                        </Typography>
                    </Grid><Grid xs={1} sm={2}
                                 sx={{display: 'flex', justifyContent: 'flex-end'}}
                                 padding={0}>
                    <Tooltip title={"AI Service"}>
                        <Psychology sx={{color: "primary.main", fontSize: "1.5rem"}}
                                    onClick={() => {
                                        handleAIToggle({
                                            target: {
                                                checked: true
                                            }
                                        });
                                    }}/>
                    </Tooltip>
                </Grid>
                </>
            ) : (
                <Typography variant={"h5"} component={"h2"} gutterBottom>
                    {item.name}
                </Typography>
            )}
        </Grid>

    const summary = () =>
        <Typography>
            {
                item.summary.length > 80 ?
                    item.summary.substring(0, 75) + "..." :
                    item.summary
            }
        </Typography>

    return (
        <CardBase index={index} item={item} tags={tags} handleTags={handleTags} cardActions={children}
                  cardName={cardName()} summary={summary()}></CardBase>
    );
}

export default ServiceCardBase;