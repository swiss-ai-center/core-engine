import type { Node, Position, XYPosition } from '@xyflow/react';
import { FieldDescription } from 'models/ExecutionUnit';

export type ElkNodeData = {
  id: string;
  label: string;
  position: XYPosition;
  data: any;
  sourceHandles: { id: string, label: string }[];
  targetHandles: { id: string, label: string }[];
  width?: number;
  height?: number;
  sourcePosition?: Position;
  targetPosition?: Position;
  dragHandle?: string;
  parentId?: string;
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

export type ElkNode = Node<EntryNodeData | ProgressNodeData | ExitNodeData>;
