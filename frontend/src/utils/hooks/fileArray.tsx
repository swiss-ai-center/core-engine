import { useContext } from 'react';
import { FileArrayContext } from 'utils/contexts/fileArray';

export const useFileArray = () => useContext(FileArrayContext);
