import React from 'react';
import { Box, Button, Container, Typography } from '@mui/material';
import { Link, useSearchParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getDescription, getServices } from '../../utils/api';
import { FullScreen, useFullScreenHandle } from 'react-full-screen';
import { fitView } from 'react-flow-renderer/dist/esm/store/utils';
import { useReactFlow } from 'reactflow';

const Showcase: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const name = searchParams.get('name') || '';
    const description = searchParams.get('description') || '';

    const [services, setServices] = React.useState<any>([]);

    const handle = useFullScreenHandle();

    const getPipeline = async (name: any) => {
        const pipeline = await getDescription(name);
        if (pipeline) {
            setServices(pipeline);
        } else {
            setServices([]);
            console.log("No services found");
        }
    }

    React.useEffect(() => {
        getPipeline(name);
    }, []);

    return (
        <Container>
            <main>
                <Container maxWidth={'lg'}>
                    <Link to="/">
                        <Button variant={'outlined'} sx={{mt: 2}}>Back</Button>
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
                        <Typography variant="h5" align="justify" color="text.secondary" paragraph>
                            {description}
                        </Typography>
                    </Container>
                </Box>
                <Container sx={{py: 2}} maxWidth="lg">
                    <Button sx={{mb: 2}} variant={'outlined'} onClick={handle.enter}>
                        Go Fullscreen
                    </Button>
                    <FullScreen handle={handle}>
                        <Box sx={handle.active ? {height: '100%', width: '100%'} :
                            {mb: 2, height: 500, width: '100%', border: 1, borderRadius: '5px', borderColor: 'primary.main'}}>
                            <Board service={services}/>
                        </Box>
                    </FullScreen>
                </Container>
            </main>
        </Container>
    );
}

export default Showcase;
