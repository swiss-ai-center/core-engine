import React from 'react';
import { Box, Button, Container, Tab, Tabs, Typography } from '@mui/material';
import { Link, useSearchParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getServiceDescription } from '../../utils/api';
import { FullScreen, useFullScreenHandle } from 'react-full-screen';
import PipelineConfiguration from '../../components/PipelineConfiguration/PipelineConfiguration';
import { ArrowBack, Fullscreen } from '@mui/icons-material';

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
    const [searchParams] = useSearchParams();
    const name = searchParams.get('name') || '';
    const summary = searchParams.get('summary') || '';

    const [value, setValue] = React.useState(0);
    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const [services, setServices] = React.useState<any>([]);

    const handle = useFullScreenHandle();

    const getPipeline = async (name: any) => {
        const pipeline = await getServiceDescription(name);
        if (pipeline) {
            console.log(pipeline);
            setServices(pipeline);
        } else {
            setServices([]);
            console.log("No services found");
        }
    }

    React.useEffect(() => {
        getPipeline(name);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <Container>
            <main>
                <Container maxWidth={'lg'}>
                    <Link to="/">
                        <Button variant={'outlined'} sx={{mt: 2}} startIcon={<ArrowBack />}>Back</Button>
                    </Link>
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
                            {name}
                        </Typography>
                        <Typography variant="h5" align="center" color="text.secondary" paragraph>
                            {summary}
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
                        <Button sx={{mb: 2}} variant={'outlined'} onClick={handle.enter} startIcon={<Fullscreen />}>
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
                                <Board services={services}/>
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
                            <PipelineConfiguration service={services} show={true}/>
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
    );
}

export default Showcase;
