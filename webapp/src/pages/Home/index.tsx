import {
    Box,
    Container,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    SelectChangeEvent,
    TextField,
    Typography
} from '@mui/material';
import React from 'react';
import ItemGrid from '../../components/ItemGrid/ItemGrid';
import { useSearchParams } from 'react-router-dom';


const Home: React.FC = () => {
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState('name-asc');
    const [searchParams] = useSearchParams();
    const history = window.history;

    const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
        if (event.target.value === '') {
            searchParams.delete('filter');
        } else {
            searchParams.set('filter', event.target.value);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
    };

    const handleOrder = (event: SelectChangeEvent) => {
        setOrderBy(event.target.value as string);
        if (event.target.value === 'name-asc') {
            searchParams.delete('orderBy');
        } else {
            searchParams.set('orderBy', event.target.value as string);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
    }

    React.useEffect(() => {
        setSearch(searchParams.get('filter') || '');
        const order = searchParams.get('orderBy');
        if (order === 'name-asc' || order === 'name-desc') {
            setOrderBy(searchParams.get('orderBy') || 'name-asc');
        } else {
            searchParams.delete('orderBy');
            setOrderBy('name-asc');
            history.pushState({}, '', `?${searchParams.toString()}`);
        }
    }, []);

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
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={8} md={10}>
                        <TextField sx={{mb: 2}} name={'search'} label={'Search'}
                               value={search} onChange={handleSearch} fullWidth
                        />
                        </Grid>
                        <Grid item xs={12} sm={4} md={2}>
                            {/* add order by name with asc and desc options */}
                            <FormControl fullWidth sx={{mb: 2}}>
                                <InputLabel id="demo-simple-select-label">Order by</InputLabel>
                                <Select
                                    labelId="demo-simple-select-label"
                                    id="demo-simple-select"
                                    value={orderBy}
                                    label="Order by"
                                    onChange={handleOrder}
                                >
                                    <MenuItem value={'name-asc'}>Name (asc)</MenuItem>
                                    <MenuItem value={'name-desc'}>Name (desc)</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>
                    <ItemGrid filter={search} orderBy={orderBy}/>
                </Container>
            </main>
        </Container>
    );
}


export default Home;
