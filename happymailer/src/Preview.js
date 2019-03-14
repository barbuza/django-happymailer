import React from 'react';

export default class Preview extends React.PureComponent {

  componentDidMount() {
    this.setIframeContent();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.html !== this.props.html) {
      this.setIframeContent();
    }
  }

  render() {
    return (
      <div className={styles.root}>
        <div className={styles.iphone5}>
          <iframe
            src="about:blank"
            ref="iframe"
            className={styles.frame}
          />
        </div>
      </div>
    );
  }

  setIframeContent() {
    this.refs.iframe.contentDocument.write(this.props.html);
    this.refs.iframe.contentDocument.close();
  }

}
