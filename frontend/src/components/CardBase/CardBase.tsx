import Grid from "@mui/material/Unstable_Grid2";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import {Psychology} from "@mui/icons-material";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";
import React, {ReactNode} from "react";
import {Tag} from "../../models/Tag";

const CardBase : React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, cardActions: ReactNode, cardName: ReactNode, summary: ReactNode
}> = ({index, item, tags, handleTags, cardActions, cardName, summary}) => {


    return (
            <Card
                sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                variant={"outlined"}
            >
                <CardContent sx={{flexGrow: 1}}>
                    {cardName}
                    <Grid container spacing={1} sx={{p: 0, mb: 2}}>
                        {item.tags ? item.tags.map((tag: any, index: number) => {
                            return (
                                <Grid key={`pipeline-tag-${index}`}>
                                    <Tooltip title={tag.name}>
                                        <Chip
                                            className={"acronym-chip"}
                                            label={tag.acronym}
                                            style={
                                                Tags.filter((t) =>
                                                    t.acronym === tag.acronym)[0].colors
                                            }
                                            variant={"outlined"}
                                            size={"small"}
                                            onClick={() => {
                                                handleTags(null, [...tags, tag]);
                                            }}
                                        />
                                    </Tooltip>
                                </Grid>
                            )
                        }) : ''}
                    </Grid>
                    {summary}
                </CardContent>
                <CardActions sx={{p: 2}}>
                    {cardActions}
                </CardActions>
            </Card>
    );
}

export default CardBase;