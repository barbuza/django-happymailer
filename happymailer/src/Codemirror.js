import React, { Component, PropTypes } from 'react';
import { findDOMNode } from 'react-dom';
import { fromTextArea } from 'codemirror';
import Link from 'valuelink';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/solarized.css';
import 'codemirror/addon/hint/show-hint.css';
import 'codemirror/mode/xml/xml';
import 'codemirror/mode/django/django';
import 'codemirror/addon/hint/xml-hint';
import 'codemirror/addon/hint/show-hint';
import 'codemirror/addon/mode/overlay';
import './mjml';
import styles from './Codemirror.scss';


export default class Codemirror extends Component {

  static propTypes = {
    singleLine: PropTypes.bool,
    mode: PropTypes.oneOf(['django:inner', 'mjml']).isRequired,
    valueLink: PropTypes.instanceOf(Link).isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      value: props.valueLink.value
    };
  }

  componentDidMount() {
    this.cm = fromTextArea(this.refs.textarea, {
      theme: 'solarized',
      lineNumbers: true,
      mode: this.props.mode
    });
    this.cm.setValue(this.props.valueLink.value);
    this.cm.on('change', () => {
      const value = this.cm.getValue();
      this.setState({ value });
      this.props.valueLink.set(value);
    });
    this.cm.on('beforeChange', (instance, change) => {
      if (this.props.singleLine) {
        var newtext = change.text.join('').replace(/\n/g, '');
        change.update(change.from, change.to, [newtext]);
        return true;
      }
    });
  }

  componentWillUnmount() {
    this.cm.toTextArea();
  }

  componentWillReceiveProps(nextProps) {
    const { value } = this.state;
    const { valueLink: { value: nextValue } } = nextProps;
    if (value !== nextValue) {
      this.cm.setValue(nextValue);
    }
  }

  render() {
    return (
      <div className={styles.root}>
        <textarea ref='textarea'/>
      </div>
    );
  }

}
