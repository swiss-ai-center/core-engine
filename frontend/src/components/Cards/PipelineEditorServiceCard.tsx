import { Button } from '@mui/material';
import ServiceCardBase from 'components/Cards/ServiceCardBase';
import { Tag } from 'models/Tag';
import React from 'react';

const PipelineEditorServiceCard: React.FC<{
    index: number, item: any, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, functions: any
}> = ({item, tags, handleTags, handleAIToggle, functions}) => {


    return (
        <ServiceCardBase item={item} tags={tags} handleTags={handleTags}
                         handleAIToggle={handleAIToggle}>
            <Button size={"small"} variant={"contained"} disableElevation={true}
                    onClick={() => {
                        functions.addService(item.id, item.tags, item.slug, item.data_in_fields, item.data_out_fields)
                    }}>Add</Button>
        </ServiceCardBase>
    );
}

export default PipelineEditorServiceCard;
