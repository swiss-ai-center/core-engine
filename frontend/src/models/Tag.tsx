class ColorSettings {
    backgroundColor: string;
    color: string;
    borderColor: string;
}

export class Tag {
    acronym: string;
    name: string;
    colors: ColorSettings;

    constructor(acronym: string, name: string, colors: ColorSettings) {
        this.acronym = acronym;
        this.name = name;
        this.colors = colors;
    }
}
