import React from 'react';
import { Box, Button, Container, Tab, Tabs, Typography, CircularProgress } from '@mui/material';
import { useParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getPipelineDescription, getServiceDescription } from '../../utils/api';
import { FullScreen, useFullScreenHandle } from 'react-full-screen';
import PipelineConfiguration from '../../components/PipelineConfiguration/PipelineConfiguration';
import { ArrowBack, Fullscreen } from '@mui/icons-material';
import { useNotification } from '../../utils/useNotification';
import { useNavigate } from 'react-router-dom';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function a11yProps(index: number) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

function TabPanel(props: TabPanelProps) {
    const {children, value, index, ...other} = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Container disableGutters={true} sx={{pt: 2}}>
                    <Box>
                        {children}
                    </Box>
                </Container>
            )}
        </div>
    );
}

const Showcase: React.FC = () => {
    const {displayNotification} = useNotification();
    const params = useParams();
    const navigate = useNavigate();
    const [isReady, setIsReady] = React.useState(false);
    const [value, setValue] = React.useState(0);
    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const [description, setDescription] = React.useState<any>(null);

    const handle = useFullScreenHandle();

    const navigateBack = () => {
        navigate(-1);
    }

    const getDescription = async (id: string, type: string) => {
        setIsReady(false);
        if (!id || !type) {
            displayNotification({message: "No id or type provided", type: "warning"});
            navigateBack();
        }
        let desc = {};
        try {
            if (type === 'service') {
                desc = await getServiceDescription(id);
            } else {
                desc = await getPipelineDescription(id);
            }
            if (desc) {
                setDescription(desc);
            } else {
                displayNotification({message: "No description found with this id", type: "warning"});
                navigateBack();
            }
            setIsReady(true);
        } catch (e: any) {
            displayNotification({message: e.message, type: "error"});
            navigateBack();
        }
    }

    React.useEffect(() => {
        const id = params.id as string;
        const type = params.type as string;
        getDescription(id, type);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (<>
            {isReady ?
                <Container>
                    <main>
                        <Container maxWidth={'lg'}>
                            <Button variant={'outlined'} color={'secondary'} sx={{mt: 2}} startIcon={<ArrowBack/>}
                                    onClick={navigateBack}>
                                Back
                            </Button>
                        </Container>
                        <Box sx={{pt: 4, pb: 4}}>
                            <Container maxWidth="lg">
                                <Typography
                                    component="h1"
                                    variant="h2"
                                    align="center"
                                    color="text.primary"
                                    gutterBottom
                                >
                                    {description ? description.name : ''}
                                </Typography>
                                <Typography variant={"h5"} align={"center"}
                                            color={"text.secondary"} whiteSpace={"pre-line"}
                                            paragraph
                                >
                                    {description ? description.description : ''}
                                </Typography>
                            </Container>
                        </Box>
                        <Container sx={{py: 2}} maxWidth="lg">
                            <Box sx={{borderBottom: 1, borderColor: 'divider'}}>
                                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                                    <Tab label="Graph" {...a11yProps(0)} />
                                    <Tab label="Description" {...a11yProps(1)} />
                                    <Tab label="Results" {...a11yProps(2)} />
                                </Tabs>
                            </Box>
                            <TabPanel value={value} index={0}>
                                <Button sx={{mb: 2}} color={'secondary'} variant={'outlined'}
                                        onClick={handle.enter} startIcon={<Fullscreen/>}>
                                    Go Fullscreen
                                </Button>
                                <FullScreen handle={handle}>
                                    <Box sx={handle.active ? {height: '100%', width: '100%'} :
                                        {
                                            mb: 2,
                                            height: 500,
                                            width: '100%',
                                            border: 1,
                                            borderRadius: '5px',
                                            borderColor: 'primary.main'
                                        }}>
                                        <Board description={description}/>
                                    </Box>
                                </FullScreen>
                            </TabPanel>
                            <TabPanel value={value} index={1}>
                                <Box sx={{
                                    border: 1,
                                    borderRadius: '5px',
                                    borderColor: 'primary.main',
                                    p: 2
                                }}>
                                    <PipelineConfiguration description={description} show={true}/>
                                </Box>
                            </TabPanel>
                            <TabPanel value={value} index={2}>
                                <Box sx={{
                                    border: 1,
                                    borderRadius: '5px',
                                    borderColor: 'primary.main',
                                    p: 2
                                }}>
                                    This is the results tab
                                </Box>
                            </TabPanel>
                        </Container>
                    </main>
                </Container>
                :
                <Box sx={{py: 2, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                    <CircularProgress/>
                </Box>
            }
        </>
    );
}

export default Showcase;
