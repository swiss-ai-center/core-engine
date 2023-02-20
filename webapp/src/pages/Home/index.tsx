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
    // this is the list of order by options, the first one is the default
    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [searchParams] = useSearchParams();
    const history = window.history;

    const handleNoFilter = () => {
        if (searchParams.toString() === '') {
            history.pushState({}, '', window.location.pathname);
        }
    }

    const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
        if (event.target.value === '') {
            searchParams.delete('filter');
        } else {
            searchParams.set('filter', event.target.value);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    };

    const handleOrder = (event: SelectChangeEvent) => {
        setOrderBy(event.target.value as string);
        if (event.target.value === orderByList[0].value) {
            searchParams.delete('orderBy');
        } else {
            searchParams.set('orderBy', event.target.value as string);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    }

    React.useEffect(() => {
        setSearch(searchParams.get('filter') || '');
        const order = searchParams.get('orderBy');
        if (orderByList.map((item) => item.value).includes(order || '')) {
            setOrderBy(searchParams.get('orderBy') || orderByList[0].value);
        } else {
            searchParams.delete('orderBy');
            setOrderBy('name-asc');
            history.pushState({}, '', `?${searchParams.toString()}`);
        }
        handleNoFilter();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
                            CSIA-PME is a project of the Swiss AI Center created by the University of Applied Sciences
                            Western Switzerland (HES-SO). The objective is to provide a platform for the development of
                            AI applications for SMEs in to accelerate the adoption of AI in Switzerland.
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
                            <FormControl fullWidth sx={{mb: 2}}>
                                <InputLabel id="demo-simple-select-label">Order by</InputLabel>
                                <Select
                                    labelId="demo-simple-select-label"
                                    id="demo-simple-select"
                                    value={orderBy}
                                    label="Order by"
                                    onChange={handleOrder}
                                >
                                    {orderByList.map((item) => (
                                        <MenuItem key={item.value} value={item.value}>{item.label}</MenuItem>
                                    ))}
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
