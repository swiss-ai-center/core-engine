import Grid from "@mui/material/Unstable_Grid2";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import {Psychology} from "@mui/icons-material";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";
import React from "react";
import {Tag} from "../../models/Tag";

const ServiceCard : React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, addService: any,
}> = ({index, item, tags, handleTags, ai, handleAIToggle, addService}) => {



    return (
        <Grid xs={12} sm={6} lg={4} xl={3} key={index}
              sx={{height: 'auto', minHeight: '250px'}}>
            <Card
                sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
            >
                <CardContent sx={{flexGrow: 1}}>
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
                    <Grid container spacing={1} sx={{p: 0, mb: 2}}>
                        {item.tags ? item.tags.map((tag: any, index: number) => {
                            return (
                                <Grid key={`service-tag-${index}`}>
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
                    <Typography>
                        {
                            item.summary.length > 80 ?
                                item.summary.substring(0, 75) + "..." :
                                item.summary
                        }
                    </Typography>
                </CardContent>
                <CardActions sx={{p: 2}}>
                    <Link
                        to={"/showcase/service/" + item.slug}>
                        <Button size={"small"} variant={"contained"}>View</Button>
                    </Link>
                    {addService && <Button onClick={() => addService(item.name, item.slug, item.data_in_fields, item.data_out_fields)}>Add</Button>}
                </CardActions>
            </Card>
        </Grid>
    );
}

export default ServiceCard;