import { createSlice } from '@reduxjs/toolkit'

const initialState = {
    value: true,
}

export const menuIconSlice = createSlice({
    name: 'menuIcon',
    initialState: initialState,
    reducers: {
        toggleMenuIcon: (state) => {
            state.value = !state.value
        },
        setMenuIcon: (state, action) => {
            state.value = action.payload
        }
    },
})

// Action creators are generated for each case reducer function
export const { toggleMenuIcon, setMenuIcon } = menuIconSlice.actions

export default menuIconSlice.reducer;
