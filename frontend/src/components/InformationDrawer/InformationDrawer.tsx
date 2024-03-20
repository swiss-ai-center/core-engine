import {
    Box,
    Drawer,
    Toolbar,
    Typography,
    Grid,
    Tooltip,
    Chip,
    AccordionSummary,
    AccordionDetails
} from '@mui/material';
import React from 'react';
import { Tags } from '../../enums/tagEnums';
import { Psychology, ExpandMore } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import MuiAccordion, { AccordionProps } from '@mui/material/Accordion';
import { useSelector } from 'react-redux';
import { isSmartphone } from '../../utils/functions';
import Markdown, { defaultUrlTransform } from 'react-markdown';
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import 'katex/dist/katex.min.css'
import './styles.css';
import { grey } from '@mui/material/colors';

const drawerWidth = isSmartphone() ? '100%' : 500;

const Accordion = styled((props: AccordionProps) => (
    <MuiAccordion disableGutters elevation={0} square {...props} children={props.children}/>
))(({theme, color}) => ({
    border: `1px solid ${color === 'light' ? "#bdbdbd" : "#5a5a5a"}`,
    '&:not(:last-child)': {
        borderBottom: 0,
        borderTopLeftRadius: theme.shape.borderRadius,
        borderTopRightRadius: theme.shape.borderRadius,
    },
    '&:last-child': {
        borderBottomLeftRadius: theme.shape.borderRadius,
        borderBottomRightRadius: theme.shape.borderRadius,
    },
    '&:before': {
        display: 'none',
    },
}));

export const InformationDrawer: React.FC<{
    mobileOpen: boolean,
    description: any,
}> = ({
          mobileOpen,
          description
      }) => {
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const lightgrey = colorMode === 'light' ? grey[100] : grey[900];
    const darkgrey = colorMode === 'light' ? grey[400] : grey[800];

    const drawer = (
        <>
            <Toolbar/>
            <Box m={isSmartphone() ? 2 : 3}
                 sx={{
                     overflow: 'auto',
                     p: isSmartphone() ? 2 : 3,
                     backgroundColor: lightgrey,
                     border: 2,
                     borderColor: darkgrey
                 }}
                 borderRadius={1}>
                <Box sx={{mb: isSmartphone() ? 2 : 3}}>
                    <Typography
                        component={"h1"}
                        variant={"h4"}
                        color={"text.primary"}
                        gutterBottom
                        sx={{mb: 2}}
                    >
                        {description ? description.name : ''}
                    </Typography>
                    <Grid container mb={3}>
                        <Grid item xs={description.has_ai ? 11 : 12} sm={description.has_ai ? 10 : 12}>
                            <Grid container>
                                {description.tags ? description.tags.map((tag: any, index: number) => {
                                    return (
                                        <Grid key={`service-tag-${index}`} pr={1} pb={1}>
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
                                                />
                                            </Tooltip>
                                        </Grid>
                                    )
                                }) : ''}
                            </Grid>
                        </Grid>
                        {description.has_ai ? (
                            <Grid item xs={1} sm={2} sx={{display: 'flex', justifyContent: 'flex-end'}}>
                                <Tooltip title={"AI Service"}>
                                    <Psychology sx={{color: "primary.main", fontSize: "1.5rem"}}/>
                                </Tooltip>
                            </Grid>
                        ) : <></>}
                    </Grid>
                    <Box sx={{
                        px: 2,
                        border: 1,
                        borderColor: colorMode === 'light' ? "#bdbdbd" : "#5a5a5a",
                        borderRadius: 1,
                        backgroundColor: colorMode === 'light' ? "#fff" : "#000"
                    }}>
                        <Markdown urlTransform={defaultUrlTransform}
                                  components={{
                                      a: ({node, ...props}) => {
                                          // eslint-disable-next-line jsx-a11y/anchor-has-content
                                          return <a target={"_blank"} {...props}/>
                                      }
                                  }}
                                  remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}
                                  skipHtml={true}
                                  className={"markdown-body"}
                        >
                            {
                                description ? description.description : ''
                            }
                        </Markdown>
                    </Box>
                </Box>
                <Box>
                    {description ?
                        <>
                            <Accordion variant={"outlined"} color={colorMode}>
                                <AccordionSummary expandIcon={<ExpandMore/>}>
                                    <Typography>Data in</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {description.data_in_fields ? description.data_in_fields.map((data: any, index: number) => {
                                            return (
                                                <Grid key={`data-in-${index}`} container>
                                                    <Grid item xs={4}>
                                                        <Typography variant={"subtitle1"} color={"primary"}>
                                                            {data.name}
                                                        </Typography>
                                                    </Grid>
                                                    <Grid item xs={8} justifyContent={"flex-end"} display={"flex"}>
                                                        <Typography variant={"subtitle1"}>
                                                            {data.type.map((type: string, index: number) => {
                                                                return (
                                                                    <span key={`data-in-type-${index}`}>
                                                                        {type}
                                                                        {index !== data.type.length - 1 ? ', ' : ''}
                                                                    </span>
                                                                )
                                                            })}
                                                        </Typography>
                                                    </Grid>
                                                </Grid>
                                            )
                                        }
                                    ) : ''}
                                </AccordionDetails>
                            </Accordion>
                            <Accordion variant={"outlined"} color={colorMode}>
                                <AccordionSummary expandIcon={<ExpandMore/>}>
                                    <Typography>Data out</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {description.data_out_fields ? description.data_out_fields.map((data: any, index: number) => {
                                            return (
                                                <Grid key={`data-out-${index}`} container>
                                                    <Grid item xs={4}>
                                                        <Typography variant={"subtitle1"} color={"primary"}>
                                                            {data.name}
                                                        </Typography>
                                                    </Grid>
                                                    <Grid item xs={8} justifyContent={"flex-end"} display={"flex"}>
                                                        <Typography variant={"subtitle1"}>
                                                            {data.type.map((type: string, index: number) => {
                                                                return (
                                                                    <span key={`data-out-type-${index}`}>
                                                                    {type}
                                                                        {index !== data.type.length - 1 ? ', ' : ''}
                                                                </span>
                                                                )
                                                            })}
                                                        </Typography>
                                                    </Grid>
                                                </Grid>
                                            )
                                        }
                                    ) : ''}
                                </AccordionDetails>
                            </Accordion>
                        </>
                        : <></>}
                </Box>
            </Box>
        </>
    );


    return (
        <Box
            component={"nav"}
            sx={{width: {md: drawerWidth}, flexShrink: {md: 0}}}
        >
            <Drawer
                variant={"temporary"}
                open={mobileOpen}
                ModalProps={{
                    keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                    display: {xs: 'block', md: 'none'},
                    '& .MuiDrawer-paper': {boxSizing: 'border-box', width: drawerWidth},
                }}
            >
                {drawer}
            </Drawer>
            <Drawer
                variant={"permanent"}
                sx={{
                    display: {xs: 'none', md: 'block'},
                    '& .MuiDrawer-paper': {boxSizing: 'border-box', width: drawerWidth},
                }}
                open
            >
                {drawer}
            </Drawer>
        </Box>
    );
}
