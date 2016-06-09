import React from 'react';

const Variable = ({ name, type, value }) => (
  <tr>
    <th>{name}</th>
    <td>{type}</td>
    <td>{value}</td>
  </tr>
);

const Variables = ({ variables }) => (
  <div className={styles.root}>
    <div className={styles.title}>Variables:</div>
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
          <Variable {...variable} key={idx}/>
        )}
      </tbody>
    </table>
  </div>
);

export default Variables;
