import { ContentCopyTwoTone, EnergySavingsLeafTwoTone, ExpandMore, PsychologyTwoTone } from '@mui/icons-material';
import {
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    Chip,
    Drawer,
    Grid,
    Toolbar,
    Tooltip,
    Typography
} from '@mui/material';
import MuiAccordion, { AccordionProps } from '@mui/material/Accordion';
import { grey } from '@mui/material/colors';
import { styled } from '@mui/material/styles';
import { Tags } from 'enums/tagEnums';
import React from 'react';
import Markdown, { defaultUrlTransform } from 'react-markdown';
import { useSelector } from 'react-redux';
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import 'katex/dist/katex.min.css'
import './styles.css';
import { isSmartphone } from 'utils/functions';
import { getCodeSnippet } from 'utils/api';
import { toast } from 'react-toastify';
import { ServiceStatus } from '../../enums/serviceStatusEnum';

const drawerWidth = isSmartphone() ? '100%' : 450;

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

    const handleCodeSnippet = async () => {
        const response = await getCodeSnippet(description.slug, description.steps !== undefined);
        if (response && response.code_snippet) {
            await navigator.clipboard.writeText(response.code_snippet);
            toast("Python Code Snippet copied to clipboard", {type: "info"});
        } else {
            toast("Error while getting the code snippet \n" + response.error, {type: "error"});
        }
    }

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
                        <Grid item
                              xs={description.has_ai ? 10 : 11}
                              sm={description.has_ai ? 9 : 10}>
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
                        <Grid item xs={description.has_ai ? 2 : 1}
                              sm={description.has_ai ? 3 : 2}
                              sx={{display: 'flex', justifyContent: 'flex-end', gap: 0.5}}>
                            {description.has_ai && (
                                <Tooltip title={"AI Service"}>
                                    <PsychologyTwoTone sx={{color: "primary.main", fontSize: "1.5rem"}}/>
                                </Tooltip>
                            )}
                            <Tooltip title={
                                description.status === ServiceStatus.SLEEPING ? "Service is sleeping" :
                                    description.status === ServiceStatus.AVAILABLE ? "Service is running" :
                                        "Service status"
                            }>
                                <EnergySavingsLeafTwoTone sx={{
                                    color: description.status === ServiceStatus.SLEEPING ? "success.main" :
                                        description.status === ServiceStatus.AVAILABLE ? "primary.main" :
                                            "text.disabled",
                                    fontSize: "1.5rem"
                                }}/>
                            </Tooltip>
                        </Grid>
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
                <Box
                    mt={isSmartphone() ? 2 : 3}
                >

                    <Tooltip
                        title={`Copy the Python code snippet to use this ${description.steps ? 'pipeline' : 'service'} in your own scripts`}>
                        <Button
                            id={"code-snippet"}
                            variant={"contained"}
                            disableElevation
                            color={"secondary"}
                            fullWidth
                            size={"large"}
                            startIcon={<ContentCopyTwoTone/>}
                            onClick={() => {
                                handleCodeSnippet();
                            }}
                        >
                            Copy Code Snippet to Clipboard
                        </Button>
                    </Tooltip>
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
