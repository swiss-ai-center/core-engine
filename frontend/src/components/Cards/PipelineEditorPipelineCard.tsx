import { Button, Typography } from '@mui/material';
import CardBase from 'components/Cards/CardBase';
import { Tag } from 'models/Tag';
import React from 'react';

const PipelineEditorPipelineCard: React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, functions: any
}> = ({item, tags, handleTags, functions}) => {

    const cardName = () =>
        <Typography gutterBottom variant={"h5"} component={"h2"}>
            {item.name}
        </Typography>

    const summaryText = typeof item.summary === "string" ? item.summary : "";

    const summary = () =>
        <Typography>
            {summaryText.length > 75 ? summaryText.substring(0, 75) + "..." : summaryText}
        </Typography>

    return (
        <CardBase item={item} tags={tags} handleTags={handleTags} cardActions={
            <Button size={"small"} variant={"contained"} disableElevation={true}
                    onClick={() => functions.addPipeline(item.id, item.tags, item.slug, item.data_in_fields, item.data_out_fields)}>
                Add
            </Button>
        } cardName={cardName()} summary={summary()} />
    );
}

export default PipelineEditorPipelineCard;
