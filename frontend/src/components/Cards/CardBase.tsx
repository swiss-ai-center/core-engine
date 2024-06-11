import { Card, CardActions, CardContent, Chip, Tooltip } from '@mui/material';
import Grid from '@mui/material/Grid';
import { Tags } from 'enums/tagEnums';
import { Tag } from 'models/Tag';
import React, { ReactNode } from 'react';

const CardBase: React.FC<{
    item: any,
    tags: Tag[],
    handleTags: any,
    cardActions: ReactNode,
    cardName: ReactNode,
    summary: ReactNode
}> = ({item, tags, handleTags, cardActions, cardName, summary}) => {


    return (
        <Card
            sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
            variant={"outlined"}
        >
            <CardContent sx={{flexGrow: 1}}>
                {cardName}
                <Grid container spacing={1} sx={{mb: 2}}>
                    {item.tags ? item.tags.map((tag: any, index: number) => {
                        return (
                            <Grid key={`pipeline-tag-${index}`} item>
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
