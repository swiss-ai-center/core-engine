import { Tag } from '../models/Tag';

// each tag has an acronym, name, and a unique set of colors
export const Tags = [
    {
        "acronym": "IP",
        "name": "Image Processing",
        "colors": {
            "backgroundColor": "rgba(255, 99, 132, 0.2)",
            "color": "rgba(255, 99, 132, 1)",
            "borderColor": "rgba(255, 99, 132, 1)"
        }
    },
    {
        "acronym": "IR",
        "name": "Image Recognition",
        "colors": {
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "color": "rgba(54, 162, 235, 1)",
            "borderColor": "rgba(54, 162, 235, 1)"
        }
    },
    {
        "acronym": "NLP",
        "name": "Natural Language Processing",
        "colors": {
            "backgroundColor": "rgba(255, 206, 86, 0.2)",
            "color": "rgba(255, 206, 86, 1)",
            "borderColor": "rgba(255, 206, 86, 1)"
        }
    },
    {
        "acronym": "AD",
        "name": "Anomaly Detection",
        "colors": {
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "color": "rgba(75, 192, 192, 1)",
            "borderColor": "rgba(75, 192, 192, 1)"
        }
    },
    {
        "acronym": "R",
        "name": "Recommendation",
        "colors": {
            "backgroundColor": "rgba(153, 102, 255, 0.2)",
            "color": "rgba(153, 102, 255, 1)",
            "borderColor": "rgba(153, 102, 255, 1)"
        }
    },
    {
        "acronym": "TS",
        "name": "Time Series",
        "colors": {
            "backgroundColor": "rgba(255, 159, 64, 0.2)",
            "color": "rgba(255, 159, 64, 1)",
            "borderColor": "rgba(255, 159, 64, 1)"
        }
    },
    {
        "acronym": "C",
        "name": "Clustering",
        "colors": {
            "backgroundColor": "rgba(4,176,0, 0.2)",
            "color": "rgba(4,176,0, 1)",
            "borderColor": "rgba(4,176,0, 1)"

        }
    },
    {
        "acronym": "S",
        "name": "Segmentation",
        "colors": {
            "backgroundColor": "rgba(0,72,255, 0.2)",
            "color": "rgb(0,72,255)",
            "borderColor": "rgba(0,72,255, 1)"
        }
    },
    {
        "acronym": "SR",
        "name": "Speech Recognition",
        "colors": {
            "backgroundColor": "rgba(255,0,0, 0.2)",
            "color": "rgba(255,0,0, 1)",
            "borderColor": "rgba(255,0,0, 1)"
        }
    },
    {
        "acronym": "DP",
        "name": "Data Preprocessing",
        "colors": {
            "backgroundColor": "rgba(0,255,0, 0.2)",
            "color": "rgba(0,255,0, 1)",
            "borderColor": "rgba(0,255,0, 1)"
        }
    },
    {
        "acronym": "SA",
        "name": "Sentiment Analysis",
        "colors": {
            "backgroundColor": "rgba(255,0,255, 0.2)",
            "color": "rgba(255,0,255, 1)",
            "borderColor": "rgba(255,0,255, 1)"
        }
    },
    {
        "acronym": "NN",
        "name": "Neural Networks",
        "colors": {
            "backgroundColor": "rgba(78,231,255, 0.2)",
            "color": "rgba(78,231,255, 1)",
            "borderColor": "rgba(78,231,255, 1)"
        }
    }
];

// convert preceding array to array of Tag objects
export const TagObjects: Tag[] = Tags.map((tag: any) => {
    return new Tag(tag.acronym, tag.name, tag.colors);
});
