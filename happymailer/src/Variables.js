import React from 'react';

const ListVariable = ({ values }) => (
    <ul>
        {values.map((val, idx) =>
            <li key={idx}>{val}</li>
        )}
    </ul>
);

const VariableRow = ({ name, type, value, valueType }) => {
  if (valueType == 'list') {
      value = <ListVariable values={value} />;
  }
  return (
      <tr>
        <th>{name}</th>
        <td>{type}</td>
        <td>{value}</td>
      </tr>
  );
};

function flatten(array) {
    let result = [],
        nodes = [...array],
        node;

    if (!array.length) {
        return result;
    }

    node = nodes.pop();

    do {
        if (node.valueType == 'dict') {
            const children = node.value.map((child) => (
                {...child, name: node.name + '.' + child.name}
            ));
            nodes.push.apply(nodes, children);
        } else {
            result.push(node);
        }
    } while (nodes.length && (node = nodes.pop()) !== undefined);

    result.reverse();
    return result;
}

const Variables = ({ variables }) => {
    const rows = flatten(variables);

    return (
        <div className={styles.root}>
            <table className={styles.table}>
                <thead>
                <tr>
                    <th>name</th>
                    <th>type</th>
                    <th>value</th>
                </tr>
                </thead>
                <tbody>
                {rows.map((row, idx) =>
                    <VariableRow {...row} key={idx}/>
                )}
                </tbody>
            </table>
        </div>
    );
};

export default Variables;