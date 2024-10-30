import { Button, Typography } from '@mui/material';
import CardBase from 'components/Cards/CardBase';
import { Tag } from 'models/Tag';
import React from 'react';
import { Link } from 'react-router-dom';

const PipelineCard: React.FC<{
    item: any, tags: Tag[], handleTags: any, searchParams: URLSearchParams
}> = ({item, tags, handleTags, searchParams}) => {

    const cardActions = () =>
        <>
            <Link
                to={"/showcase/pipeline/" + item.slug}
                state={{back: searchParams.toString()}}
            >
                <Button size={"small"} variant={"contained"} disableElevation={true}>
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
            {
                item.summary.length > 100 ?
                    item.summary.substring(0, 75) + "..." :
                    item.summary
            }
        </Typography>

    return (
        <CardBase item={item} tags={tags} handleTags={handleTags} cardActions={cardActions()}
                  cardName={cardName()} summary={summary()}></CardBase>
    );
}

export default PipelineCard;
