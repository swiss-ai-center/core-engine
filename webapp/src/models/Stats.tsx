import { RunState } from '../utils/reducers/runStateSlice';

class StatusCount {
    status: RunState;
    count: number;
}

class ServiceStats {
    service_id: string;
    service_name: string;
    total: number;
    status: StatusCount[];
}

class PipelineStats {
    pipeline_id: string;
    pipeline_name: string;
    total: number;
    status: StatusCount[];
}

export class Stats {
    total: number;
    summary: StatusCount[];
    services: ServiceStats[];
    pipelines: PipelineStats[];
}
