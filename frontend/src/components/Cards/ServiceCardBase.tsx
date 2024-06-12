import { Psychology } from '@mui/icons-material';
import { Tooltip, Typography, Grid } from '@mui/material';
import { Tag } from 'models/Tag';
import React, { ReactNode } from 'react';
import CardBase from 'components/Cards/CardBase';

const ServiceCardBase: React.FC<{
    item: any, tags: Tag[], handleTags: any, handleAIToggle: any, children: ReactNode
}> = ({item, tags, handleTags, handleAIToggle, children}) => {


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
        <CardBase item={item} tags={tags} handleTags={handleTags} cardActions={children}
                  cardName={cardName()} summary={summary()}></CardBase>
    );
}

export default ServiceCardBase;
