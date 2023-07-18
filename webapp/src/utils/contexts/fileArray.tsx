import { createContext } from 'react';
import { FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';

export const FileArrayContext = createContext<{ fileArray: FieldDescriptionWithSetAndValue[], setFileArray: any }>({
    fileArray: [],
    setFileArray: () => {
    }
});
