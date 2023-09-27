import graphlib
from graphviz import Digraph

correct_pipeline_blur_women = {
    "name": "Blur Women",
    "slug": "blur-women",
    "summary": "Blur Women",
    "description": "Blur Women",
    "data_in_fields": [
        {
            "name": "image",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-analyzer",
            "needs": [],
            "inputs": ["pipeline.image"],
            "service_slug": "face-analyzer"
        },
        {
            "identifier": "image-blur",
            "needs": ["face-detection"],
            "condition": "len(face-detection.result['areas']) > 0",
            "inputs": ["pipeline.image", "face-detection.result"],
            "service_slug": "image-blur"
        }
    ]
}

correct_pipeline_convert_image = {
    "name": "Convert and blur",
    "slug": "convert-blur",
    "summary": "Convert and blur",
    "description": "Convert and blur",
    "data_in_fields": [
        {
            "name": "image",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "format",
            "type": [
                "text/plain"
            ]
        },
        {
            "name": "areas",
            "type": [
                "application/json"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "image-conversion",
            "needs": [],
            "inputs": ["pipeline.image", "pipeline.format"],
            "condition": "1 == 0",
            "service_slug": "image-conversion"
        },
        {
            "identifier": "image-blur",
            "needs": ["image-conversion"],
            "inputs": ["image-conversion.result", "pipeline.areas"],
            "service_slug": "image-blur"
        }
    ]
}

correct_pipeline_simple = {
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Blur the faces in an image",
    "description": "Use Face Detection service to locate the faces in the image and send the bounding boxes to the Image Blur service to get the final result",  # noqa E501
    "data_in_fields": [
        {
            "name": "image",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "tags": [
        {
            "name": "Image Recognition",
            "acronym": "IR"
        },
        {
            "name": "Image Processing",
            "acronym": "IP"
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": [
                "pipeline.image"
            ],
            "service_slug": "face-detection"
        },
        {
            "identifier": "image-blur",
            "needs": [
                "face-detection"
            ],
            "condition": "len(face-detection.result['areas']) > 0",
            "inputs": [
                "pipeline.image",
                "face-detection.result"
            ],
            "service_slug": "image-blur"
        }
    ]
}

correct_pipeline = {
    "id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5",
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Face Blur",
    "description": "Face Blur",
    "data_in_fields": [
        {
            "name": "image_1",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "image_2",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "json",
            "type": [
                "application/json",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": ["pipeline.image_1", "pipeline.image_2"],
            "service_slug": "face-detection"
        },
        {
            "identifier": "weather-metrics",
            "needs": [],
            "inputs": ["pipeline.json"],
            "service_slug": "weather-metrics"
        },
        {
            "identifier": "image-blur",
            "needs": ["face-detection", "weather-metrics"],
            "inputs": ["weather-metrics.results", "face-detection.result"],
            "service_slug": "image-blur"
        },
        {
            "identifier": "rotate-image",
            "needs": ["image-blur"],
            "inputs": ["image-blur.result"],
            "service_slug": "rotate-image"
        },
        {
            "identifier": "crop-image",
            "needs": ["rotate-image", "weather-metrics"],
            "inputs": ["weather-metrics.json", "rotate-image.result"],
            "service_slug": "crop-image"
        }
    ]
}

incorrect_pipeline_with_input_referenced_before_being_available = {
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Face Blur",
    "description": "Face Blur",
    "data_in_fields": [
        {
            "name": "image_1",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "image_2",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "json",
            "type": [
                "application/json",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": ["pipeline.image_1", "pipeline.image_2"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        },
        {
            "identifier": "weather-metrics",
            "needs": [],
            "inputs": ["pipeline.json"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        },
        {
            "identifier": "image-blur",
            "needs": ["face-detection", "weather-metrics"],
            "inputs": ["rotate-image.results", "face-detection.result"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        },
        {
            "identifier": "rotate-image",
            "needs": ["image-blur"],
            "inputs": ["image-blur.result"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        },
        {
            "identifier": "crop-image",
            "needs": ["rotate-image", "weather-metrics"],
            "inputs": ["weather-metrics.json", "rotate-image.result"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        }
    ]
}

incorrect_pipeline_with_undefined_unit_execution_input = {
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Face Blur",
    "description": "Face Blur",
    "data_in_fields": [
        {
            "name": "image_1",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "image_2",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "json",
            "type": [
                "application/json",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": ["undefined_identifier.results"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        }
    ]
}

incorrect_pipeline_with_unknown_pipeline_input = {
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Face Blur",
    "description": "Face Blur",
    "data_in_fields": [
        {
            "name": "image_1",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "image_2",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "json",
            "type": [
                "application/json",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": ["pipeline.undefined_variable", "pipeline.image_2"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        }
    ]
}

incorrect_pipeline_with_invalid_input_syntax = {
    "name": "Face Blur",
    "slug": "face-blur",
    "summary": "Face Blur",
    "description": "Face Blur",
    "data_in_fields": [
        {
            "name": "image_1",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "image_2",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        },
        {
            "name": "json",
            "type": [
                "application/json",
                "image/png"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "result",
            "type": [
                "image/jpeg",
                "image/png"
            ]
        }
    ],
    "steps": [
        {
            "identifier": "face-detection",
            "needs": [],
            "inputs": ["invalid_input"],
            "service_id": "793db858-e66b-4ad8-a2f4-2c65c03e32e5"
        }
    ]
}

pipeline = incorrect_pipeline_with_input_referenced_before_being_available

steps = pipeline['steps']

dot = Digraph()
dot.node("pipeline", color="blue")

# Create the graph structure with the nodes and predecessors
graph = {}
referenced_steps = []
for step in steps:
    identifier = step['identifier']
    needs = step['needs']
    inputs = step['inputs']

    dot.node(identifier)

    if len(needs) == 0:
        dot.edge("pipeline", identifier, label=", ".join(inputs), color="blue")

    for need in needs:
        referenced_steps.append(need)
        filtered_inputs = [i for i in inputs if i.split('.')[0] == need]
        dot.edge(need, identifier, label=", ".join(filtered_inputs))

    graph[identifier] = needs

dot.node("outputs", color="red")
# get all the steps that are not needed by any other step
last_steps = [s for s in steps if s['identifier'] not in referenced_steps]
for last_step in last_steps:
    # optional: check the outputs to get label
    dot.edge(last_step['identifier'], "outputs", color="red")

dot.render(directory='test', format='pdf', view=True)

# Create the graph from the structure
ts = graphlib.TopologicalSorter(graph)

# # Check if the graph is valid
try:
    ts.prepare()
except Exception:
    print("The graph is not valid.")  # noqa T201

# Iterate over the graph
predecessors = set()
while ts.is_active():
    node_group = ts.get_ready()

    print(node_group)  # noqa T201

    # Iterate over the nodes that are ready
    for node in node_group:
        # Store the node in the predecessors
        predecessors.add(node)

        # Find the step definition in all the available steps
        step_found = None
        for step in steps:
            if step['identifier'] == node:
                step_found = step
                break

        inputs = step_found['inputs']

        # Check if the inputs of the step are available
        used_identifiers = []
        for input_file in inputs:
            input_split = input_file.split('.')

            if len(input_split) != 2:
                raise Exception(
                    f"The input {input_file} is not valid. It should be in the format '<identifier>.<variable>'.")

            identifier, variable = input_split
            used_identifiers.append(identifier)

            if identifier == step_found["identifier"]:
                raise Exception(f"The identifier {identifier} is the same as the current step.")

            # Check if the identifier is the pipeline
            if identifier == "pipeline":

                # Check if the variable is available in the pipeline
                variables_found = [v for v in pipeline["data_in_fields"] if v["name"] == variable]

                if len(variables_found) == 0:
                    raise Exception(f"The variable {variable} is not available in the pipeline.")
                elif len(variables_found) > 1:
                    raise Exception(f"The variable {variable} is set multiple times in the pipeline.")

                # next: Check if the variable type is compatible with the input type of the remote execution unit
            else:
                # Check if the identifier is a predecessor
                if identifier not in predecessors:
                    raise Exception(f"The identifier {identifier} is not a predecessor of the current step.")

                # Check if identifier exists in the steps
                steps_found = [s for s in steps if s['identifier'] == identifier]

                if len(steps_found) == 0:
                    raise Exception(f"The identifier {identifier} does not exist in the steps.")
                elif len(steps_found) > 1:
                    raise Exception(f"The identifier {identifier} is set multiple times in the steps.")

                # next: Get the outputs of the service in the database and check if it's compatible with the input type
                #  of the remote execution unit

            # Check if all the identifiers in the needs are used in the inputs
            for need in step_found['needs']:
                if need not in used_identifiers:
                    print(  # noqa T201
                        f"WARNING: The identifier {need} is not used in the inputs of the current step ({node})."
                        f" removed from the needs."
                    )

    ts.done(*node_group)

print("All good.")  # noqa T201
