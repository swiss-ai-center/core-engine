import { createSlice } from '@reduxjs/toolkit'

export const ColorMode = {
  LIGHT: 'light',
  DARK: 'dark'
};

const initialState = {
  value: ColorMode.LIGHT,
}

const saveToLocalStorage = (state: any) => {
  try {
    const serializedState = JSON.stringify(state);
    localStorage.setItem('colorModeState', serializedState);
  } catch (e) {
    console.error(e);
  }
}

const loadFromLocalStorage = () => {
  try {
    const serializedState = localStorage.getItem('colorModeState');
    if (serializedState === null) return initialState;
    return JSON.parse(serializedState);
  } catch (e) {
    return initialState;
  }
}

export const colorModeSlice = createSlice({
  name: 'colorMode',
  initialState: loadFromLocalStorage(),
  reducers: {
    toggleColorMode: (state) => {
      state.value = state.value === ColorMode.LIGHT ? ColorMode.DARK : ColorMode.LIGHT;
      saveToLocalStorage(state);
    },
    setColorMode: (state, action) => {
      state.value = action.payload;
      saveToLocalStorage(state);
    }
  },
})

// Action creators are generated for each case reducer function
export const {toggleColorMode, setColorMode} = colorModeSlice.actions

export default colorModeSlice.reducer
