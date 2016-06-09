import React, { Component, PropTypes } from 'react';
import Link from 'valuelink';
import Switch from 'react-ios-switch';
import 'react-ios-switch/build/bundle.css';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import Codemirror from './Codemirror';

const Row = ({ label, children }) => (
  <div className={styles.row}>
    <div className={styles.label}>{label}</div>
    <div className={styles.control}>
      {children}
    </div>
  </div>
);

export default class Form extends Component {

  static propTypes = {
    links: PropTypes.shape({
      enabled: PropTypes.instanceOf(Link).isRequired,
      layout: PropTypes.instanceOf(Link).isRequired,
      subject: PropTypes.instanceOf(Link).isRequired,
      body: PropTypes.instanceOf(Link).isRequired
    }).isRequired
  };

  render() {
    const { links } = this.props;
    return (
      <div className={styles.root}>
        <Row label='Name'>
          <div>dummy</div>
        </Row>
        <Row label='Enabled'>
          <Switch
            checked={links.enabled.value}
            onChange={checked => links.enabled.set(checked)}
          />
        </Row>
        <Row label='Layout'>
          <Select value={links.layout.value}
                  onChange={value => links.layout.set(value)}
                  clearable={false}
                  options={window.happymailerConfig.layouts}
          />
        </Row>
        <Row label='Subject'>
          <Codemirror singleLine mode='django:inner' valueLink={links.subject}/>
        </Row>
        <Row label='Body'>
          <Codemirror mode='mjml' valueLink={links.body}/>
        </Row>
      </div>
    );
  }

}
