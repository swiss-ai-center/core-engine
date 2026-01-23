import { EnergySavingsLeafTwoTone, PsychologyTwoTone } from '@mui/icons-material';
import { Grid, Tooltip, Typography } from '@mui/material';
import { Tag } from 'models/Tag';
import React, { ReactNode } from 'react';
import CardBase from 'components/Cards/CardBase';
import { ServiceStatus } from '../../enums/serviceStatusEnum';

const ServiceCardBase: React.FC<{
    item: any, tags: Tag[], handleTags: any, handleAIToggle: any, children: ReactNode
}> = ({item, tags, handleTags, handleAIToggle, children}) => {


    const cardName = () => {
        const getEnergySavingsColor = () => {
            switch (item.status) {
                case ServiceStatus.SLEEPING:
                    return "success.main";
                case ServiceStatus.AVAILABLE:
                    return "primary.main";
                default:
                    return "text.disabled";
            }
        };

        const getEnergySavingsTooltip = () => {
            switch (item.status) {
                case ServiceStatus.SLEEPING:
                    return "Service is sleeping";
                case ServiceStatus.AVAILABLE:
                    return "Service is running";
                default:
                    return "Service is not available or disabled";
            }
        };

        return (
            <Grid container>
                <Grid xs={item.has_ai ? 9 : 10}
                      sm={item.has_ai ? 8 : 9} padding={0} item>
                    <Typography variant={"h5"} component={"h2"} gutterBottom>
                        {item.name}
                    </Typography>
                </Grid>
                <Grid xs={item.has_ai ? 3 : 2}
                      sm={item.has_ai ? 4 : 3}
                      sx={{display: 'flex', justifyContent: 'flex-end', gap: 0.5}}
                      padding={0} item>
                    {item.has_ai && (
                        <Tooltip title={"AI Service"}>
                            <PsychologyTwoTone sx={{color: "primary.main", fontSize: "1.5rem"}}
                                               onClick={() => {
                                                   handleAIToggle({
                                                       target: {
                                                           checked: true
                                                       }
                                                   });
                                               }}/>
                        </Tooltip>
                    )}
                    <Tooltip title={getEnergySavingsTooltip()}>
                        <EnergySavingsLeafTwoTone sx={{color: getEnergySavingsColor(), fontSize: "1.5rem"}}/>
                    </Tooltip>
                </Grid>
            </Grid>
        );
    }

    const summary = () =>
        <Typography>
            {
                item.summary.length > 100 ?
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
