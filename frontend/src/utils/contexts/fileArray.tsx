import { FieldDescriptionWithSetAndValue } from 'models/ExecutionUnit';
import { createContext } from 'react';

export const FileArrayContext = createContext<{ fileArray: FieldDescriptionWithSetAndValue[], setFileArray: any }>({
    fileArray: [],
    setFileArray: () => {
    }
});
