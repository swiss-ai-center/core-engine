import { Node } from 'reactflow';
import { FieldDescription } from './ExecutionUnit';

export type ElkNodeData = {
    label: string;
    sourceHandles: { id: string, label: string }[];
    targetHandles: { id: string, label: string }[];
};

export type ProgressNodeData = ElkNodeData & {
    type: string;
    service_id: string;
    service_slug: string;
};

export type EntryNodeData = ElkNodeData & {
    executionType: string;
    data_in_fields: FieldDescription[];
};

export type ExitNodeData = ElkNodeData & {
    data_out_fields: FieldDescription[];
};

export type ElkNode = Node<EntryNodeData | ProgressNodeData | ExitNodeData, 'elk'>;
