import { FieldDescriptionWithSetAndValue } from 'models/ExecutionUnit';
import React, { useMemo, useState } from "react";
import { FileArrayContext } from "../contexts/fileArray";

export const FileArrayProvider = ({children}: any) => {
    const [fileArray, setFileArray] = useState<FieldDescriptionWithSetAndValue[]>([]);
    const value = useMemo(() => ({fileArray, setFileArray}), [fileArray, setFileArray]);

    return (
        <FileArrayContext.Provider value={value}>
            {children}
        </FileArrayContext.Provider>
    );
};
