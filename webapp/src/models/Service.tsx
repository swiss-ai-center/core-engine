export class FieldDescription {
    name: string;
    type: string[];
}

export class FieldDescriptionWithSetAndValue extends FieldDescription {
    value: any;
    isSet: boolean;
}

export class Service {
    id: number;
    name: string;
    slug: string;
    summary: string;
    description: string;
    url: string;
    status: string;
    data_in_fields: FieldDescription[];
    data_out_fields: FieldDescription[];
}
