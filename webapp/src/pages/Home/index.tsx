import {
    Box,
    Container,
    SelectChangeEvent,
    Typography,
    Toolbar,
} from '@mui/material';
import React from 'react';
import ItemGrid from '../../components/ItemGrid/ItemGrid';
import { FilterDrawer } from '../../components/FilterDrawer/FilterDrawer';
import { useSearchParams } from 'react-router-dom';
import Copyright from '../../components/Copyright/Copyright';
import { Tag } from '../../models/Tag';
import { TagObjects } from '../../enums/tagEnums';


const Home: React.FC<{ mobileOpen: boolean }> = ({mobileOpen}) => {
    // this is the list of order by options, the first one is the default
    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
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

    const handleTags = (event: SelectChangeEvent, newValue: Tag[]) => {
        setTags(newValue);
        if (newValue.length === 0) {
            searchParams.delete('tags');
        } else {
            searchParams.delete('tags');
            newValue.forEach((tag) => {
                searchParams.append('tags', tag.acronym);
            });
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    }

    React.useEffect(() => {
        setSearch(searchParams.get('filter') || '');
        const query_tags = searchParams.getAll('tags');
        setTags(query_tags.map((tag) => TagObjects.filter((tagObject) => tagObject.acronym === tag)[0]));
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
        <Box sx={{display: 'flex'}}>
            <FilterDrawer
                mobileOpen={mobileOpen}
                orderBy={orderBy} handleOrder={handleOrder} orderByList={orderByList}
                search={search} handleSearch={handleSearch}
                tags={tags} handleTags={handleTags}
            />
            <Box component="main" sx={{flexGrow: 1, p: 2, pt: 4, pb: 3}}>
                <Toolbar/>
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
                        AI applications for SMEs to accelerate its adoption in Switzerland.
                    </Typography>
                </Container>
                <Container sx={{py: 4}} maxWidth="lg">
                    <ItemGrid filter={search} skip={0} limit={20} orderBy={orderBy} tags={tags} />
                </Container>
                <Container maxWidth="lg" sx={{pb: 0}}>
                    <Copyright/>
                </Container>
            </Box>
        </Box>
    );
}


export default Home;
