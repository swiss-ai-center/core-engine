export class FieldDescription {
    name: string;
    type: string[];
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
    status: string;
    data_in_fields: FieldDescription[];
    data_out_fields: FieldDescription[];
}
