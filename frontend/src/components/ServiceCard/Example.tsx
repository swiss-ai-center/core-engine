import React, {ReactNode} from "react";


const ExampleComponent : React.FC<{
    params:  any}> = ({params}) => {

    let variable = "some text";

    function example () {
        return <p>some text</p>
    }

    return (
        <>
            <h1>Title</h1>
            {example()}
            <p>{variable}</p>
        </>
    );
}

export default ExampleComponent;