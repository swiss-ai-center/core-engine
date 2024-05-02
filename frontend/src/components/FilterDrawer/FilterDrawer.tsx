import {
    Autocomplete,
    Box,
    Button,
    Checkbox,
    Drawer,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    Link as URLLink,
    MenuItem,
    Select,
    Stack,
    styled,
    Switch,
    TextField,
    Toolbar,
    Typography,
} from '@mui/material';
import React from 'react';
import {
    ApiRounded,
    CheckBox as CheckBoxIcon,
    CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon,
    Clear as ClearIcon, Psychology,
} from '@mui/icons-material';
import { TagObjects } from '../../enums/tagEnums';
import { Tag } from '../../models/Tag';
import { isSmartphone } from '../../utils/functions';

const icon = <CheckBoxOutlineBlankIcon fontSize={"small"}/>;
const checkedIcon = <CheckBoxIcon fontSize={"small"}/>;
const drawerWidth = isSmartphone() ? '100%' : 500;

export const FilterDrawer: React.FC<{
    mobileOpen: boolean,
    handleOpen: any,
    search: string,
    handleSearch: any,
    orderBy: string,
    handleOrder: any,
    orderByList: any[]
    tags: Tag[],
    handleTags: any,
    ai: boolean,
    handleAIToggle: any,
}> = ({
          mobileOpen,
          handleOpen,
          search,
          handleSearch,
          orderBy,
          handleOrder,
          orderByList,
          tags,
          handleTags,
          ai,
          handleAIToggle,
      }) => {

    const CustomSwitch = styled(Switch)(({ theme }) => ({
        padding: 8,
        '& .MuiSwitch-track': {
            borderRadius: 22 / 2,
            '&::before, &::after': {
                content: '""',
                position: 'absolute',
                top: '50%',
                transform: 'translateY(-50%)',
                width: 16,
                height: 16,
            },
            '&::before': {
                backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
                    theme.palette.getContrastText(theme.palette.primary.main),
                )}" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>')`,
                left: 12,
            },
            '&::after': {
                backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
                    theme.palette.getContrastText(theme.palette.primary.main),
                )}" d="M19,13H5V11H19V13Z" /></svg>')`,
                right: 12,
            },
        },
        '& .MuiSwitch-thumb': {
            boxShadow: 'none',
            width: 16,
            height: 16,
            margin: 2,
        },
    }));

    const drawer = (
        <>
            <Toolbar/>
            <Box sx={{overflow: 'auto'}}>
                <Box sx={{ml: 3}}>
                    <h3>Filters</h3>
                </Box>
                <Box sx={{mx: 3, pb: 2}}>
                    <TextField sx={{mb: 2}} name={"search-field"} label={"Search"}
                               value={search} onChange={handleSearch} fullWidth
                               InputProps={{
                                   endAdornment: search ? (
                                       <IconButton size={"small"} onClick={() => handleSearch({target: {value: ''}})}>
                                           <ClearIcon/>
                                       </IconButton>
                                   ) : undefined
                               }}
                    />
                    <Autocomplete
                        multiple
                        sx={{mb: 2}}
                        options={TagObjects}
                        disableCloseOnSelect
                        getOptionLabel={(option) => option.name}
                        isOptionEqualToValue={(option, value) => option.acronym === value.acronym}
                        renderOption={(props, option, {selected}) => (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    color={"primary"}
                                    value={option.acronym}
                                    checked={selected}
                                />
                                {option.name}
                            </li>
                        )}
                        onChange={handleTags}
                        renderInput={(params) => (
                            <TextField {...params} label={"Tags"} placeholder={"Tags"}/>
                        )}
                        value={tags}
                    />
                    <FormControl fullWidth sx={{mb: 2}}>
                        <InputLabel id={"order-by-label"} htmlFor={"order-by-select"}>Order by</InputLabel>
                        <Select
                            labelId={"order-by-label"}
                            id={"order-by-select"}
                            value={orderBy}
                            label={"Order by"}
                            onChange={handleOrder}
                        >
                            {orderByList.map((item) => (
                                <MenuItem key={item.value} value={item.value}>{item.label}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth sx={{mb: 2}}>
                        <Grid component={"label"} container alignItems={"center"} spacing={1}>
                            <Grid item sx={{mt: 2}}>
                                <Typography component={Stack} direction={"row"} alignItems={"center"} paragraph
                                            sx={{fontSize: "0.9rem"}}
                                >
                                    <Psychology sx={{fontSize: "1.6rem", marginRight: "0.5rem"}} />
                                    All Services
                                </Typography>
                            </Grid>
                            <Grid item>
                                <CustomSwitch
                                    checked={ai}
                                    onChange={() => {
                                        handleAIToggle({target: {checked: !ai}});
                                    }}
                                    value={ai}
                                />
                            </Grid>
                            <Grid item sx={{mt: 2}}>
                                <Typography component={Stack} direction={"row"} alignItems={"center"} paragraph
                                            sx={{fontSize: "0.9rem"}}
                                >
                                    AI Services Only
                                    <Psychology sx={{fontSize: "1.6rem", marginLeft: "0.5rem"}} color={"primary"}/>
                                </Typography>
                            </Grid>
                        </Grid>
                    </FormControl>
                    <Button
                        id={"reset-filters-button"}
                        variant={"contained"}
                        disableElevation
                        color={"secondary"}
                        fullWidth
                        size={"large"}
                        onClick={() => {
                            handleSearch({target: {value: ''}});
                            handleTags(null, []);
                            handleOrder({target: {value: orderByList[0].value}});
                            handleAIToggle({target: {checked: false}});
                            if (isSmartphone()) handleOpen();
                        }}
                    >
                        Reset filters
                    </Button>
                </Box>
            </Box>
            <Box sx={{position: 'fixed', bottom: 20, left: 20, zIndex: 1000}}>
                <URLLink href={`${process.env.REACT_APP_ENGINE_URL}/docs`} target={"_blank"}>
                    <Button color={"secondary"} variant={"outlined"}
                            startIcon={<ApiRounded/>}>
                        Backend
                    </Button>
                </URLLink>
            </Box>
        </>
    );


    return (
        <Box
            component={"nav"}
            sx={{width: {md: drawerWidth}, flexShrink: {md: 0}}}
        >
            {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
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
