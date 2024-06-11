import { Button } from '@mui/material';
import ServiceCardBase from 'components/Cards/ServiceCardBase';
import { Tag } from 'models/Tag';
import React from 'react';
import { Link } from 'react-router-dom';

const HomeServiceCard: React.FC<{
    item: any, tags: Tag[], handleTags: any, handleAIToggle: any
}> = ({item, tags, handleTags, handleAIToggle}) => {


    return (
        <ServiceCardBase item={item} tags={tags} handleTags={handleTags}
                         handleAIToggle={handleAIToggle}>
            <Link
                to={"/showcase/service/" + item.slug}>
                <Button size={"small"} variant={"contained"} disableElevation={true}>View</Button>
            </Link>

        </ServiceCardBase>
    );
}

export default HomeServiceCard;
