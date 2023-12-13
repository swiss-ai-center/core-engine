import React, { useState, useMemo } from "react";
import { FileArrayContext } from "../contexts/fileArray";
import { FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';

export const FileArrayProvider = ({children}: any) => {
    const [fileArray, setFileArray] = useState<FieldDescriptionWithSetAndValue[]>([]);
    const value = useMemo(() => ({fileArray, setFileArray}), [fileArray, setFileArray]);

    return (
        <FileArrayContext.Provider value={value}>
            {children}
        </FileArrayContext.Provider>
    );
};
