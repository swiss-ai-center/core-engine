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
import ScrollToTop from 'react-scroll-to-top';
import { ArrowUpward } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { useFileArray } from '../../utils/hooks/fileArray';
import {handleAIToggle, handleNoFilter, handleSearch, handleTags} from "../../utils/functions";


const Home: React.FC<{ mobileOpen: boolean, handleOpen: any }> = (
    {
        mobileOpen,
        handleOpen,
    }) => {
    const colorMode = useSelector((state: any) => state.colorMode.value);
    // this is the list of order by options, the first one is the default
    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];
    const {setFileArray} = useFileArray();
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
    const [ai, setAI] = React.useState(false);
    const [searchParams] = useSearchParams();
    const history = window.history;

    const handleNoFilterWrapper = () =>   handleNoFilter(searchParams, history)
    const handleTagsWrapper = (event: SelectChangeEvent, newValue: Tag[]) => {
        handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper);
    };

    const handleAIToggleWrapper = (event: React.ChangeEvent<HTMLInputElement>) => {
        handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)
    }

    const handleSearchWrapper =  (event: React.ChangeEvent<HTMLInputElement>) => {
        handleSearch(event, setSearch, searchParams, handleNoFilterWrapper, history)
    }

    const handleOrder = (event: SelectChangeEvent) => {
        setOrderBy(event.target.value as string);
        if (event.target.value === orderByList[0].value) {
            searchParams.delete('orderBy');
        } else {
            searchParams.set('orderBy', event.target.value as string);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilterWrapper();
    }

    React.useEffect(() => {
        setFileArray([]);
        setSearch(searchParams.get('filter') || '');
        const query_tags = searchParams.getAll('tags');
        setTags(query_tags.map((tag) => TagObjects.filter((tagObject) => tagObject.acronym === tag)[0]));
        setAI(searchParams.get('ai') === 'true');
        const order = searchParams.get('orderBy');
        if (orderByList.map((item) => item.value).includes(order || '')) {
            setOrderBy(order || orderByList[0].value);
        } else {
            searchParams.delete('orderBy');
            setOrderBy('name-asc');
            history.pushState({}, '', `?${searchParams.toString()}`);
        }
        handleNoFilterWrapper();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <Box sx={{display: 'flex'}}>
            <ScrollToTop smooth component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                        sx={{paddingTop: '2px'}}/>}/>
            <FilterDrawer
                mobileOpen={mobileOpen} handleOpen={handleOpen}
                orderBy={orderBy} handleOrder={handleOrder} orderByList={orderByList}
                search={search} handleSearch={handleSearch}
                tags={tags} handleTags={handleTags}
                ai={ai} handleAIToggle={handleAIToggle}
            />
            <Box component={"main"} sx={{flexGrow: 1, py: 4}}>
                <Toolbar/>
                <Container maxWidth={false} sx={{mb: 4}}>
                    <Typography
                        component={"h1"}
                        variant={"h2"}
                        align={"center"}
                        color={"text.primary"}
                        gutterBottom
                    >
                        Swiss AI Center
                    </Typography>
                    <Typography variant={"h5"} align={"justify"} color={"text.secondary"} paragraph>
                        The Swiss AI Center is a project created by the University of Applied Sciences
                        Western Switzerland (HES-SO). The objective is to provide a platform to develop
                        AI applications for SMEs to accelerate its adoption in Switzerland.
                    </Typography>
                </Container>
                <Container maxWidth={false}>
                    <ItemGrid filter={search} orderBy={orderBy} tags={tags} handleTags={handleTags}
                              ai={ai} handleAIToggle={handleAIToggle} addService={null}/>
                </Container>
                <Container maxWidth={false}>
                    <Copyright/>
                </Container>
            </Box>
        </Box>
    );
}


export default Home;
