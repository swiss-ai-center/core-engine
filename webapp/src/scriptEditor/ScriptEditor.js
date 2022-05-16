import { useEffect } from 'react';
import ReactJson from 'react-json-view';

export default function ScriptEditor({service, setService}) {

  return (
    <div className="column is-3">
      <ReactJson
        indentWidth={2}
        collapsed={2}
        src={[
          {
            task: 'Learn React',
            done: true,
          },
          {
            task: 'Write Book',
            done: false,
            test: {
              ouw: 100,
              asdf: {
                sadfasdfasdf: 97832,
                lits: [2,3,"fv","fs","s","sdf","asd",34,]
              }
            }
          }
        ]}
      />
    </div>
  )
}
