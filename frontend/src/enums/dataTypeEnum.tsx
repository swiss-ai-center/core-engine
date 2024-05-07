export enum DataType {
    IMAGE_JPEG = "image/jpeg",
    IMAGE_PNG = "image/png",
    TEXT_PLAIN = "text/plain",
    TEXT_CSV = "text/csv",
    APPLICATION_JSON = "application/json",
    APPLICATION_PDF = "application/pdf",
    AUDIO_MP3 = "audio/mpeg",
    AUDIO_OGG = "audio/ogg"
}

export const dataTypeOptions: string[] = [];

Object.values(DataType).forEach((value) => {
    dataTypeOptions.push(value);
});
