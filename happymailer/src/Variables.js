import React from 'react';


const VariableInput = ({valueLink}) => (
  <input type='text'
         value={valueLink.value}
         onChange={e => valueLink.set(e.target.value)} />
);  

const VariableRow = ({ variableLink }) => {
  const {name, type} = variableLink.value,
        valueLink = variableLink.at('value');
  return (
      <tr>
        <th>{name}</th>
        <td>{type}</td>
        <td><VariableInput valueLink={valueLink} /></td>
      </tr>
  );
};

const Variables = ({ variables }) => (
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
        {variables.map((variable, idx) =>
          <VariableRow variableLink={variable} key={idx}/>
        )}
      </tbody>
    </table>
  </div>
);

export default Variables;