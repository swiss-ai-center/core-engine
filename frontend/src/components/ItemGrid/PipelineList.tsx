import React from "react";
import {Tag} from "../../models/Tag";
import {Button, Card, CardActions, CardContent, Chip, Tooltip, Typography} from "@mui/material";
import LoadingGrid from "../LoadingGrid/LoadingGrid";
import Grid from "@mui/material/Unstable_Grid2";
import {isSmartphone} from "../../utils/functions";
import {Tags} from "../../enums/tagEnums";
import {Link} from "react-router-dom";

const PipelineList: React.FC<{
    pipelineCount: number, isReady: boolean, tags: Tag[], handleTags: any, pipelinePagination: any, pipelines: never[], searchParams: URLSearchParams
}> = ({pipelineCount, isReady, tags, handleTags, pipelinePagination, pipelines, searchParams}) => {

    return (
        <>
            <Typography gutterBottom variant={"h4"} component={"h2"}>
                Pipelines <Chip label={isReady ? pipelineCount : 0} variant={"outlined"} color={"secondary"}
                                size={"small"} style={{marginTop: "-2px"}}/>
            </Typography>

            {(isReady && pipelines.length > 0) || !isReady ? pipelinePagination() : <></>}
            {!isReady ?
                <LoadingGrid/>
                :
                <Grid container spacing={isSmartphone() ? 2 : 3}>
                    {pipelines.length === 0 ? (
                        <Grid xs={6} md={8}>
                            <Typography gutterBottom variant={"h6"} component={"h2"}>
                                No pipeline found
                            </Typography>
                        </Grid>
                    ) : (
                        pipelines.map((item: any, index: number) => {
                            return (
                                <Grid xs={12} sm={6} lg={4} xl={3} key={index}
                                      sx={{height: 'auto', minHeight: '250px'}}>
                                    <Card
                                        sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                    >
                                        <CardContent sx={{flexGrow: 1}}>
                                            <Typography gutterBottom variant={"h5"} component={"h2"}>
                                                {item.name}
                                            </Typography>
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
                                            <Typography>
                                                {item.summary}
                                            </Typography>
                                        </CardContent>
                                        <CardActions sx={{p: 2}}>
                                            <Link
                                                to={"/showcase/pipeline/" + item.slug}
                                                state={{back: searchParams.toString()}}
                                            >
                                                <Button size={"small"} variant={"contained"}>View</Button>
                                            </Link>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            );
                        }))}
                </Grid>
            }
            {(isReady && pipelines.length > 0) || !isReady ? pipelinePagination() : <></>}
        </>
    )
}

export default PipelineList;