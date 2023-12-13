import { useContext } from 'react';
import { FileArrayContext } from '../contexts/fileArray';

export const useFileArray = () => useContext(FileArrayContext);
