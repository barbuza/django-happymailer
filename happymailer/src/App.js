import React, { Component, PropTypes } from 'react';
import Link from 'valuelink';
import Form from './Form';
import Preview from './Preview';

export default class App extends Component {

  static propTypes = {
    previewUrl: PropTypes.string.isRequired
  };

  state = {
    template: { ...window.happymailerConfig.template },
    variables: [...window.happymailerConfig.variables]
  };

  render() {
    const { previewUrl } = this.props;
    const { template } = this.state;
    const links = Link.state(this, 'template').pick('layout', 'enabled', 'subject', 'body');
    return (
      <div className={styles.root}>
        <Form
          links={links}
          template={template.template}
          variables={this.state.variables} />
        <div className={styles.divider}/>
        <Preview
          variables={this.state.variables}
          previewUrl={previewUrl}
          template={template}
        />
      </div>
    );

  }

}
