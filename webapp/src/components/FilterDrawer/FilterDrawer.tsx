import {
    Autocomplete,
    Box, Checkbox,
    Drawer, FormControl, IconButton, InputLabel, MenuItem, Select, TextField,
    Toolbar,
} from '@mui/material';
import React from 'react';
import {
    CheckBox as CheckBoxIcon,
    CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon,
    Clear as ClearIcon,
} from '@mui/icons-material';
import { TagNames } from '../../enums/tagEnums';

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
const checkedIcon = <CheckBoxIcon fontSize="small"/>;
const isSmartphone = (): boolean => {
    return window.innerWidth < 600;
}
const drawerWidth = isSmartphone() ? '100%' : 400;

export const FilterDrawer: React.FC<{
    mobileOpen: boolean,
    handleOpen: any,
    search: string,
    handleSearch: any,
    orderBy: string,
    handleOrder: any,
    orderByList: any[]
    tags: string[],
    handleTags: any,
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
      }) => {

    const drawer = (
        <>
            <Toolbar/>
            <Box sx={{overflow: 'auto'}}>
                <Box sx={{ml: 3}}>
                    <h3>Filters</h3>
                </Box>
                <Box sx={{mx: 3}}>
                    <TextField sx={{mb: 2}} name={'search'} label={'Search'}
                               value={search} onChange={handleSearch} fullWidth
                               InputProps={{
                                   endAdornment: search ? (
                                       <IconButton size="small" onClick={() => handleSearch({target: {value: ''}})}>
                                           <ClearIcon/>
                                       </IconButton>
                                   ) : undefined
                               }}
                    />
                    <Autocomplete
                        multiple
                        sx={{mb: 2}}
                        id="tags-filter"
                        options={Object.values(TagNames)}
                        disableCloseOnSelect
                        getOptionLabel={(option) => option}
                        renderOption={(props, option, {selected}) => (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    color={'primary'}
                                    checked={tags.includes(option)}
                                />
                                {option}
                            </li>
                        )}
                        onChange={handleTags}
                        renderInput={(params) => (
                            <TextField {...params} label="Tags" placeholder="Tags"/>
                        )}
                        value={tags}
                    />
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
                </Box>
            </Box>
        </>
    );


    return (
        <Box
            component="nav"
            sx={{width: {md: drawerWidth}, flexShrink: {md: 0}}}
            aria-label="mailbox folders"
        >
            {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
            <Drawer
                variant="temporary"
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
                variant="permanent"
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
