import { ServiceStatus } from '../enums/serviceStatusEnum';

export type JsonValue =
    | string
    | number
    | boolean
    | null
    | { [key: string]: JsonValue }
    | JsonValue[];

export type CsvColumnHint = {
    name: string;
    description?: string;
};

export type CsvFormatHint = {
    columns: CsvColumnHint[];
};

export type ZipTreeNode = {
    name: string;
    kind: "file" | "directory";
    children?: ZipTreeNode[];
};

export type ZipFormatHint = {
    tree: ZipTreeNode[];
};

export class FieldDescription {
    name: string;
    type: string[];
    format_hint?: JsonValue;
}

export class FieldDescriptionWithSetAndValue extends FieldDescription {
    value: any;
    isSet: boolean;
}

export class ExecutionUnit {
    id: string;
    name: string;
    slug: string;
    summary: string;
    description: string;
    status: ServiceStatus;
    data_in_fields: FieldDescription[];
    data_out_fields: FieldDescription[];
}
