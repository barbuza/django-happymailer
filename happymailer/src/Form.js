import React, { Component, PropTypes } from 'react';
import Link from 'valuelink';
import Switch from 'react-ios-switch';
import 'react-ios-switch/build/bundle.css';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import Codemirror from './Codemirror';
import Variables from './Variables';

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

  state = {
    version: window.happymailerConfig.history[0]['value'],
  }

  async setVersion(versionId) {
    const { links, actions } = this.props;
    const result = await actions.loadVersion(versionId);
    const { body, subject, layout } = result.data;

    if (subject) links.subject.set(subject);
    if (layout) links.layout.set(layout);
    if (body) links.body.set(body);

    this.setState({'version': versionId});
    actions.refresh();
  };

  render() {
    const { links, template, actions, variables } = this.props;

    links.subject.check(x => x);
    links.body.check(x => x);

    return (
      <div className={styles.root}>
        <Row label='Name'>
          <div>{template}</div>
        </Row>
        <Row label='Version'>
          <Select value={this.state.version}
                  onChange={value => ::this.setVersion(value.value)}
                  clearable={false}
                  options={window.happymailerConfig.history} />
        </Row>
        <Row label='Enabled'>
          <Switch
            checked={links.enabled.value}
            onChange={checked => links.enabled.set(checked)}
          />
        </Row>
          
        <Row label='Layout'>
          <Select value={links.layout.value}
                  onChange={value => links.layout.set(value.value)}
                  clearable={false}
                  options={window.happymailerConfig.layouts}
          />
        </Row>

        <Row label='Variables'>
          <Variables variables={variables}/>
        </Row>

        <Row label='Subject'>
          <Codemirror singleLine mode='django:inner' valueLink={links.subject}/>
        </Row>

        <Row label='Body'>
          <Codemirror mode='mjml' valueLink={links.body}/>
        </Row>

        <div className='submit-row'>
            <input type="submit" className="default" value="Save"
                   onClick={actions.save}
                   disabled={ links.subject.error || links.body.error } />
            <input type="button" value="Save and continue editing"
                   onClick={() => actions.save(false) }
                   disabled={ links.subject.error || links.body.error } />
            <p className='deletelink-box'>
                <input type="button" value="Preview" onClick={actions.refresh} />
                <input type="button" value="Send Test" onClick={actions.sendTest} />
            </p>
        </div>
      </div>
    );
  }

}
