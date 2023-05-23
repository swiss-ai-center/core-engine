import { Tag } from '../models/Tag';

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
            "backgroundColor": "rgba(255, 99, 132, 0.2)",
            "color": "rgba(255, 99, 132, 1)",
            "borderColor": "rgba(255, 99, 132, 1)"
        }
    },
    {
        "acronym": "S",
        "name": "Segmentation",
        "colors": {
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "color": "rgba(54, 162, 235, 1)",
            "borderColor": "rgba(54, 162, 235, 1)"
        }
    },
    {
        "acronym": "SR",
        "name": "Speech Recognition",
        "colors": {
            "backgroundColor": "rgba(255, 206, 86, 0.2)",
            "color": "rgba(255, 206, 86, 1)",
            "borderColor": "rgba(255, 206, 86, 1)"
        }
    },
    {
        "acronym": "DP",
        "name": "Data Preprocessing",
        "colors": {
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "color": "rgba(75, 192, 192, 1)",
            "borderColor": "rgba(75, 192, 192, 1)"
        }
    },
    {
        "acronym": "SA",
        "name": "Sentiment Analysis",
        "colors": {
            "backgroundColor": "rgba(153, 102, 255, 0.2)",
            "color": "rgba(153, 102, 255, 1)",
            "borderColor": "rgba(153, 102, 255, 1)"
        }
    }
];

// convert preceding array to array of Tag objects
export const TagObjects: Tag[] = Tags.map((tag: any) => {
    return new Tag(tag.acronym, tag.name, tag.colors);
});

//
// export const TagNames = {
//     "IP": "Image Processing",
//     "IR": "Image Recognition",
//     "NLP": "Natural Language Processing",
//     "AD": "Anomaly Detection",
//     "R": "Recommendation",
//     "TS": "Time Series",
//     "C": "Clustering",
//     "S": "Segmentation",
//     "SR": "Speech Recognition",
//     "DP": "Data Preprocessing",
//     "SA": "Sentiment Analysis"
// };
//
// export const TagColors: any = {
//     "IP": {
//         backgroundColor: "rgba(255, 99, 132, 0.2)",
//         color: "rgba(255, 99, 132, 1)",
//         borderColor: "rgba(255, 99, 132, 1)"
//     },
//     "IR": {
//         backgroundColor: "rgba(54, 162, 235, 0.2)",
//         color: "rgba(54, 162, 235, 1)",
//         borderColor: "rgba(54, 162, 235, 1)"
//     },
//     "NLP": {
//         backgroundColor: "rgba(255, 206, 86, 0.2)",
//         color: "rgba(255, 206, 86, 1)",
//         borderColor: "rgba(255, 206, 86, 1)"
//     },
//     "AD": {
//         backgroundColor: "rgba(75, 192, 192, 0.2)",
//         color: "rgba(75, 192, 192, 1)",
//         borderColor: "rgba(75, 192, 192, 1)"
//     },
//     "R": {
//         backgroundColor: "rgba(153, 102, 255, 0.2)",
//         color: "rgba(153, 102, 255, 1)",
//         borderColor: "rgba(153, 102, 255, 1)"
//     },
//     "TS": {
//         backgroundColor: "rgba(255, 159, 64, 0.2)",
//         color: "rgba(255, 159, 64, 1)",
//         borderColor: "rgba(255, 159, 64, 1)"
//     },
//     "C": {
//         backgroundColor: "rgba(255, 99, 132, 0.2)",
//         color: "rgba(255, 99, 132, 1)",
//         borderColor: "rgba(255, 99, 132, 1)"
//     },
//     "S": {
//         backgroundColor: "rgba(54, 162, 235, 0.2)",
//         color: "rgba(54, 162, 235, 1)",
//         borderColor: "rgba(54, 162, 235, 1)"
//     },
//     "SR": {
//         backgroundColor: "rgba(255, 206, 86, 0.2)",
//         color: "rgba(255, 206, 86, 1)",
//         borderColor: "rgba(255, 206, 86, 1)"
//     },
//     "DP": {
//         backgroundColor: "rgba(75, 192, 192, 0.2)",
//         color: "rgba(75, 192, 192, 1)",
//         borderColor: "rgba(75, 192, 192, 1)"
//     },
//     "SA": {
//         backgroundColor: "rgba(153, 102, 255, 0.2)",
//         color: "rgba(153, 102, 255, 1)",
//         borderColor: "rgba(153, 102, 255, 1)"
//     }
// }
