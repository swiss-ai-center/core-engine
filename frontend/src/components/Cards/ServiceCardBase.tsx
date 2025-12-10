import { Psychology } from '@mui/icons-material';
import { Grid, Tooltip, Typography } from '@mui/material';
import { Tag } from 'models/Tag';
import React, { ReactNode } from 'react';
import CardBase from 'components/Cards/CardBase';

const ServiceCardBase: React.FC<{
  data: any, tags: Tag[], handleTags: any, handleAIToggle: any, children: ReactNode
}> = ({data, tags, handleTags, handleAIToggle, children}) => {


  const cardName = () =>
    <Grid container>
      {data.has_ai ? (
        <>
          <Grid size={{xs: 11, sm: 10}} padding={0}>
            <Typography variant={"h5"} component={"h2"} gutterBottom>
              {data.name}
            </Typography>
          </Grid><Grid size={{xs: 1, sm: 2}}
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
          {data.name}
        </Typography>
      )}
    </Grid>

  const summary = () =>
    <Typography>
      {
        data.summary.length > 100 ?
          data.summary.substring(0, 75) + "..." :
          data.summary
      }
    </Typography>

  return (
    <CardBase item={data} tags={tags} handleTags={handleTags} cardActions={children}
              cardName={cardName()} summary={summary()}></CardBase>
  );
}

export default ServiceCardBase;
