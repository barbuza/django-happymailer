import React, { Component, PropTypes } from 'react';
import cookie from 'cookie';
import qs from 'qs';

export default class Preview extends Component {

  static propTypes = {
    previewUrl: PropTypes.string.isRequired,
    template: PropTypes.object.isRequired
  };

  state = {
    iframeKey: 1,
    previewHtml: ''
  };

  componentDidMount() {
    this.refresh();
  }

  async refresh() {
    const { previewUrl, template } = this.props;
    let { variables } = this.props;
    const csrftoken = cookie.parse(document.cookie).csrftoken;
    variables = variables.reduce((res, item) => ({ ...res, [item.name]: item.value }), {});
    const response = await fetch(previewUrl, {
      method: 'POST',
      body: qs.stringify({ ...template, variables: JSON.stringify(variables) }),
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    const result = await response.json();
    this.setState({
      iframeKey: this.state.iframeKey + 1,
      previewHtml: result.html
    });
  }

  render() {
    const { iframeKey, previewHtml } = this.state;
    return (
      <div className={styles.root}>
        <div className={styles.iphone5}>
          <iframe seamless
                  key={iframeKey}
                  src={`data:text/html;charset=utf-8,${previewHtml}`}
                  className={styles.frame}/>
        </div>
      </div>
    );
  }

}
