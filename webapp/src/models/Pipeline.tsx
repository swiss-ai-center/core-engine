import { Service } from './Service';

export class Pipeline {
    id: number;
    name: string;
    slug: string;
    summary: string;
    description: string;
    url: string;
    status: string;
    services: Service[];

    constructor(id: number, name: string, slug: string, summary: string, description: string, url: string, status: string, services: Service[]) {
        this.id = id;
        this.name = name;
        this.slug = slug;
        this.summary = summary;
        this.description = description;
        this.url = url;
        this.status = status;
        this.services = services;
    }
}
