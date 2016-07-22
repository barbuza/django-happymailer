import React, { Component, PropTypes } from 'react';
import Link from 'valuelink';
import Form from './Form';
import Preview from './Preview';
import Notify from './Notify';
import cookie from 'cookie';
import qs from 'qs';

export default class App extends Component {

  static propTypes = {
    previewUrl: PropTypes.string.isRequired,
    changeUrl: PropTypes.string.isRequired,
    changelistUrl: PropTypes.string.isRequired
  };

  state = {
    template: { ...this.props.template },
    variables: [...this.props.variables],
    previewHtml: '',
    iframeKey: 0
  };

  componentDidMount() {
      this.refreshPreview();
  }

  async makeRequest(url, body) {
      const csrftoken = cookie.parse(document.cookie).csrftoken;
      const response = await fetch(url, {
          method: 'POST',
          body: body,
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded'
          }
      });
      const result = await response.json();
      // console.log(result);
      return result;
  }

  async refreshPreview() {
      console.log("preview refresh");
      const { template } = this.state;
      const { previewUrl } = this.props;
      let { variables } = this.state;
      variables = variables.reduce((res, item) => ({ ...res, [item.name]: item.value }), {});
      const body = qs.stringify({ ...template, variables: JSON.stringify(variables)});
      const result = await this.makeRequest(previewUrl, body);

      this.setState({
          previewHtml: result.html,
          iframeKey: this.state.iframeKey + 1
      });
  }
    
  async sendTest() {
      console.log('send test');
      const { template } = this.state;
      const { sendtestUrl } = this.props;
      let { variables } = this.state;
      variables = variables.reduce((res, item) => ({ ...res, [item.name]: item.value }), {});
      const body = qs.stringify({ ...template, variables: JSON.stringify(variables)});
      const result = await this.makeRequest(sendtestUrl, body);

      console.log('send result:', result);
      this.showNotify('Test Email', 'Sended to ' + result.mail);
  }
    
  async save(redirect=true) {
      const { changeUrl, changelistUrl } = this.props;
      const { template } = this.state;
      const body = qs.stringify({ ...template });
      const result = await this.makeRequest(changeUrl, body);

      if (redirect) {
          window.location = changelistUrl;
      } else {
          this.showNotify('Template saved');
      } 
  }  

  showNotify(title, msg) {
      this.refs.notificator.success(title, msg, 3000);
  }

  render() {
    const { variables, template, previewHtml, iframeKey } = this.state;
    const links = Link.state(this, 'template').pick('layout', 'enabled', 'subject', 'body');
    const variableLinks = Link.state(this, 'variables');
      
    return (
      <div className={styles.root}>
        <Form
          saveFn={::this.save}
          sendFn={::this.sendTest}
          refreshFn={::this.refreshPreview}
          links={links}
          template={template.template}
          variables={variableLinks}
        />
        <div className={styles.divider} />
        <Preview key={iframeKey} html={previewHtml} />
        <Notify ref='notificator'/>
      </div>
    );

  }

}
