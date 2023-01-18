import { Box, Container, TextField, Typography } from '@mui/material';
import React from 'react';
import ItemGrid from '../../components/ItemGrid/ItemGrid';


const Home: React.FC = () => {
    const [search, setSearch] = React.useState('');

    const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
    };

    return (
        <Container>
            <main>
                <Box sx={{pt: 8, pb: 6}}>
                    <Container maxWidth="lg">
                        <Typography
                            component="h1"
                            variant="h2"
                            align="center"
                            color="text.primary"
                            gutterBottom
                        >
                            CSIA-PME
                        </Typography>
                        <Typography variant="h5" align="justify" color="text.secondary" paragraph>
                            CSIA-PME is a project of the Swiss AI Center of the University of Applied Sciences Western
                            Switzerland HES-SO. The objective is to provide a platform for the development of AI
                            applications for SMEs in different domains.
                        </Typography>
                    </Container>
                </Box>
                <Container sx={{py: 8}} maxWidth="lg">
                    <TextField sx={{mb: 2}} name={'search'} label={'Search'} value={search} onChange={handleSearch} fullWidth />
                    <ItemGrid filter={search}/>
                </Container>
            </main>
        </Container>
    );
}


export default Home;
