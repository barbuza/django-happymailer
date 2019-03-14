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

async function request(method, url, data = null) {
  const csrfToken = cookie.parse(document.cookie).csrftoken;
  let options = {
    method,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken
    }
  };

  if (data) {
    options.body = qs.stringify(data);
  }

  const response = await fetch(url, options);

  if (response.status < 200 || response.status >= 300) {
    const error = new Error(response.statusText || `error ${response.status}`);
    error.response = await response.json();
    throw error;
  }

  const result = await response.json();
  return result;
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
    iframeKey: 0,
    errors: {},
  };

  componentDidMount() {
      this.preview();
  }

  setError(errors) {
    this.setState({
      errors
    });
  }

  preview = async (sendTest=false) => {
      const { template } = this.state;
      const { previewUrl } = this.props;
      let { variables } = this.state;
      variables = reduce_vars(variables);

      try {
        const result = await request('post', previewUrl, {
          ...template,
          variables: JSON.stringify(variables),
          send_test: sendTest
        });

        this.setState({
          previewHtml: result.html,
          iframeKey: this.state.iframeKey + 1,
          errors: {}
        });

        if (sendTest) {
          this.showNotify('Test email', 'Sent to ' + result.email);
        }

      } catch(err) {
        this.setError(err.response);
      }
  }

  save = async (redirect=true) => {
      const { changeUrl, changelistUrl } = this.props;
      const { template } = this.state;

      try {
        const result = await request('post', changeUrl, {
          ...template
        });

        if (redirect) {
          window.location = changelistUrl;
        } else {
          window.location = changeUrl;
        }

      } catch(err) {
        this.setError(err.response);
      }
  }

  loadVersion = async (versionId) => {
    const { changelistUrl } = this.props;
    const { template } = this.state;
    const url = changelistUrl + `${template.pk}/version/${versionId}/`;

    try {
      const result = await request('post', url, null);
      return result;

    } catch(err) {
      this.setError(err.response);
      throw err;
    }
  }

  showNotify(title, msg) {
      this.refs.notificator.success(title, msg, 3000);
  }

  render() {
    const { variables, template, previewHtml, iframeKey, errors } = this.state;
    const links = Link.state(this, 'template').pick('layout', 'enabled', 'subject', 'body');

    const actions = {
      save: this.save,
      preview: this.preview,
      loadVersion: this.loadVersion,
    };

    return (
      <div className={styles.root}>
        <Form
          actions={actions}
          links={links}
          template={template.template}
          variables={variables}
          errors={errors}
        />
        <div className={styles.divider} />
        <Preview iframeKey={iframeKey} html={previewHtml} />
        <Notify ref='notificator'/>
      </div>
    );

  }

}
