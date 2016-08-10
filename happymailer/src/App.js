import React, { Component, PropTypes } from 'react';
import Link from 'valuelink';
import Form from './Form';
import Preview from './Preview';
import Notify from './Notify';
import cookie from 'cookie';
import qs from 'qs';

function reduce_vars(items) {
    return items.reduce((prev, item) => {
        const value = (item.valueType == 'dict') ? reduce_vars(item.value) : item.value;
        return {...prev, [item.name]: value};
    }, {});
}

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
      return result;
  }

  async refreshPreview() {
      console.log("preview refresh");
      const { template } = this.state;
      const { previewUrl } = this.props;
      let { variables } = this.state;
      variables = reduce_vars(variables);
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
      variables = reduce_vars(variables);
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
          // this.showNotify('Template saved');
          window.location = changeUrl;
      } 
  }  

  async loadVersion(versionId) {
    const { changelistUrl } = this.props;
    const { template } = this.state;
    const url = changelistUrl + `${template.pk}/version/${versionId}/`;
    const result = await this.makeRequest(url, null);
    console.log('version data:', result);
    return result;
  }

  showNotify(title, msg) {
      this.refs.notificator.success(title, msg, 3000);
  }

  render() {
    const { variables, template, previewHtml, iframeKey } = this.state;
    const links = Link.state(this, 'template').pick('layout', 'enabled', 'subject', 'body');

    const actions = {
      save: ::this.save,
      sendTest: ::this.sendTest,
      refresh: ::this.refreshPreview,
      loadVersion: ::this.loadVersion
    };

    return (
      <div className={styles.root}>
        <Form
          actions={actions}
s         links={links}
          template={template.template}
          variables={variables}
        />
        <div className={styles.divider} />
        <Preview key={iframeKey} html={previewHtml} />
        <Notify ref='notificator'/>
      </div>
    );

  }

}
