import {
    Box,
    Container,
    SelectChangeEvent,
    Toolbar,
} from '@mui/material';
import React, { useCallback } from 'react';
import ItemGrid from '../../components/ItemGrid/ItemGrid';
import { FilterDrawer } from '../../components/FilterDrawer/FilterDrawer';
import { useSearchParams } from 'react-router-dom';
import Copyright from '../../components/Copyright/Copyright';
import { Tag } from '../../models/Tag';
import { TagObjects } from '../../enums/tagEnums';
import ScrollToTop from 'react-scroll-to-top';
import { ArrowUpward } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useFileArray } from '../../utils/hooks/fileArray';
import { setMenuIcon } from '../../utils/reducers/menuIconSlice';


const Home: React.FC<{ mobileOpen: boolean, handleOpen: any }> = (
    {
        mobileOpen,
        handleOpen,
    }) => {
    const dispatch = useDispatch();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    // this is the list of order by options, the first one is the default
    const orderByList = React.useMemo(() => [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'}
    ], []);
    const {setFileArray} = useFileArray();
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
    const [ai, setAI] = React.useState(false);
    const [searchParams] = useSearchParams();
    const history = window.history;

    const handleNoFilter = useCallback(() => {
        if (searchParams.toString() === '') {
            history.pushState({}, '', window.location.pathname);
        }
    }, [searchParams, history]);

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

    const removeDuplicates = (arr: Tag[]) => {
        return arr.filter((v, i, a) => a.findIndex(t => (t.acronym === v.acronym)) === i);
    }

    const arrayEquals = (a: Tag[], b: Tag[]) => {
        return Array.isArray(a) && Array.isArray(b) && a.length === b.length &&
            a.every((val, index) => val === b[index]);
    }

    const handleTags = (_: SelectChangeEvent, newValue: Tag[]) => {
        newValue = removeDuplicates(newValue);
        if (arrayEquals(newValue, tags)) {
            return;
        }
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

    const handleAIToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
        setAI(event.target.checked);
        if (event.target.checked) {
            searchParams.set('ai', 'true');
        } else {
            searchParams.delete('ai');
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    }

    // rewrite last useEffect in a clean way
    // the same logic but with a cleaner code
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
        handleNoFilter();
    }, [searchParams, setFileArray, history, orderByList, handleNoFilter]);

    React.useEffect(() => {
        dispatch(setMenuIcon(true));
    });

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
                <Container maxWidth={false}>
                    <ItemGrid filter={search} orderBy={orderBy} tags={tags} handleTags={handleTags}
                              ai={ai} handleAIToggle={handleAIToggle}/>
                </Container>
                <Container maxWidth={false}>
                    <Copyright/>
                </Container>
            </Box>
        </Box>
    );
}


export default Home;
