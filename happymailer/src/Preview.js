import React from 'react';

const Preview = ({html, iframeKey})=> (
  <div className={styles.root}>
    <div className={styles.iphone5}>
      <iframe seamless
              key={iframeKey}
              src={`data:text/html;charset=utf-8,${html}`}
              className={styles.frame}/>
    </div>
  </div>
);

export default Preview;
